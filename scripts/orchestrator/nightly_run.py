#!/usr/bin/env python3
"""Run the unattended scrape -> analyze -> score -> vote -> report pipeline.

Every external command is launched by a shell that first activates the local
virtual environment.  Stage checkpoints are written before and after each
attempt, and ``--resume`` restarts at the first stage without a successful
checkpoint.

Ref: codex/tasks/006-orchestrator-scheduler.md
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.agent_runner import (  # noqa: E402
    read_note,
    sanitize_text,
    write_note,
)

try:  # noqa: E402
    from .state import StateStore
except ImportError:  # pragma: no cover - direct script execution
    from state import StateStore  # type: ignore


STAGES = ("scrape", "analyze", "score", "vote", "report")
MAX_TOTAL_TIMEOUT_SECONDS = 2 * 60 * 60
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


class ConfigError(ValueError):
    """Raised when orchestrator configuration is incomplete or unsafe."""


class StageCommandError(RuntimeError):
    """Raised when one external stage command exits unsuccessfully."""


class StageTimeoutError(TimeoutError):
    """Raised when a stage attempt exceeds its configured timeout."""


class TotalRunTimeoutError(TimeoutError):
    """Raised when the two-hour run deadline is exhausted."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_error(value: Any, *, limit: int = 500) -> str:
    cleaned = sanitize_text(value).replace("\n", " ").replace("\r", " ").strip()
    return cleaned[:limit] or value.__class__.__name__


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise ConfigError(f"config.{key} must be a mapping")
    return value


def _positive_number(value: Any, label: str, *, integer: bool = False) -> int | float:
    if isinstance(value, bool):
        raise ConfigError(f"{label} must be a positive number")
    try:
        number = int(value) if integer else float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be a positive number") from exc
    if number <= 0:
        raise ConfigError(f"{label} must be a positive number")
    return number


def _nonnegative_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ConfigError(f"{label} must be zero or a positive number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be zero or a positive number") from exc
    if number < 0:
        raise ConfigError(f"{label} must be zero or a positive number")
    return number


@dataclass(frozen=True)
class OrchestratorConfig:
    """Validated and repository-root-resolved runtime configuration."""

    repo_root: Path
    config_path: Path
    vault_dir: Path
    output_dir: Path
    state_file: Path
    logs_dir: Path
    candidates_dir: Path
    reports_dir: Path
    scraped_json_dir: Path
    venv_activate: Path
    scraper_config: Path
    scraper_script: Path
    transformer_script: Path
    agent_runner_script: Path
    score_script: Path
    vote_script: Path
    report_script: Path
    analysis_agents: tuple[str, ...]
    stage_timeouts: Mapping[str, float]
    total_timeout_seconds: float
    max_attempts: int
    initial_backoff_seconds: float
    backoff_multiplier: float
    cron_schedule: str


def load_config(
    path: Path = DEFAULT_CONFIG_PATH,
    *,
    repo_root: Path = REPO_ROOT,
) -> OrchestratorConfig:
    """Load config.yaml and resolve all relative paths from the repository root."""

    config_path = Path(path).resolve()
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"Unable to read orchestrator config: {config_path}") from exc
    if not isinstance(raw, Mapping):
        raise ConfigError("Orchestrator config must contain a YAML mapping")

    root = Path(repo_root).resolve()
    configured_paths = raw.get("paths", raw)
    if not isinstance(configured_paths, Mapping):
        raise ConfigError("config.paths must be a mapping when present")
    paths = configured_paths
    scripts = _mapping(raw, "scripts")
    timeouts = _mapping(raw, "timeouts")
    retry = _mapping(raw, "retry")

    def resolved(section: Mapping[str, Any], key: str) -> Path:
        value = section.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"Missing configured path: {key}")
        candidate = Path(value).expanduser()
        return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()

    total_timeout = float(
        _positive_number(timeouts.get("total_seconds"), "timeouts.total_seconds")
    )
    if total_timeout > MAX_TOTAL_TIMEOUT_SECONDS:
        raise ConfigError(
            f"timeouts.total_seconds cannot exceed {MAX_TOTAL_TIMEOUT_SECONDS} seconds"
        )
    stage_timeouts: dict[str, float] = {}
    for stage_name in STAGES:
        stage_timeouts[stage_name] = float(
            _positive_number(timeouts.get(stage_name), f"timeouts.{stage_name}")
        )

    max_attempts = int(
        _positive_number(retry.get("max_attempts"), "retry.max_attempts", integer=True)
    )
    if max_attempts > 3:
        raise ConfigError("retry.max_attempts cannot exceed 3")
    agents = raw.get("analysis_agents")
    if not isinstance(agents, list) or not agents or not all(
        isinstance(agent, str) and agent.strip() for agent in agents
    ):
        raise ConfigError("analysis_agents must be a non-empty list of agent names")

    schedule = raw.get("cron_schedule")
    if not isinstance(schedule, str) or not schedule.strip():
        raise ConfigError("cron_schedule must be a non-empty crontab expression")

    return OrchestratorConfig(
        repo_root=root,
        config_path=config_path,
        vault_dir=resolved(paths, "vault_dir"),
        output_dir=resolved(paths, "output_dir"),
        state_file=resolved(paths, "state_file"),
        logs_dir=resolved(paths, "logs_dir"),
        candidates_dir=resolved(paths, "candidates_dir"),
        reports_dir=resolved(paths, "reports_dir"),
        scraped_json_dir=resolved(paths, "scraped_json_dir"),
        venv_activate=resolved(paths, "venv_activate"),
        scraper_config=resolved(paths, "scraper_config"),
        scraper_script=resolved(scripts, "scraper"),
        transformer_script=resolved(scripts, "transformer"),
        agent_runner_script=resolved(scripts, "agent_runner"),
        score_script=resolved(scripts, "score"),
        vote_script=resolved(scripts, "vote"),
        report_script=resolved(scripts, "report"),
        analysis_agents=tuple(agent.strip() for agent in agents),
        stage_timeouts=stage_timeouts,
        total_timeout_seconds=total_timeout,
        max_attempts=max_attempts,
        initial_backoff_seconds=_nonnegative_number(
            retry.get("initial_backoff_seconds"), "retry.initial_backoff_seconds"
        ),
        backoff_multiplier=float(
            _positive_number(retry.get("backoff_multiplier"), "retry.backoff_multiplier")
        ),
        cron_schedule=schedule.strip(),
    )


class CommandRunner:
    """Run commands under the repository virtual environment."""

    def __init__(self, config: OrchestratorConfig) -> None:
        self.config = config

    def shell_command(self, arguments: Sequence[str | Path]) -> str:
        command = " ".join(shlex.quote(str(argument)) for argument in arguments)
        activate = shlex.quote(str(self.config.venv_activate))
        return f"source {activate} && exec {command}"

    def run(
        self,
        arguments: Sequence[str | Path],
        *,
        timeout: float,
    ) -> subprocess.CompletedProcess[str]:
        shell_command = self.shell_command(arguments)
        try:
            completed = subprocess.run(
                ["bash", "-c", shell_command],
                cwd=self.config.repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=max(timeout, 0.001),
            )
        except subprocess.TimeoutExpired as exc:
            raise StageTimeoutError(f"Command timed out after {timeout:.1f} seconds") from exc
        except OSError as exc:
            raise StageCommandError(f"Unable to launch stage command: {_clean_error(exc)}") from exc
        if completed.returncode != 0:
            detail = _clean_error(completed.stderr or completed.stdout or "no command output")
            raise StageCommandError(
                f"Command exited with status {completed.returncode}: {detail}"
            )
        return completed


@dataclass(frozen=True)
class RunResult:
    status: str
    run_id: str
    completed_stages: tuple[str, ...]
    failed_stage: str | None
    state_path: Path
    log_path: Path

    @property
    def ok(self) -> bool:
        return self.status == "completed"


class NightlyOrchestrator:
    """Dependency-ordered, retrying pipeline with checkpoint/resume support."""

    def __init__(
        self,
        config: OrchestratorConfig,
        *,
        stage_handlers: Mapping[str, Callable[[], Any]] | None = None,
        command_runner: CommandRunner | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        timestamp: Callable[[], str] = utc_now,
    ) -> None:
        self.config = config
        defaults: dict[str, Callable[[], Any]] = {
            "scrape": self._stage_scrape,
            "analyze": self._stage_analyze,
            "score": self._stage_score,
            "vote": self._stage_vote,
            "report": self._stage_report,
        }
        if stage_handlers:
            unknown = set(stage_handlers) - set(STAGES)
            if unknown:
                raise ValueError(f"Unknown stage handler(s): {', '.join(sorted(unknown))}")
            defaults.update(stage_handlers)
        self.stage_handlers = defaults
        self.command_runner = command_runner or CommandRunner(config)
        self.monotonic = monotonic
        self.sleep = sleep
        self.timestamp = timestamp
        self.state_store = StateStore(config.state_file)
        self.events: list[str] = []
        self._run_deadline = 0.0
        self._attempt_deadline = 0.0

    def _event(self, message: str) -> None:
        self.events.append(f"{self.timestamp()} — {_clean_error(message, limit=1000)}")

    def _remaining_command_time(self) -> float:
        remaining = min(self._run_deadline, self._attempt_deadline) - self.monotonic()
        if remaining <= 0:
            if self.monotonic() >= self._run_deadline:
                raise TotalRunTimeoutError("Total run timeout reached")
            raise StageTimeoutError("Stage attempt timeout reached")
        return remaining

    def _run_command(self, arguments: Sequence[str | Path]) -> subprocess.CompletedProcess[str]:
        return self.command_runner.run(arguments, timeout=self._remaining_command_time())

    def _candidate_notes(self) -> list[tuple[str, Path]]:
        candidates: dict[str, Path] = {}
        if not self.config.candidates_dir.exists():
            raise StageCommandError(
                f"Candidate directory does not exist: {self.config.candidates_dir}"
            )
        for path in sorted(self.config.candidates_dir.rglob("*.md")):
            try:
                note = read_note(path)
            except (OSError, ValueError, yaml.YAMLError):
                continue
            if note.frontmatter.get("type") != "product_candidate":
                continue
            product_id = str(note.frontmatter.get("product_id", "")).strip()
            if product_id:
                candidates.setdefault(product_id, path)
        if not candidates:
            raise StageCommandError(
                f"No product_candidate notes found below {self.config.candidates_dir}"
            )
        return sorted(candidates.items())

    def _stage_scrape(self) -> None:
        before = set(self.config.scraped_json_dir.glob("shopee_scraped_*.json"))
        self._run_command(
            [
                "python",
                self.config.scraper_script,
                "--config",
                self.config.scraper_config,
            ]
        )
        scraped = list(self.config.scraped_json_dir.glob("shopee_scraped_*.json"))
        new_files = [path for path in scraped if path not in before]
        choices = new_files or scraped
        if not choices:
            raise StageCommandError(
                f"Scraper completed without a JSON output in {self.config.scraped_json_dir}"
            )
        latest = max(choices, key=lambda path: (path.stat().st_mtime_ns, path.name))
        self._run_command(
            [
                "python",
                self.config.transformer_script,
                "--input",
                latest,
                "--output-dir",
                self.config.candidates_dir,
            ]
        )

    def _stage_analyze(self) -> None:
        candidate_ids = [product_id for product_id, _path in self._candidate_notes()]
        for agent_name in self.config.analysis_agents:
            base = [
                "python",
                self.config.agent_runner_script,
                "--agent",
                agent_name,
                "--vault-root",
                self.config.vault_dir,
            ]
            if agent_name == "product_miner":
                self._run_command(base)
                continue
            for product_id in candidate_ids:
                self._run_command([*base, "--product-id", product_id])

    def _persist_score(self, candidate_path: Path, payload: Mapping[str, Any]) -> None:
        note = read_note(candidate_path)
        timestamp = self.timestamp()
        frontmatter = dict(note.frontmatter)
        for field_name in (
            "product_opportunity_score",
            "score_decision",
            "confidence_score",
            "missing_signal_count",
        ):
            if field_name not in payload:
                raise StageCommandError(f"Score output is missing {field_name}")
            frontmatter[field_name] = payload[field_name]
        frontmatter["last_scored_at"] = timestamp
        frontmatter["updated_at"] = timestamp
        frontmatter["status"] = "scored"
        write_note(
            self.config.vault_dir,
            candidate_path,
            frontmatter,
            note.body,
        )

    def _stage_score(self) -> None:
        for _product_id, candidate_path in self._candidate_notes():
            completed = self._run_command(
                ["python", self.config.score_script, candidate_path]
            )
            try:
                payload = json.loads(completed.stdout)
            except (TypeError, json.JSONDecodeError) as exc:
                raise StageCommandError(
                    f"Score command returned invalid JSON for {candidate_path.name}"
                ) from exc
            if not isinstance(payload, Mapping):
                raise StageCommandError(
                    f"Score command returned a non-object for {candidate_path.name}"
                )
            self._persist_score(candidate_path, payload)

    def _stage_vote(self) -> None:
        for product_id, _candidate_path in self._candidate_notes():
            self._run_command(
                [
                    "python",
                    self.config.vote_script,
                    "--vault-root",
                    self.config.vault_dir,
                    "--product-id",
                    product_id,
                ]
            )

    def _stage_report(self) -> None:
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        iso_year, iso_week, _weekday = now.isocalendar()
        report_week = f"{iso_year}-W{iso_week:02d}"
        output_path = self.config.reports_dir / f"weekly-report-{report_week}.md"
        self._run_command(
            [
                "python",
                self.config.report_script,
                "--input-dir",
                self.config.vault_dir,
                "--report-week",
                report_week,
                "--output",
                output_path,
            ]
        )

    def _execute_stage(self, stage_name: str) -> str:
        timeout = self.config.stage_timeouts[stage_name]
        for attempt in range(1, self.config.max_attempts + 1):
            if self.monotonic() >= self._run_deadline:
                error = "Total run timeout reached"
                self.state_store.checkpoint(
                    stage_name,
                    "timed_out",
                    error=error,
                    attempts=attempt,
                    timestamp=self.timestamp(),
                )
                self._event(f"{stage_name} timed out before attempt {attempt}")
                return "timed_out"

            self._attempt_deadline = min(
                self._run_deadline,
                self.monotonic() + timeout,
            )
            self.state_store.checkpoint(
                stage_name,
                "running",
                attempts=attempt,
                timestamp=self.timestamp(),
            )
            self._event(f"{stage_name} attempt {attempt} started")
            try:
                self.stage_handlers[stage_name]()
                if self.monotonic() >= self._run_deadline:
                    raise TotalRunTimeoutError("Total run timeout reached")
                if self.monotonic() > self._attempt_deadline:
                    raise StageTimeoutError(
                        f"Stage attempt exceeded its {timeout:.1f}-second timeout"
                    )
            except TotalRunTimeoutError as exc:
                error = _clean_error(exc)
                self.state_store.checkpoint(
                    stage_name,
                    "timed_out",
                    error=error,
                    attempts=attempt,
                    timestamp=self.timestamp(),
                )
                self._event(f"{stage_name} timed out: {error}")
                return "timed_out"
            except Exception as exc:
                error = _clean_error(exc)
                if self.monotonic() >= self._run_deadline:
                    self.state_store.checkpoint(
                        stage_name,
                        "timed_out",
                        error="Total run timeout reached",
                        attempts=attempt,
                        timestamp=self.timestamp(),
                    )
                    self._event(f"{stage_name} exhausted the total run timeout")
                    return "timed_out"
                final_attempt = attempt == self.config.max_attempts
                checkpoint_status = "failed" if final_attempt else "retrying"
                self.state_store.checkpoint(
                    stage_name,
                    checkpoint_status,
                    error=error,
                    attempts=attempt,
                    timestamp=self.timestamp(),
                )
                self._event(f"{stage_name} attempt {attempt} failed: {error}")
                if final_attempt:
                    return "failed"
                delay = self.config.initial_backoff_seconds * (
                    self.config.backoff_multiplier ** (attempt - 1)
                )
                remaining = self._run_deadline - self.monotonic()
                if delay >= remaining:
                    self.state_store.checkpoint(
                        stage_name,
                        "timed_out",
                        error="Retry backoff would exceed the total run timeout",
                        attempts=attempt,
                        timestamp=self.timestamp(),
                    )
                    self._event(f"{stage_name} retry backoff exhausted the run deadline")
                    return "timed_out"
                if delay:
                    self.sleep(delay)
                continue

            self.state_store.checkpoint(
                stage_name,
                "success",
                attempts=attempt,
                timestamp=self.timestamp(),
            )
            self._event(f"{stage_name} completed on attempt {attempt}")
            return "success"
        raise AssertionError("unreachable stage retry state")

    def _write_run_log(self, *, resumed: bool, status: str) -> Path:
        if self.state_store.state is None:
            raise RuntimeError("Cannot write a run log before state is initialized")
        state = self.state_store.state
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.config.logs_dir / f"{state['run_id']}.md"
        records = {
            record.get("stage_name"): record
            for record in state.get("stages", [])
            if isinstance(record, Mapping)
        }
        completed_count = sum(
            records.get(stage_name, {}).get("status") == "success" for stage_name in STAGES
        )
        failed_stage = next(
            (
                stage_name
                for stage_name in STAGES
                if records.get(stage_name, {}).get("status") in {"failed", "timed_out"}
            ),
            None,
        )
        timestamp = self.timestamp()
        frontmatter = {
            "type": "nightly_run_log",
            "run_id": state["run_id"],
            "pipeline_status": status,
            "resumed": resumed,
            "successful_stage_count": completed_count,
            "failed_stage": failed_stage,
            "started_at": state["started_at"],
            "finished_at": state.get("finished_at"),
            "created_at": state["started_at"],
            "updated_at": timestamp,
            "status": "complete" if status == "completed" else status,
        }
        lines = [
            "# Nightly Orchestrator Run",
            "",
            f"- Run ID: `{state['run_id']}`",
            f"- Pipeline status: **{status}**",
            f"- Resume invocation: {'yes' if resumed else 'no'}",
            "",
            "## Stage checkpoints",
            "",
            "| Stage | Status | Attempts | Timestamp | Error |",
            "| --- | --- | ---: | --- | --- |",
        ]
        for stage_name in STAGES:
            record = records.get(stage_name, {})
            error = _clean_error(record.get("error") or "-").replace("|", "\\|")
            lines.append(
                f"| {stage_name} | {record.get('status', 'not_run')} | "
                f"{record.get('attempts', 0)} | {record.get('timestamp', '-')} | {error} |"
            )
        lines.extend(("", "## Events", ""))
        lines.extend(f"- {event}" for event in self.events)
        if not self.events:
            lines.append("- No stage work was required.")
        markdown = (
            "---\n"
            + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
            + "\n---\n\n"
            + "\n".join(lines).rstrip()
            + "\n"
        )
        temporary = log_path.with_name(f".{log_path.name}.tmp")
        temporary.write_text(markdown, encoding="utf-8")
        temporary.replace(log_path)
        return log_path

    def run(self, *, resume: bool = False) -> RunResult:
        """Execute or resume the pipeline without leaking stage exceptions."""

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        was_resumed = resume and self.config.state_file.exists()
        state = self.state_store.start(resume=resume, timestamp=self.timestamp())
        start_index = self.state_store.next_stage_index(STAGES) if resume else 0
        self._run_deadline = self.monotonic() + self.config.total_timeout_seconds
        status = "completed"
        failed_stage: str | None = None

        if was_resumed:
            if start_index < len(STAGES):
                self._event(f"resume selected stage {STAGES[start_index]}")
            else:
                self._event("resume found every stage already completed")

        for stage_name in STAGES[start_index:]:
            stage_status = self._execute_stage(stage_name)
            if stage_status != "success":
                status = stage_status
                failed_stage = stage_name
                break

        self.state_store.finish(status, timestamp=self.timestamp())
        log_path = self._write_run_log(resumed=was_resumed, status=status)
        records = {
            record.get("stage_name"): record
            for record in self.state_store.state.get("stages", [])  # type: ignore[union-attr]
            if isinstance(record, Mapping)
        }
        completed = tuple(
            stage_name
            for stage_name in STAGES
            if records.get(stage_name, {}).get("status") == "success"
        )
        return RunResult(
            status=status,
            run_id=str(state["run_id"]),
            completed_stages=completed,
            failed_stage=failed_stage,
            state_path=self.config.state_file,
            log_path=log_path,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the nightly affiliate intelligence pipeline.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume at the first stage without a successful checkpoint.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        result = NightlyOrchestrator(config).run(resume=args.resume)
    except Exception as exc:
        print(f"[ERROR] {_clean_error(exc)}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": result.status,
                "run_id": result.run_id,
                "completed_stages": list(result.completed_stages),
                "failed_stage": result.failed_stage,
                "state_path": str(result.state_path),
                "log_path": str(result.log_path),
            }
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
