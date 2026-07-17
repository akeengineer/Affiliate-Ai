"""Phase 3 nightly orchestrator tests with every pipeline stage mocked.

Ref: codex/tasks/006-orchestrator-scheduler.md
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.orchestrator.nightly_run import (
    STAGES,
    CommandRunner,
    NightlyOrchestrator,
    load_config,
)
from scripts.orchestrator.state import StateStore, load_state, write_checkpoint


DEFAULT_CONFIG = REPO_ROOT / "scripts" / "orchestrator" / "config.yaml"
TIMESTAMP = "2026-07-16T02:00:00Z"


def orchestrator_config(tmp_path: Path, **changes: object):
    base = load_config(DEFAULT_CONFIG)
    output_dir = tmp_path / "output"
    values: dict[str, object] = {
        "scrape_source": "direct",
        "vault_dir": tmp_path / "vault",
        "output_dir": output_dir,
        "state_file": output_dir / "state.json",
        "logs_dir": tmp_path / "vault" / "logs",
        "candidates_dir": tmp_path / "vault" / "candidates",
        "reports_dir": tmp_path / "vault" / "reports",
        "scraped_json_dir": tmp_path / "scraped",
        "stage_timeouts": {stage: 30.0 for stage in STAGES},
        "total_timeout_seconds": 120.0,
        "max_attempts": 3,
        "initial_backoff_seconds": 0.0,
        "backoff_multiplier": 2.0,
    }
    values.update(changes)
    return replace(base, **values)


def handlers_that_record(calls: list[str]) -> dict[str, Callable[[], None]]:
    return {
        stage: (lambda stage_name=stage: calls.append(stage_name))
        for stage in STAGES
    }


def test_nightly_run_full_pipeline(tmp_path: Path) -> None:
    calls: list[str] = []
    config = orchestrator_config(tmp_path)
    runner = NightlyOrchestrator(
        config,
        stage_handlers=handlers_that_record(calls),
        timestamp=lambda: TIMESTAMP,
    )

    result = runner.run()

    assert result.ok
    assert result.status == "completed"
    assert calls == list(STAGES)
    assert result.completed_stages == STAGES
    state = load_state(config.state_file)
    assert state["run_status"] == "completed"
    assert [record["stage_name"] for record in state["stages"]] == list(STAGES)
    assert all(record["status"] == "success" for record in state["stages"])


def test_state_checkpoint_write(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "nightly.json"

    state = write_checkpoint(
        state_path,
        "scrape",
        "success",
        attempts=2,
        timestamp=TIMESTAMP,
    )

    assert state_path.exists()
    assert state["stage_name"] == "scrape"
    assert state["status"] == "success"
    assert state["timestamp"] == TIMESTAMP
    assert state["error"] is None
    assert state["stages"] == [
        {
            "stage_name": "scrape",
            "status": "success",
            "timestamp": TIMESTAMP,
            "error": None,
            "attempts": 2,
        }
    ]


def test_state_resume_from_checkpoint(tmp_path: Path) -> None:
    config = orchestrator_config(tmp_path)
    store = StateStore(config.state_file)
    original = store.start(timestamp=TIMESTAMP)
    store.checkpoint("scrape", "success", timestamp=TIMESTAMP)
    store.checkpoint("analyze", "success", timestamp=TIMESTAMP)
    calls: list[str] = []

    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers_that_record(calls),
        timestamp=lambda: TIMESTAMP,
    ).run(resume=True)

    assert result.ok
    assert result.run_id == original["run_id"]
    assert calls == ["score", "vote", "report"]
    assert result.completed_stages == STAGES


def test_stage_error_handling(tmp_path: Path) -> None:
    config = orchestrator_config(tmp_path)
    calls: list[str] = []

    def fail_scrape() -> None:
        calls.append("scrape")
        raise RuntimeError("scraper unavailable")

    handlers = handlers_that_record(calls)
    handlers["scrape"] = fail_scrape
    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers,
        timestamp=lambda: TIMESTAMP,
    ).run()

    assert result.status == "failed"
    assert result.failed_stage == "scrape"
    assert calls == ["scrape", "scrape", "scrape"]
    state = load_state(config.state_file)
    assert state["stages"][0]["status"] == "failed"
    assert state["stages"][0]["error"] == "scraper unavailable"
    assert result.log_path.exists()


def test_retry_logic(tmp_path: Path) -> None:
    attempts = 0
    calls: list[str] = []
    sleeps: list[float] = []
    config = orchestrator_config(
        tmp_path,
        initial_backoff_seconds=1.0,
        backoff_multiplier=2.0,
    )

    def flaky_scrape() -> None:
        nonlocal attempts
        attempts += 1
        calls.append("scrape")
        if attempts < 3:
            raise RuntimeError("temporary failure")

    handlers = handlers_that_record(calls)
    handlers["scrape"] = flaky_scrape
    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers,
        sleep=sleeps.append,
        timestamp=lambda: TIMESTAMP,
    ).run()

    assert result.ok
    assert attempts == 3
    assert sleeps == [1.0, 2.0]
    scrape = load_state(config.state_file)["stages"][0]
    assert scrape["status"] == "success"
    assert scrape["attempts"] == 3


def test_timeout_enforcement(tmp_path: Path) -> None:
    clock = [0.0]
    config = orchestrator_config(
        tmp_path,
        total_timeout_seconds=5.0,
        stage_timeouts={stage: 30.0 for stage in STAGES},
    )
    calls: list[str] = []

    def exceed_deadline() -> None:
        calls.append("scrape")
        clock[0] = 6.0

    handlers = handlers_that_record(calls)
    handlers["scrape"] = exceed_deadline
    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers,
        monotonic=lambda: clock[0],
        timestamp=lambda: TIMESTAMP,
    ).run()

    assert result.status == "timed_out"
    assert result.failed_stage == "scrape"
    assert calls == ["scrape"]
    state = load_state(config.state_file)
    assert state["run_status"] == "timed_out"
    assert state["stages"][0]["status"] == "timed_out"
    assert config.total_timeout_seconds <= 2 * 60 * 60


def test_run_log_output(tmp_path: Path) -> None:
    config = orchestrator_config(tmp_path)
    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers_that_record([]),
        timestamp=lambda: TIMESTAMP,
    ).run()

    log = result.log_path.read_text(encoding="utf-8")
    assert result.log_path.parent == config.logs_dir
    assert "type: nightly_run_log" in log
    assert "pipeline_status: completed" in log
    assert "| scrape | success | 1 |" in log
    assert "| report | success | 1 |" in log
    assert f"run_id: {result.run_id}" in log


def test_commands_source_virtual_environment(tmp_path: Path) -> None:
    config = orchestrator_config(tmp_path)
    command = CommandRunner(config).shell_command(
        ["python", config.agent_runner_script, "--agent", "product_miner"]
    )

    assert command.startswith(f"source {config.venv_activate}")
    assert "scripts/agents/agent_runner.py" in command
    assert "--agent product_miner" in command


def test_default_config_has_required_limits() -> None:
    config = load_config(DEFAULT_CONFIG)

    assert config.cron_schedule == "0 2 * * *"
    assert config.scrape_source == "local_sync"
    assert config.max_attempts == 3
    assert config.total_timeout_seconds == 7200
    assert tuple(config.stage_timeouts) == STAGES
    assert config.vault_dir == REPO_ROOT / "vault"
    assert config.output_dir == REPO_ROOT / ".cache" / "orchestrator"


def test_local_sync_skips_scrape_stage(tmp_path: Path) -> None:
    calls: list[str] = []
    config = orchestrator_config(tmp_path, scrape_source="local_sync")

    result = NightlyOrchestrator(
        config,
        stage_handlers=handlers_that_record(calls),
        timestamp=lambda: TIMESTAMP,
    ).run()

    assert result.ok
    assert calls == list(STAGES[1:])
    assert result.completed_stages == STAGES[1:]
    assert "| scrape | skipped_local_sync | 0 |" in result.log_path.read_text(
        encoding="utf-8"
    )


def test_cron_setup_installs_daily_0200_job() -> None:
    cron_setup = REPO_ROOT / "scripts" / "orchestrator" / "cron_setup.sh"
    text = cron_setup.read_text(encoding="utf-8")

    assert cron_setup.stat().st_mode & 0o111
    assert 'CRON_SCHEDULE" != "0 2 * * *"' in text
    assert "crontab \"$TEMP_CRONTAB\"" in text
    assert "source $ACTIVATE_QUOTED" in text
    assert "/home/ubuntu/Affiliate-Ai" not in text
