from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_task_003_runtime_artifacts_exist() -> None:
    assert (REPO_ROOT / "codex/tasks/003-operational-ai-agents-runtime.md").is_file()
    assert (REPO_ROOT / "docs/plans/operational-ai-agents.md").is_file()
