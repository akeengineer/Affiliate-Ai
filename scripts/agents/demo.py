"""Demo script for 9ake-kiro-agents orchestration pipeline.

Demonstrates the full E2E pipeline using mocked agents.
Run: python scripts/agents/demo.py

This shows what happens when Kiro orchestrates tasks through
Claude-CLI and Codex-CLI agents.
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from scripts.agents.core.collector import Collector
from scripts.agents.core.dispatcher import Dispatcher
from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.result import AgentResult
from scripts.agents.core.reporter import Reporter
from scripts.agents.core.retry import RetryEngine
from scripts.agents.create_task import create_batch


DEMO_CONFIG = {
    "project_name": "Affiliate-Ai (Demo)",
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
    "ssh": {"host": "god-of-ai", "project_path": str(PROJECT_ROOT), "user": "ubuntu"},
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


def setup_demo_project(tmp_path: Path) -> ProjectConfig:
    """Set up a temporary project for the demo."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports", "prompts", "schemas"]:
        (agents_dir / sub).mkdir()

    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(DEMO_CONFIG), encoding="utf-8")
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text("# Claude", encoding="utf-8")
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text("# Codex", encoding="utf-8")

    return ProjectConfig.load(str(config_path))


def print_header(text: str) -> None:
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()


def print_step(num: int, text: str) -> None:
    """Print a step indicator."""
    print(f"  [{num}] {text}")


def main() -> int:
    """Run the full demo pipeline."""
    print_header("9ake-kiro-agents Demo - Full E2E Pipeline")
    print("  This demo shows Kiro orchestrating tasks through")
    print("  Claude-CLI (reasoning) and Codex-CLI (implementation) agents.")
    print("  All agent calls are mocked for demonstration.")
    print()

    # Setup
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        config = setup_demo_project(tmp_path)
        print_step(0, f"Demo project created at: {tmp_path}")
        print()

        # Step 1: Create tasks
        print_header("Step 1: Create Tasks")
        tasks_data = [
            {
                "title": "Design scoring module interface",
                "type": "design",
                "prompt": "Design the Product Opportunity Score calculator interfaces",
                "priority": "high",
                "input_files": ["docs/SCORING_SPEC.md"],
            },
            {
                "title": "Implement score_product.py",
                "type": "implementation",
                "prompt": "Create scripts/dev/score_product.py with YAML frontmatter parsing and weighted scoring",
                "priority": "high",
                "input_files": ["docs/SCORING_SPEC.md", "docs/OBSIDIAN_CONTRACT.md"],
                "expected_outputs": ["scripts/dev/score_product.py"],
            },
            {
                "title": "Write scoring tests",
                "type": "test",
                "prompt": "Create tests/test_score_product.py covering all thresholds and edge cases",
                "priority": "medium",
                "expected_outputs": ["tests/test_score_product.py"],
            },
        ]
        tasks = create_batch(tasks_data, config=config)
        for task in tasks:
            print_step(1, f"Created: [{task.type.value:14s}] {task.title}")
        print()

        # Step 2: Plan dispatch
        print_header("Step 2: Plan Dispatch")
        dispatcher = Dispatcher(config)
        plan = dispatcher.create_plan()
        print(f"  Total tasks: {plan.total_tasks}")
        print(f"  Parallel groups: {len(plan.parallel_groups)}")
        print()
        for i, group in enumerate(plan.parallel_groups, 1):
            print(f"  Group {i}:")
            for cmd in group:
                print(f"    -> [{cmd.agent.name:6s}] {cmd.task.title}")
        print()

        # Step 3: Dispatch with mocked agents
        print_header("Step 3: Dispatch (Mocked Agents)")

        # Mock responses
        mock_responses = {
            "design": json.dumps({
                "status": "success",
                "summary": "Designed 3 interfaces: ScoreParser, ScoreCalculator, DecisionEngine",
                "files_created": [],
                "next_steps": ["Implement ScoreCalculator"],
            }),
            "implementation": json.dumps({
                "status": "success",
                "summary": "Implemented score_product.py with 7 scoring dimensions",
                "files_created": ["scripts/dev/score_product.py"],
                "tests_run": None,
                "tests_passed": None,
            }),
            "test": json.dumps({
                "status": "success",
                "summary": "Created 12 test cases covering all thresholds",
                "files_created": ["tests/test_score_product.py"],
                "tests_run": "python -m pytest tests/test_score_product.py -v",
                "tests_passed": True,
            }),
        }

        call_idx = [0]

        def mock_subprocess(cmd, **kwargs):
            call_idx[0] += 1
            cmd_str = " ".join(cmd)
            # Determine which task type based on command content
            for task_type, response in mock_responses.items():
                if task_type.upper() in cmd_str:
                    return MagicMock(returncode=0, stdout=response, stderr="")
            # Default success
            return MagicMock(
                returncode=0,
                stdout=json.dumps({"status": "success", "summary": "Done"}),
                stderr="",
            )

        collector = Collector(config)
        retry_engine = RetryEngine(config, sleep_fn=lambda s: None)
        results = []

        with patch("scripts.agents.core.dispatcher.subprocess.run", side_effect=mock_subprocess):
            for group in plan.parallel_groups:
                for dispatch_cmd in group:
                    agent = dispatch_cmd.agent
                    start = time.time()

                    def dispatch_fn(t, a, attempt, is_fallback):
                        cmd = dispatcher.build_dispatch_command(t)
                        process_result = dispatcher.execute_command(cmd)
                        return collector.collect(
                            cmd, process_result, attempt=attempt,
                            duration_seconds=time.time() - start,
                        )

                    result, log = retry_engine.execute_with_retry(
                        dispatch_cmd.task, agent, dispatch_fn
                    )
                    results.append(result)

                    status_icon = "+" if result.is_success else "x"
                    print(f"  [{status_icon}] {dispatch_cmd.task.title}")
                    print(f"      Agent: {log.final_agent} | Attempts: {len(log.attempts)}")
                    print(f"      Summary: {result.summary}")
                    print()

        # Step 4: Report
        print_header("Step 4: Generate Report")
        reporter = Reporter(config)
        report_path = reporter.generate(results, title="Demo Orchestration Run")
        print(f"  Markdown report: {report_path.name}")

        json_path = report_path.with_name(
            report_path.stem.replace("-report", "-summary") + ".json"
        )
        print(f"  JSON summary:    {json_path.name}")
        print()

        # Summary
        summary = reporter.generate_summary(results)
        print_header("Final Summary")
        print(f"  Tasks dispatched: {summary['total_tasks']}")
        print(f"  Succeeded:        {summary['status_counts'].get('success', 0)}")
        print(f"  Failed:           {summary['status_counts'].get('fail', 0)}")
        print(f"  Agent usage:      {dict(summary['agent_utilization'])}")
        print(f"  Fallbacks:        {summary['fallback_count']}")
        print()
        print("  Pipeline complete! All components wired and working.")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
