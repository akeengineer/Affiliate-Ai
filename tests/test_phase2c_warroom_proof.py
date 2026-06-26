from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = REPO_ROOT / "scripts/dev/run_phase2c_warroom_proof.sh"
CHECK_SCRIPT = REPO_ROOT / "scripts/dev/check_phase2c_warroom_outputs.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/006-phase2c-warroom-proof.md"
PROMPT_FILE = REPO_ROOT / "prompts/workflows/phase2c-warroom-proof.md"
OUTPUT_ROOT = REPO_ROOT / "tmp/phase2c-warroom"
PROOF_SESSION = "affiliate-warroom-phase2c"
NORMAL_SESSION = "affiliate-warroom"


def _tmux_env(bin_dir: Path) -> dict[str, str]:
    return {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}


def _write_tmux_stub(bin_dir: Path) -> None:
    state_dir = bin_dir / "tmux-state"
    state_dir.mkdir()
    sessions_file = state_dir / "sessions.txt"
    sessions_file.write_text("", encoding="utf-8")

    stub_path = bin_dir / "tmux"
    stub_path.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail

sessions_file={sessions_file!s}
touch "$sessions_file"

cmd="${{1:-}}"
shift || true

session_name() {{
  local value=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      -s|-t)
        value="${{2:-}}"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  printf '%s\\n' "$value"
}}

case "$cmd" in
  has-session)
    name="$(session_name "$@")"
    grep -Fxq "$name" "$sessions_file"
    ;;
  kill-session)
    name="$(session_name "$@")"
    grep -Fxv "$name" "$sessions_file" > "$sessions_file.tmp" || true
    mv "$sessions_file.tmp" "$sessions_file"
    ;;
  new-session)
    name="$(session_name "$@")"
    if ! grep -Fxq "$name" "$sessions_file"; then
      printf '%s\\n' "$name" >> "$sessions_file"
    fi
    ;;
  attach-session|set-environment|split-window|new-window|send-keys|select-layout|select-window)
    ;;
  -V)
    echo "tmux 3.6"
    ;;
  *)
    echo "unexpected tmux invocation: $cmd $*" >&2
    exit 1
    ;;
esac
""",
        encoding="utf-8",
    )
    stub_path.chmod(0o755)


def _kill_session(name: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(
        ["tmux", "kill-session", "-t", name],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _tmux_has_session(name: str, env: dict[str, str] | None = None) -> bool:
    completed = subprocess.run(
        ["tmux", "has-session", "-t", name],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return completed.returncode == 0


def _frontmatter(text: str) -> str:
    assert text.startswith("---\n")
    _, frontmatter, _ = text.split("---\n", 2)
    return frontmatter


def test_phase2c_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMPT_FILE.is_file()
    assert RUN_SCRIPT.is_file()
    assert CHECK_SCRIPT.is_file()
    assert os.access(RUN_SCRIPT, os.X_OK)
    assert os.access(CHECK_SCRIPT, os.X_OK)


def test_run_phase2c_warroom_proof_creates_outputs() -> None:
    bin_dir = OUTPUT_ROOT.parent / "phase2c-test-bin"
    shutil.rmtree(bin_dir, ignore_errors=True)
    bin_dir.mkdir(parents=True)
    _write_tmux_stub(bin_dir)
    env = _tmux_env(bin_dir)

    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)
    _kill_session(PROOF_SESSION, env)
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", NORMAL_SESSION],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    completed = subprocess.run(
        ["bash", str(RUN_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**env, "ENABLE_AUTOPUBLISH": "false"},
        check=False,
    )

    try:
        assert completed.returncode == 0, completed.stderr
        assert "tmux attach -t affiliate-warroom-phase2c" in completed.stdout
        assert _tmux_has_session(PROOF_SESSION, env)
        assert _tmux_has_session(NORMAL_SESSION, env)

        vote_paths = sorted((OUTPUT_ROOT / "votes").glob("vote-*.md"))
        decision_paths = sorted((OUTPUT_ROOT / "decisions").glob("decision-*.md"))

        assert len(vote_paths) == 5
        assert len(decision_paths) == 1

        for vote_path in vote_paths:
            text = vote_path.read_text(encoding="utf-8")
            frontmatter = _frontmatter(text)
            assert "type: agent_vote" in frontmatter
            assert "product_id: prod-smart-desk-pad" in frontmatter
            assert "# Agent Vote" in text
            assert "## Inputs Read" in text
            assert "## Findings" in text
            assert "## Rationale" in text
            assert "## Required Actions" in text

        decision_text = decision_paths[0].read_text(encoding="utf-8")
        decision_frontmatter = _frontmatter(decision_text)
        assert "type: decision" in decision_frontmatter
        assert "vote_count: 5" in decision_frontmatter
        assert "# Decision" in decision_text
        assert "## Score Summary" in decision_text
        assert "## Votes" in decision_text
        assert "## Decision" in decision_text
        assert "## Required Actions" in decision_text
    finally:
        _kill_session(PROOF_SESSION, env)
        _kill_session(NORMAL_SESSION, env)
        shutil.rmtree(bin_dir, ignore_errors=True)


def test_run_phase2c_warroom_proof_fails_when_autopublish_enabled() -> None:
    completed = subprocess.run(
        ["bash", str(RUN_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "ENABLE_AUTOPUBLISH": "true"},
        check=False,
    )

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH must not be true" in completed.stderr


def test_phase2c_checker_passes_after_proof_run() -> None:
    bin_dir = OUTPUT_ROOT.parent / "phase2c-test-bin"
    shutil.rmtree(bin_dir, ignore_errors=True)
    bin_dir.mkdir(parents=True)
    _write_tmux_stub(bin_dir)
    env = _tmux_env(bin_dir)

    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)
    _kill_session(PROOF_SESSION, env)

    try:
        run_completed = subprocess.run(
            ["bash", str(RUN_SCRIPT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**env, "ENABLE_AUTOPUBLISH": "false"},
            check=False,
        )
        assert run_completed.returncode == 0, run_completed.stderr

        check_completed = subprocess.run(
            ["bash", str(CHECK_SCRIPT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert check_completed.returncode == 0, check_completed.stderr
        assert "phase2c_warroom_proof: success" in check_completed.stdout
    finally:
        _kill_session(PROOF_SESSION, env)
        shutil.rmtree(bin_dir, ignore_errors=True)
