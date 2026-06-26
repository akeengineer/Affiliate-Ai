from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts/dev/check_hermes_runtime.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/005-phase2b-hermes-operational-test.md"
PROMPT_FILE = REPO_ROOT / "prompts/workflows/hermes-phase2b-operational-test.md"


def _write_sudo_stub(bin_dir: Path, skills_output: str) -> None:
    stub_path = bin_dir / "sudo"
    stub_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [ \"$#\" -ge 3 ] && [ \"$1\" = \"hermes\" ] && [ \"$2\" = \"skills\" ] && [ \"$3\" = \"list\" ]; then\n"
        "  cat <<'EOF'\n"
        f"{skills_output}\n"
        "EOF\n"
        "  exit 0\n"
        "fi\n"
        "printf 'unexpected sudo invocation: %s\\n' \"$*\" >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    stub_path.chmod(0o755)


def test_phase2b_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMPT_FILE.is_file()
    assert CHECK_SCRIPT.is_file()
    assert os.access(CHECK_SCRIPT, os.X_OK)


def test_check_hermes_runtime_passes_with_required_skills(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_stub(
        bin_dir,
        "\n".join(
            [
                "affiliate-growth-os enabled",
                "obsidian enabled",
                "codex enabled",
            ]
        ),
    )

    completed = subprocess.run(
        ["bash", str(CHECK_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "ENABLE_AUTOPUBLISH": "false",
        },
    )

    assert completed.returncode == 0, completed.stderr
    assert "phase2b_runtime_check: success" in completed.stdout


def test_check_hermes_runtime_fails_when_skill_missing(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_stub(
        bin_dir,
        "\n".join(
            [
                "affiliate-growth-os enabled",
                "obsidian enabled",
            ]
        ),
    )

    completed = subprocess.run(
        ["bash", str(CHECK_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "ENABLE_AUTOPUBLISH": "false",
        },
    )

    assert completed.returncode != 0
    assert "Missing Hermes skill: codex" in completed.stderr


def test_check_hermes_runtime_fails_when_autopublish_true(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_stub(
        bin_dir,
        "\n".join(
            [
                "affiliate-growth-os enabled",
                "obsidian enabled",
                "codex enabled",
            ]
        ),
    )

    completed = subprocess.run(
        ["bash", str(CHECK_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "ENABLE_AUTOPUBLISH": "true",
        },
    )

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH must not be true" in completed.stderr
