from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts/dev/check_hermes_runtime.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/005-phase2b-hermes-operational-test.md"
PROMPT_FILE = REPO_ROOT / "prompts/workflows/hermes-phase2b-operational-test.md"

VALID_REMOTE = "git@github.com:akeengineer/Affiliate-Ai.git"


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


def _write_sudo_tripwire(bin_dir: Path) -> Path:
    """A sudo stub that records invocation and fails; proves sudo is not used."""
    sentinel = bin_dir / "sudo-was-called"
    stub_path = bin_dir / "sudo"
    stub_path.write_text(
        "#!/usr/bin/env bash\n"
        f"touch {sentinel!s}\n"
        "echo 'sudo must not be called in CI mode' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    stub_path.chmod(0o755)
    return sentinel


def _write_git_stub(bin_dir: Path, remote_url: str) -> None:
    """A git stub so operator-mode tests do not depend on the real remote."""
    stub_path = bin_dir / "git"
    stub_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [ \"$#\" -ge 3 ] && [ \"$1\" = \"remote\" ] && [ \"$2\" = \"get-url\" ] && [ \"$3\" = \"origin\" ]; then\n"
        f"  printf '%s\\n' '{remote_url}'\n"
        "  exit 0\n"
        "fi\n"
        "exec /usr/bin/git \"$@\"\n",
        encoding="utf-8",
    )
    stub_path.chmod(0o755)


def _env(bin_dir: Path, **overrides: str) -> dict[str, str]:
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "ENABLE_AUTOPUBLISH": "false",
    }
    env.update(overrides)
    return env


def _run(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CHECK_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


# ── 1. artifacts exist ────────────────────────────────────────────────────────

def test_phase2b_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMPT_FILE.is_file()
    assert CHECK_SCRIPT.is_file()
    assert os.access(CHECK_SCRIPT, os.X_OK)


# ── 2. CI/default mode passes without calling sudo ────────────────────────────

def test_check_hermes_runtime_ci_mode_static_pass(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    sentinel = _write_sudo_tripwire(bin_dir)

    env = _env(bin_dir)
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)

    completed = _run(env)

    assert completed.returncode == 0, completed.stderr
    assert "phase2b_runtime_check: ci-static" in completed.stdout
    assert not sentinel.exists(), "sudo must not be called in CI mode"


# ── 3. operator mode passes with required skills ──────────────────────────────

def test_check_hermes_runtime_operator_mode_pass(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_stub(
        bin_dir,
        "\n".join(["affiliate-growth-os enabled", "obsidian enabled", "codex enabled"]),
    )
    _write_git_stub(bin_dir, VALID_REMOTE)

    completed = _run(_env(bin_dir, AFFILIATE_REQUIRE_OPERATOR_RUNTIME="true"))

    assert completed.returncode == 0, completed.stderr
    assert "phase2b_runtime_check: success" in completed.stdout


# ── 4. operator mode fails when a required skill is missing ───────────────────

def test_check_hermes_runtime_operator_mode_missing_skill(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_stub(
        bin_dir,
        "\n".join(["affiliate-growth-os enabled", "obsidian enabled"]),
    )
    _write_git_stub(bin_dir, VALID_REMOTE)

    completed = _run(_env(bin_dir, AFFILIATE_REQUIRE_OPERATOR_RUNTIME="true"))

    assert completed.returncode != 0
    assert "Missing Hermes skill: codex" in completed.stderr


# ── 5. autopublish guard fails in CI mode too ─────────────────────────────────

def test_check_hermes_runtime_autopublish_guard_in_ci_mode(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_sudo_tripwire(bin_dir)

    env = _env(bin_dir, ENABLE_AUTOPUBLISH="true")
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)

    completed = _run(env)

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH must not be true" in completed.stderr
