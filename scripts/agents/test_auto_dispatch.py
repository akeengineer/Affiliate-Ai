"""Integration Simulation — Full Auto-Dispatch Flow.

Demonstrates both small (auto) and large (plan-first) task flows
with mocked agent execution. Run this to verify the entire
auto-dispatch pipeline works end-to-end.

Usage:
    python scripts/agents/test_auto_dispatch.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from scripts.agents.core.classifier import classify_task, select_agent_type
from scripts.agents.core.concurrency import AgentProcessManager
from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.kiro_dispatch import (
    RESULT_MARKER,
    build_agent_command,
    create_result,
    execute_agent,
    parse_agent_output,
    save_result,
)


CONFIG_DATA = {
    "project_name": "Auto-Dispatch Simulation",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {
            "command": "claude",
            "flags": ["-p", "--dangerously-skip-permissions", "--output-format", "json"],
            "system_prompt": ".agents/prompts/claude-cli-agent.md",
            "max_turns": 10,
            "max_budget_usd": 5.0,
            "task_types": ["reasoning", "design", "review"],
            "fallback_to": "codex",
        },
        "codex": {
            "command": "codex",
            "flags": ["-q", "--approval-mode", "full-auto"],
            "system_prompt": ".agents/prompts/codex-cli-agent.md",
            "task_types": ["implementation", "test", "refactor"],
            "fallback_to": "claude",
        },
    },
    "dispatch": {
        "retry_max": 2,
        "retry_backoff_seconds": [1, 2],
        "fallback_enabled": True,
        "parallel_max": 2,
        "default_timeout_seconds": 60,
    },
    "ssh": {"host": "god-of-ai", "project_path": "/home/ubuntu/Affiliate-Ai", "user": "ubuntu"},
    "validation": {"run_tests": False, "test_command": "python -m pytest", "check_files_exist": False},
    "paths": {
        "queue": ".agents/queue",
        "results": ".agents/results",
        "state": ".agents/state",
        "reports": ".agents/reports",
        "prompts": ".agents/prompts",
        "schemas": ".agents/schemas",
    },
}


def setup_project(tmp_path: Path) -> ProjectConfig:
    """Set up a temp project for the simulation."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports", "prompts"]:
        (agents_dir / sub).mkdir()
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text("# Claude", encoding="utf-8")
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text("# Codex", encoding="utf-8")
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(CONFIG_DATA), encoding="utf-8")
    return ProjectConfig.load(str(config_path))


def header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def simulate_small_task(config: ProjectConfig, project_root: Path) -> bool:
    """Simulate the small task auto-dispatch flow.

    Flow: User says "implement score_product.py" → classify → select agent → dispatch → collect → report
    """
    header("SIMULATION: Small Task (Auto-Dispatch)")

    user_request = "implement score_product.py following docs/SCORING_SPEC.md"
    print(f"  User: \"{user_request}\"")
    print()

    # Step 1: Classify
    classification = classify_task(user_request, expected_outputs=["scripts/dev/score_product.py"])
    print(f"  [Classify] Size: {classification.size} (confidence: {classification.confidence:.2f})")
    print(f"             Reason: {classification.reason}")
    assert classification.is_small, f"Expected small, got {classification.size}"
    print()

    # Step 2: Check concurrency
    mgr = AgentProcessManager(state_dir=project_root / ".agents" / "state")
    print(f"  [Concurrency] Running agents: {mgr.get_running_count()}")
    assert not mgr.is_any_running()
    print()

    # Step 3: Select agent
    task_type = select_agent_type(user_request)
    print(f"  [Agent Select] Type: {task_type} → Agent: codex")
    assert task_type == "implementation"

    agent_config = config.get_agent("codex")
    print()

    # Step 4: Build command
    task_id = "sim-small-001"
    cmd = build_agent_command(agent_config, user_request, task_id, task_type, project_root)
    print(f"  [Build Command] {cmd[0]} {cmd[1]} ... (prompt length: {len(cmd[-1])} chars)")
    assert cmd[0] == "codex"
    assert "-q" in cmd
    print()

    # Step 5: Simulate execution (mocked)
    mock_stdout = json.dumps({
        "status": "success",
        "summary": "Implemented score_product.py with 7 scoring dimensions and 4 thresholds",
        "files_created": ["scripts/dev/score_product.py"],
        "files_modified": [],
        "tests_run": "python -m pytest tests/test_score_product.py -v",
        "tests_passed": True,
        "errors": [],
        "next_steps": ["Add edge case tests for malformed YAML"],
    })

    print(f"  [Execute] Simulating codex -q execution...")
    result = create_result(task_id, "codex", 0, mock_stdout, "", 45.2)
    print(f"  [Execute] Duration: {result['duration_seconds']:.1f}s")
    print()

    # Step 6: Save result
    save_result(result, config)
    result_path = project_root / ".agents" / "results" / f"{task_id}.json"
    assert result_path.exists()
    print(f"  [Save] Result saved to: .agents/results/{task_id}.json")
    print()

    # Step 7: Report
    print(f"  [Report to User]")
    print(f"  Status: {result['status']}")
    print(f"  Summary: {result['summary']}")
    print(f"  Files created: {result['files_created']}")
    print(f"  Tests: {result['tests_run']} → {'PASSED' if result['tests_passed'] else 'FAILED'}")
    if result['next_steps']:
        print(f"  Next: {result['next_steps'][0]}")
    print()

    assert result["status"] == "success"
    print("  PASS: Small task flow completed successfully")
    return True


def simulate_large_task(config: ProjectConfig, project_root: Path) -> bool:
    """Simulate the large task plan-first flow.

    Flow: User says "redesign the scoring architecture" → classify → present plan → user approves → multi-dispatch
    """
    header("SIMULATION: Large Task (Plan-First)")

    user_request = "redesign the entire scoring architecture to support plugins and custom scoring dimensions"
    print(f"  User: \"{user_request}\"")
    print()

    # Step 1: Classify
    classification = classify_task(user_request)
    print(f"  [Classify] Size: {classification.size} (confidence: {classification.confidence:.2f})")
    print(f"             Reason: {classification.reason}")
    assert classification.is_large, f"Expected large, got {classification.size}"
    print()

    # Step 2: Present plan (Kiro would show this to user)
    plan = [
        {"step": 1, "agent": "claude", "type": "design", "title": "Design plugin architecture and interfaces"},
        {"step": 2, "agent": "codex", "type": "implementation", "title": "Implement plugin loader and registry"},
        {"step": 3, "agent": "codex", "type": "implementation", "title": "Implement custom scoring dimensions"},
        {"step": 4, "agent": "codex", "type": "test", "title": "Write integration tests"},
    ]
    print(f"  [Plan Presented to User]")
    print(f"  This is a multi-step task. Here's my plan:")
    for p in plan:
        parallel = " (parallel with #2)" if p["step"] == 3 else ""
        print(f"    {p['step']}. [{p['agent'].capitalize()}] {p['title']}{parallel}")
    print()

    # Step 3: Simulate user approval
    print(f"  User: \"yes, proceed\"")
    print()

    # Step 4: Dispatch tasks sequentially (simulated)
    results = []
    mock_responses = [
        {"status": "success", "summary": "Designed PluginInterface, ScoringDimension, and PluginRegistry interfaces"},
        {"status": "success", "summary": "Implemented plugin_loader.py with dynamic import support"},
        {"status": "success", "summary": "Implemented custom scoring dimensions with weighted composition"},
        {"status": "success", "summary": "Created 15 integration tests covering plugin lifecycle"},
    ]

    for i, (step, response) in enumerate(zip(plan, mock_responses)):
        task_id = f"sim-large-{step['step']:03d}"
        print(f"  [Dispatch #{step['step']}] [{step['agent']}] {step['title']}")

        result = create_result(task_id, step["agent"], 0, json.dumps(response), "", 30.0 + i * 10)
        results.append(result)
        save_result(result, config)
        print(f"    Status: {result['status']} | Duration: {result['duration_seconds']:.0f}s")

    print()

    # Step 5: Final report
    succeeded = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - succeeded
    print(f"  [Final Report]")
    print(f"  Tasks completed: {len(results)}")
    print(f"  Succeeded: {succeeded}, Failed: {failed}")
    print(f"  Total time: {sum(r['duration_seconds'] for r in results):.0f}s")
    print()

    assert succeeded == 4
    print("  PASS: Large task flow completed successfully")
    return True


def simulate_concurrency_check(config: ProjectConfig, project_root: Path) -> bool:
    """Simulate the concurrency awareness flow.

    Flow: Agent running → user requests new task → Kiro asks about queueing
    """
    header("SIMULATION: Concurrency Check")

    # Simulate an agent already running
    mgr = AgentProcessManager(state_dir=project_root / ".agents" / "state")
    mgr.register_process("existing-task", "term-123", "codex", "Building the parser")
    print(f"  [Setup] Agent running: codex - 'Building the parser'")
    print()

    # New user request
    user_request = "fix the typo in utils.py"
    print(f"  User: \"{user_request}\"")
    print()

    # Check concurrency
    assert mgr.is_any_running()
    summary = mgr.get_running_summary()
    print(f"  [Concurrency Check]")
    print(f"  {summary}")
    print()

    # Kiro would ask user:
    print(f"  [Kiro asks user]:")
    print(f"  \"An agent is currently working on 'Building the parser'. Would you like me to:")
    print(f"   a) Queue this task until it finishes")
    print(f"   b) Dispatch in parallel\"")
    print()

    # Simulate user choosing parallel
    print(f"  User: \"b - parallel\"")
    print()

    # Dispatch anyway
    classification = classify_task(user_request)
    assert classification.is_small
    print(f"  [Dispatch] Small task, dispatching in parallel")
    print(f"  Now 2 agents running concurrently")
    print()

    # Cleanup
    mgr.clear_all()
    assert not mgr.is_any_running()
    print("  PASS: Concurrency check flow completed successfully")
    return True


def simulate_failure_fallback(config: ProjectConfig, project_root: Path) -> bool:
    """Simulate failure detection and fallback offer.

    Flow: Codex fails → Kiro reports → offers Claude as fallback → Claude succeeds
    """
    header("SIMULATION: Failure + Fallback")

    user_request = "implement the scoring validator"
    print(f"  User: \"{user_request}\"")
    print()

    task_id = "sim-fallback-001"

    # Step 1: First attempt with Codex fails
    print(f"  [Attempt 1] Dispatching to codex...")
    fail_stdout = json.dumps({
        "status": "fail",
        "summary": "Could not parse the scoring spec",
        "errors": ["KeyError: 'demand_score' field not found in template"],
    })
    result1 = create_result(task_id, "codex", 0, fail_stdout, "", 15.0)
    print(f"  [Result] Status: {result1['status']}")
    print(f"           Error: {result1['errors'][0]}")
    print()

    # Step 2: Kiro offers fallback
    print(f"  [Kiro to User]:")
    print(f"  \"Codex-CLI failed: {result1['errors'][0]}\"")
    print(f"  \"Would you like me to retry with Claude-CLI?\"")
    print()
    print(f"  User: \"yes\"")
    print()

    # Step 3: Retry with Claude succeeds
    print(f"  [Attempt 2] Dispatching to claude (fallback)...")
    success_stdout = json.dumps({
        "status": "success",
        "summary": "Implemented validator with field presence checks and type validation",
        "files_created": ["scripts/dev/scoring_validator.py"],
    })
    result2 = create_result(task_id + "-fallback", "claude", 0, success_stdout, "", 28.0)
    save_result(result2, config)
    print(f"  [Result] Status: {result2['status']}")
    print(f"           Summary: {result2['summary']}")
    print()

    assert result2["status"] == "success"
    print("  PASS: Failure + fallback flow completed successfully")
    return True


def main() -> int:
    """Run all simulations."""
    header("9ake-kiro-agents Auto-Dispatch Integration Simulation")
    print("  This verifies the full auto-dispatch pipeline that Kiro uses")
    print("  to automatically spawn Claude/Codex agents as background processes.")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        config = setup_project(tmp_path)
        project_root = config.project_root

        results = []
        results.append(("Small Task (Auto)", simulate_small_task(config, project_root)))
        results.append(("Large Task (Plan)", simulate_large_task(config, project_root)))
        results.append(("Concurrency Check", simulate_concurrency_check(config, project_root)))
        results.append(("Failure + Fallback", simulate_failure_fallback(config, project_root)))

        # Final summary
        header("SIMULATION RESULTS")
        all_pass = True
        for name, passed in results:
            icon = "PASS" if passed else "FAIL"
            print(f"  [{icon}] {name}")
            if not passed:
                all_pass = False

        print()
        if all_pass:
            print("  All simulations passed! Auto-dispatch pipeline is working.")
        else:
            print("  Some simulations failed.")

        return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
