from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/python-tests.yml"
CHECK = REPO_ROOT / "scripts/dev/check_hermes_runtime.sh"
WARROOM = REPO_ROOT / "scripts/tmux/start-affiliate-warroom.sh"

TASK_FILE = REPO_ROOT / "codex/tasks/028-ci-c-runner-regression-guards.md"
PLAN = REPO_ROOT / "docs/CI_RUNNER_COMPATIBILITY_PLAN.md"

# This guard-definition file names skip selectors and the operator path as data;
# it must be excluded from scans that would otherwise treat those literals as
# real usage.
SELF = Path(__file__).name

DERIVE_SCRIPT_DIR = 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
DERIVE_REPO_ROOT = 'REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"'


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 4. workflow cache guard ───────────────────────────────────────────────────

def test_workflow_has_no_unsupported_pip_cache() -> None:
    assert WORKFLOW.is_file()
    text = _text(WORKFLOW)
    has_dep_file = (REPO_ROOT / "requirements.txt").exists() or (
        REPO_ROOT / "pyproject.toml"
    ).exists()
    if not has_dep_file:
        assert not re.search(r"cache:\s*[\"']?pip[\"']?", text), (
            "setup-python pip cache must not return without a dependency lockfile"
        )
    assert "python -m pytest" in text


# ── 5. hardcoded operator path guard (executable scripts only) ────────────────

def test_no_hardcoded_operator_path_in_scripts() -> None:
    script_files = sorted((REPO_ROOT / "scripts").rglob("*.sh")) + sorted(
        (REPO_ROOT / "scripts").rglob("*.py")
    )
    assert script_files, "expected scripts to scan"
    for path in script_files:
        assert "/home/ubuntu/Affiliate-Ai" not in _text(path), (
            f"hardcoded operator path in executable script: "
            f"{path.relative_to(REPO_ROOT)}"
        )


# ── 6. operator-runtime gate guard ────────────────────────────────────────────

def test_operator_runtime_gate_is_ci_safe_by_default() -> None:
    text = _text(CHECK)
    assert "AFFILIATE_REQUIRE_OPERATOR_RUNTIME" in text
    assert "AFFILIATE_REQUIRE_OPERATOR_RUNTIME:-false" in text
    assert "phase2b_runtime_check: ci-static" in text
    assert "sudo hermes" in text

    ci_index = text.index("phase2b_runtime_check: ci-static")
    sudo_index = text.index("sudo hermes")
    assert ci_index < sudo_index, "sudo hermes must come after the CI-static exit"
    assert "exit 0" in text[ci_index:sudo_index], (
        "CI mode must return before reaching sudo/Hermes"
    )


# ── 7. repo-root derivation guard ─────────────────────────────────────────────

def test_scripts_derive_repo_root_from_location() -> None:
    for path in (CHECK, WARROOM):
        text = _text(path)
        assert DERIVE_SCRIPT_DIR in text, f"{path.name} must derive SCRIPT_DIR"
        assert DERIVE_REPO_ROOT in text, f"{path.name} must derive REPO_ROOT"


def test_warroom_project_dir_default_is_portable() -> None:
    # The ${PROJECT_DIR:-$REPO_ROOT} form proves both the derived default and a
    # preserved environment override.
    assert 'PROJECT_DIR="${PROJECT_DIR:-$REPO_ROOT}"' in _text(WARROOM)


# ── 8. no broad skip guard ────────────────────────────────────────────────────

BANNED_SELECTORS = [
    "not phase2b",
    "not phase2c",
    "not ci_",
    "not runner",
    "not phase2 ",
]


def test_no_broad_skip_hides_runner_compatibility_tests() -> None:
    scan_paths = [
        p for p in (REPO_ROOT / "tests").glob("*.py") if p.name != SELF
    ] + [WORKFLOW]
    for path in scan_paths:
        text = _text(path)
        for selector in BANNED_SELECTORS:
            assert selector not in text, (
                f"broad skip hiding runner-compat coverage in "
                f"{path.relative_to(REPO_ROOT)}: {selector}"
            )


def test_phase1_smoke_self_recursion_guard_is_confined() -> None:
    for path in (REPO_ROOT / "tests").glob("*.py"):
        if path.name == SELF:
            continue
        if "not phase1_smoke" in _text(path):
            assert path.name == "test_phase1_smoke.py"


def test_workflow_runs_full_suite_without_exclusions() -> None:
    text = _text(WORKFLOW)
    # Forbid pytest keyword/marker exclusions and path ignores. Match the
    # selector against pytest specifically so the `-m` in `python -m pytest`
    # (the module-run flag, not a marker filter) is not flagged.
    assert "pytest -k" not in text
    assert "pytest -m" not in text
    assert "--ignore" not in text


# ── 9. no network guard (CI-B scripts only) ───────────────────────────────────

NETWORK_PATTERNS = [
    r"\bcurl\b",
    r"\bwget\b",
    r"\bnc\b",
    r"\bnetcat\b",
    r"https?://",
]


def test_ci_b_scripts_make_no_network_calls() -> None:
    for path in (CHECK, WARROOM):
        text = _text(path)
        for pattern in NETWORK_PATTERNS:
            assert not re.search(pattern, text), (
                f"network token {pattern!r} in {path.name}"
            )


# ── 10. operator-mode preservation guard ──────────────────────────────────────

def test_operator_mode_still_requires_hermes_skills() -> None:
    text = _text(CHECK)
    assert "sudo hermes skills list" in text
    for skill in ["affiliate-growth-os", "obsidian", "codex"]:
        assert skill in text, f"operator mode must still require skill: {skill}"


# ── 11. CI-C docs/task contract ───────────────────────────────────────────────

def test_task_contract_exists_with_final_status() -> None:
    assert TASK_FILE.is_file()
    assert "ci_c_status: success" in _text(TASK_FILE)


def test_plan_doc_has_ci_c_guard_policy() -> None:
    text = _text(PLAN)
    assert "CI-C guard policy" in text
    for token in [
        "AFFILIATE_REQUIRE_OPERATOR_RUNTIME",
        "cache",
        "phase1_smoke",
        "scripts/",
        "no runtime behavior",
    ]:
        assert token in text, f"CI-C guard policy missing: {token}"
