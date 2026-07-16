"""Orchestrator CLI for 9ake-kiro-agents.

Main entry point that wires all components together.
Kiro uses this to plan, dispatch, monitor, and report on agent tasks.

Usage:
    python scripts/agents/orchestrate.py init
    python scripts/agents/orchestrate.py create --title "..." --type implementation --prompt "..."
    python scripts/agents/orchestrate.py dispatch [--dry-run]
    python scripts/agents/orchestrate.py status
    python scripts/agents/orchestrate.py results
    python scripts/agents/orchestrate.py report
    python scripts/agents/orchestrate.py run "description"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.agents.core.collector import Collector
from scripts.agents.core.dispatcher import Dispatcher, DispatchCommand
from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.result import AgentResult
from scripts.agents.core.models.task import Task, TaskStatus
from scripts.agents.core.retry import RetryEngine
from scripts.agents.core.ssh_bridge import SSHBridge
from scripts.agents.create_task import create_single_task


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize .agents/ structure in the current directory.

    Creates directory structure, default config, and template prompts.
    """
    target = Path.cwd()
    agents_dir = target / ".agents"

    if agents_dir.exists() and (agents_dir / "config.yaml").exists():
        print("Already initialized: .agents/config.yaml exists.")
        return 0

    # Create directories
    for sub in ["prompts", "schemas", "queue", "results", "state", "reports"]:
        (agents_dir / sub).mkdir(parents=True, exist_ok=True)

    # Write default config
    project_name = args.project_name or target.name
    config_content = f"""# 9ake-kiro-agents Configuration
project_name: "{project_name}"
package_name: "9ake-kiro-agents"

agents:
  claude:
    command: "claude"
    flags:
      - "-p"
      - "--dangerously-skip-permissions"
      - "--output-format"
      - "json"
    system_prompt: ".agents/prompts/claude-cli-agent.md"
    max_turns: 10
    max_budget_usd: 5.00
    task_types:
      - "reasoning"
      - "design"
      - "review"
    fallback_to: "codex"

  codex:
    command: "codex"
    flags:
      - "-q"
      - "--approval-mode"
      - "full-auto"
    system_prompt: ".agents/prompts/codex-cli-agent.md"
    task_types:
      - "implementation"
      - "test"
      - "refactor"
    fallback_to: "claude"

dispatch:
  retry_max: 2
  retry_backoff_seconds:
    - 5
    - 15
  fallback_enabled: true
  parallel_max: 2
  default_timeout_seconds: 300

ssh:
  host: ""
  project_path: ""
  user: ""

validation:
  run_tests: true
  test_command: "python -m pytest"
  check_files_exist: true

paths:
  queue: ".agents/queue"
  results: ".agents/results"
  state: ".agents/state"
  reports: ".agents/reports"
  prompts: ".agents/prompts"
  schemas: ".agents/schemas"
"""
    (agents_dir / "config.yaml").write_text(config_content, encoding="utf-8")

    # Write template prompts (minimal)
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text(
        "# Claude-CLI Agent\n\nYou are the reasoning and design agent.\n",
        encoding="utf-8",
    )
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text(
        "# Codex-CLI Agent\n\nYou are the implementation and testing agent.\n",
        encoding="utf-8",
    )
    (agents_dir / "prompts" / "shared-context.md").write_text(
        "# Shared Context\n\nProject-specific rules go here.\n",
        encoding="utf-8",
    )

    # Write .gitkeep for gitignored dirs
    for sub in ["queue", "results", "state", "reports"]:
        gitkeep = agents_dir / sub / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    print(f"Initialized .agents/ in {target}")
    print(f"  Project: {project_name}")
    print(f"  Config:  .agents/config.yaml")
    print(f"  Prompts: .agents/prompts/")
    print()
    print("Next steps:")
    print("  1. Edit .agents/config.yaml (set ssh.host if using remote)")
    print("  2. Customize .agents/prompts/ for your project")
    print("  3. Add .agents/queue/ .agents/results/ .agents/state/ .agents/reports/ to .gitignore")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    """Create a task (delegates to create_task module)."""
    from scripts.agents.create_task import main as create_main

    # Forward args to create_task
    forward_args = []
    if args.title:
        forward_args.extend(["--title", args.title])
    if args.task_type:
        forward_args.extend(["--type", args.task_type])
    if args.prompt:
        forward_args.extend(["--prompt", args.prompt])
    if args.priority:
        forward_args.extend(["--priority", args.priority])
    if args.agent:
        forward_args.extend(["--agent", args.agent])
    if args.config_path:
        forward_args.extend(["--config", args.config_path])
    if args.json_output:
        forward_args.append("--json-output")

    return create_main(forward_args)


def cmd_dispatch(args: argparse.Namespace) -> int:
    """Dispatch queued tasks to agents."""
    config = ProjectConfig.load(args.config_path)
    dispatcher = Dispatcher(config)

    plan = dispatcher.create_plan()

    if plan.total_tasks == 0:
        print("No tasks in queue.")
        return 0

    print(f"Dispatch plan: {plan.total_tasks} task(s) in {len(plan.parallel_groups)} group(s)")
    print()

    for i, group in enumerate(plan.parallel_groups, 1):
        print(f"  Group {i} ({len(group)} task{'s' if len(group) > 1 else ''}, parallel):")
        for cmd in group:
            print(f"    - [{cmd.agent.name}] {cmd.task.title}")
            if args.dry_run:
                print(f"      CMD: {cmd.command_str}")
        print()

    if plan.skipped:
        print("  Skipped:")
        for task, reason in plan.skipped:
            print(f"    - {task.title}: {reason}")
        print()

    if args.dry_run:
        print("(dry-run — no tasks executed)")
        return 0

    # Execute with retry/fallback
    collector = Collector(config)
    retry_engine = RetryEngine(config)
    results: List[AgentResult] = []

    for i, group in enumerate(plan.parallel_groups, 1):
        print(f"Executing group {i}...")
        for dispatch_cmd in group:
            agent = dispatch_cmd.agent

            def dispatch_fn(task, agent_cfg, attempt, is_fallback):
                cmd = dispatcher.build_dispatch_command(task, is_fallback=is_fallback)
                if not cmd:
                    return AgentResult.create(
                        task_id=task.id, agent=agent_cfg.name,
                        status="fail", summary="No agent found",
                        errors=["Could not build dispatch command"],
                    )
                # Override agent if fallback
                if is_fallback:
                    cmd.agent = agent_cfg
                    cmd.command = dispatcher.build_command(task, agent_cfg)
                process_result = dispatcher.execute_command(cmd)
                return collector.collect(
                    cmd, process_result,
                    attempt=attempt, is_fallback=is_fallback,
                )

            result, retry_log = retry_engine.execute_with_retry(
                dispatch_cmd.task, agent, dispatch_fn
            )
            results.append(result)

            status_icon = "+" if result.is_success else "x"
            print(f"  [{status_icon}] {dispatch_cmd.task.title} -> {result.status.value}")

    # Summary
    print()
    succeeded = sum(1 for r in results if r.is_success)
    failed = len(results) - succeeded
    print(f"Done: {succeeded} succeeded, {failed} failed")
    return 0 if failed == 0 else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show current state of tasks and agents."""
    config = ProjectConfig.load(args.config_path)
    project_root = config.project_root or Path.cwd()

    # Load queue
    dispatcher = Dispatcher(config)
    queued = dispatcher.load_queue()

    # Load state (active/completed/failed tasks)
    state_dir = project_root / config.paths.state
    state_tasks = []
    if state_dir.exists():
        for f in sorted(state_dir.glob("*.json")):
            try:
                task = Task.load(f)
                state_tasks.append(task)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    # Load results
    collector = Collector(config)
    results = collector.load_all_results()

    print("=== 9ake-kiro-agents Status ===")
    print()
    print(f"Queued tasks:    {len(queued)}")
    print(f"Active tasks:    {sum(1 for t in state_tasks if t.status == TaskStatus.ACTIVE)}")
    print(f"Completed tasks: {sum(1 for t in state_tasks if t.status == TaskStatus.COMPLETED)}")
    print(f"Failed tasks:    {sum(1 for t in state_tasks if t.status == TaskStatus.FAILED)}")
    print(f"Results stored:  {len(results)}")
    print()

    if queued:
        print("Queue:")
        for task in queued:
            print(f"  [{task.priority.value:8s}] {task.title} ({task.type.value})")
        print()

    if args.json_output:
        data = {
            "queued": [t.to_dict() for t in queued],
            "state": [t.to_dict() for t in state_tasks],
            "results_count": len(results),
        }
        print(json.dumps(data, indent=2))

    return 0


def cmd_results(args: argparse.Namespace) -> int:
    """Show collected results."""
    config = ProjectConfig.load(args.config_path)
    collector = Collector(config)
    results = collector.load_all_results()

    if not results:
        print("No results collected yet.")
        return 0

    print(f"=== Results ({len(results)} total) ===")
    print()

    for result in results:
        status_icon = "+" if result.is_success else "x"
        fallback_tag = " [fallback]" if result.is_fallback else ""
        print(f"  [{status_icon}] {result.task_id[:8]}... ({result.agent}{fallback_tag})")
        print(f"      Status: {result.status.value} | Attempt: {result.attempt}")
        print(f"      Summary: {result.summary}")
        if result.errors:
            for err in result.errors:
                print(f"      Error: {err}")
        print()

    if args.json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Generate a summary report."""
    # Import reporter here to avoid circular dependency on first load
    from scripts.agents.core.reporter import Reporter

    config = ProjectConfig.load(args.config_path)
    reporter = Reporter(config)
    report_path = reporter.generate()

    print(f"Report generated: {report_path}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Full E2E pipeline: plan -> create tasks -> dispatch -> report.

    Uses Claude to break down the description into tasks, then dispatches them.
    """
    config = ProjectConfig.load(args.config_path)
    description = args.description

    print(f"=== Orchestration Run ===")
    print(f"Description: {description}")
    print()

    # Step 1: Create task(s) from the description
    # For now, create a single task. Full "plan" mode (using Claude to break down)
    # will be added when the orchestrator is proven.
    print("Step 1: Creating task...")
    task_type = args.task_type or "implementation"
    task = create_single_task(
        title=description[:100],
        task_type=task_type,
        prompt=description,
        priority=args.priority or "medium",
        config=config,
    )
    print(f"  Created: {task.id} ({task.type.value})")
    print()

    # Step 2: Dispatch
    print("Step 2: Dispatching...")
    dispatcher = Dispatcher(config)
    collector = Collector(config)
    retry_engine = RetryEngine(config)

    agent = dispatcher.select_agent(task)
    if not agent:
        print(f"  Error: No agent found for task type '{task.type.value}'")
        return 1

    def dispatch_fn(t, agent_cfg, attempt, is_fallback):
        cmd = dispatcher.build_dispatch_command(t, is_fallback=is_fallback)
        if not cmd:
            return AgentResult.create(
                task_id=t.id, agent=agent_cfg.name,
                status="fail", summary="No agent found",
                errors=["Could not build dispatch command"],
            )
        if is_fallback:
            cmd.agent = agent_cfg
            cmd.command = dispatcher.build_command(t, agent_cfg)
        process_result = dispatcher.execute_command(cmd)
        return collector.collect(
            cmd, process_result,
            attempt=attempt, is_fallback=is_fallback,
        )

    result, retry_log = retry_engine.execute_with_retry(task, agent, dispatch_fn)
    print(f"  Agent: {retry_log.final_agent}")
    print(f"  Status: {result.status.value}")
    print(f"  Attempts: {len(retry_log.attempts)}")
    print()

    # Step 3: Report
    print("Step 3: Result")
    print(f"  Summary: {result.summary}")
    if result.files_created:
        print(f"  Files created: {', '.join(result.files_created)}")
    if result.files_modified:
        print(f"  Files modified: {', '.join(result.files_modified)}")
    if result.errors:
        print(f"  Errors:")
        for err in result.errors:
            print(f"    - {err}")
    if result.next_steps:
        print(f"  Next steps:")
        for step in result.next_steps:
            print(f"    - {step}")
    print()

    return 0 if result.is_success else 1


def cmd_remote_status(args: argparse.Namespace) -> int:
    """Check remote EC2 agent status via SSH."""
    config = ProjectConfig.load(args.config_path)

    if not config.ssh.host:
        print("Error: No SSH host configured in .agents/config.yaml")
        return 1

    bridge = SSHBridge(config)
    print(f"Checking remote: {bridge.ssh_target}...")
    print()

    result = bridge.check_remote_status()
    if result.success:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")
    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="orchestrate",
        description="9ake-kiro-agents: Multi-Agent Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", dest="config_path", default=None,
        help="Path to config.yaml (default: auto-discover)",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize .agents/ in current directory")
    init_parser.add_argument("--project-name", default=None, help="Project name")

    # create
    create_parser = subparsers.add_parser("create", help="Create a task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument(
        "--type", dest="task_type", required=True,
        choices=["reasoning", "design", "review", "implementation", "test", "refactor"],
    )
    create_parser.add_argument("--prompt", required=True, help="Task prompt")
    create_parser.add_argument("--priority", default="medium")
    create_parser.add_argument("--agent", default="auto")

    # dispatch
    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch queued tasks")
    dispatch_parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")

    # status
    subparsers.add_parser("status", help="Show current state")

    # results
    subparsers.add_parser("results", help="Show collected results")

    # report
    subparsers.add_parser("report", help="Generate summary report")

    # run
    run_parser = subparsers.add_parser("run", help="Full E2E pipeline")
    run_parser.add_argument("description", help="Task description")
    run_parser.add_argument("--type", dest="task_type", default=None)
    run_parser.add_argument("--priority", default=None)

    # remote-status
    subparsers.add_parser("remote-status", help="Check remote EC2 status")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        commands = {
            "init": cmd_init,
            "create": cmd_create,
            "dispatch": cmd_dispatch,
            "status": cmd_status,
            "results": cmd_results,
            "report": cmd_report,
            "run": cmd_run,
            "remote-status": cmd_remote_status,
        }

        handler = commands.get(args.command)
        if handler:
            return handler(args)
        else:
            parser.print_help()
            return 1

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
