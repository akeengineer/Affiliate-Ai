"""Task Creator CLI for 9ake-kiro-agents.

Creates task JSON files and places them in the agent queue for dispatch.

Usage:
    python scripts/agents/create_task.py --title "..." --type implementation --prompt "..."
    python scripts/agents/create_task.py --from-json tasks.json
    echo '{"title": "...", ...}' | python scripts/agents/create_task.py --from-stdin
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.task import Task, TaskType


def create_single_task(
    title: str,
    task_type: str,
    prompt: str,
    priority: str = "medium",
    agent_preference: str = "auto",
    dependencies: Optional[List[str]] = None,
    input_files: Optional[List[str]] = None,
    expected_outputs: Optional[List[str]] = None,
    timeout_seconds: int = 300,
    max_retries: int = 2,
    config: Optional[ProjectConfig] = None,
) -> Task:
    """Create a single task and save it to the queue.

    Args:
        title: Human-readable task title.
        task_type: Task type (must be valid TaskType).
        prompt: The instruction for the agent.
        priority: Task priority level.
        agent_preference: Preferred agent or 'auto'.
        dependencies: Task IDs that must complete first.
        input_files: Files the agent should read.
        expected_outputs: Expected output artifacts.
        timeout_seconds: Max execution time.
        max_retries: Max retry attempts.
        config: Project configuration (auto-loaded if None).

    Returns:
        The created Task instance.

    Raises:
        ValueError: If task_type is invalid.
        FileNotFoundError: If config cannot be found.
    """
    # Validate task type
    try:
        TaskType(task_type)
    except ValueError:
        valid_types = [t.value for t in TaskType]
        raise ValueError(
            f"Invalid task type '{task_type}'. Valid types: {valid_types}"
        )

    # Load config if not provided
    if config is None:
        config = ProjectConfig.load()

    # Create the task
    task = Task.create(
        title=title,
        task_type=task_type,
        prompt=prompt,
        priority=priority,
        agent_preference=agent_preference,
        dependencies=dependencies,
        input_files=input_files,
        expected_outputs=expected_outputs,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
    )

    # Save to queue directory
    queue_dir = Path(config.paths.queue)
    if config.project_root:
        queue_dir = config.project_root / config.paths.queue
    saved_path = task.save(queue_dir)

    return task


def create_from_dict(data: dict, config: Optional[ProjectConfig] = None) -> Task:
    """Create a task from a dictionary (e.g., parsed from JSON).

    Args:
        data: Dictionary with task fields (title, type, prompt required).
        config: Project configuration.

    Returns:
        The created Task instance.

    Raises:
        KeyError: If required fields are missing.
        ValueError: If field values are invalid.
    """
    required_fields = ["title", "type", "prompt"]
    for field in required_fields:
        if field not in data:
            raise KeyError(f"Missing required field: '{field}'")

    return create_single_task(
        title=data["title"],
        task_type=data["type"],
        prompt=data["prompt"],
        priority=data.get("priority", "medium"),
        agent_preference=data.get("agent_preference", "auto"),
        dependencies=data.get("dependencies"),
        input_files=data.get("input_files"),
        expected_outputs=data.get("expected_outputs"),
        timeout_seconds=data.get("timeout_seconds", 300),
        max_retries=data.get("max_retries", 2),
        config=config,
    )


def create_batch(tasks_data: List[dict], config: Optional[ProjectConfig] = None) -> List[Task]:
    """Create multiple tasks from a list of dictionaries.

    Args:
        tasks_data: List of task dictionaries.
        config: Project configuration.

    Returns:
        List of created Task instances.
    """
    if config is None:
        config = ProjectConfig.load()

    tasks = []
    for data in tasks_data:
        task = create_from_dict(data, config=config)
        tasks.append(task)
    return tasks


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Create tasks for 9ake-kiro-agents orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Create a single implementation task
  python scripts/agents/create_task.py \\
    --title "Implement scoring script" \\
    --type implementation \\
    --prompt "Create scripts/dev/score_product.py following docs/SCORING_SPEC.md"

  # Create with dependencies and input files
  python scripts/agents/create_task.py \\
    --title "Write tests for scoring" \\
    --type test \\
    --prompt "Write pytest tests for score_product.py" \\
    --depends-on 12345678-1234-1234-1234-123456789abc \\
    --input-file scripts/dev/score_product.py

  # Create from JSON file (batch)
  python scripts/agents/create_task.py --from-json tasks.json

  # Create from stdin
  echo '{"title":"Quick task","type":"implementation","prompt":"Do X"}' | \\
    python scripts/agents/create_task.py --from-stdin
        """,
    )

    # Single task mode
    parser.add_argument("--title", help="Task title")
    parser.add_argument(
        "--type",
        dest="task_type",
        choices=[t.value for t in TaskType],
        help="Task type",
    )
    parser.add_argument("--prompt", help="Task prompt/instruction")
    parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Task priority (default: medium)",
    )
    parser.add_argument(
        "--agent",
        choices=["claude", "codex", "auto"],
        default="auto",
        help="Preferred agent (default: auto)",
    )
    parser.add_argument(
        "--depends-on",
        action="append",
        default=[],
        help="Task ID dependency (can be repeated)",
    )
    parser.add_argument(
        "--input-file",
        action="append",
        default=[],
        help="Input file for agent context (can be repeated)",
    )
    parser.add_argument(
        "--expected-output",
        action="append",
        default=[],
        help="Expected output file (can be repeated)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max retry attempts (default: 2)",
    )

    # Batch/stdin modes
    parser.add_argument(
        "--from-json",
        metavar="FILE",
        help="Create tasks from a JSON file (array of task objects)",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="Read task JSON from stdin",
    )

    # Config override
    parser.add_argument(
        "--config",
        help="Path to config.yaml (default: auto-discover)",
    )

    # Output options
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output created task(s) as JSON",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        # Load config
        config = ProjectConfig.load(args.config)

        # Determine mode
        if args.from_json:
            # Batch from JSON file
            json_path = Path(args.from_json)
            if not json_path.exists():
                print(f"Error: File not found: {args.from_json}", file=sys.stderr)
                return 1
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                tasks = create_batch(data, config=config)
            else:
                tasks = [create_from_dict(data, config=config)]

        elif args.from_stdin:
            # From stdin
            stdin_data = sys.stdin.read().strip()
            if not stdin_data:
                print("Error: No data received from stdin", file=sys.stderr)
                return 1
            data = json.loads(stdin_data)
            if isinstance(data, list):
                tasks = create_batch(data, config=config)
            else:
                tasks = [create_from_dict(data, config=config)]

        else:
            # Single task from CLI args
            if not args.title or not args.task_type or not args.prompt:
                print(
                    "Error: --title, --type, and --prompt are required for single task mode",
                    file=sys.stderr,
                )
                parser.print_usage(sys.stderr)
                return 1

            task = create_single_task(
                title=args.title,
                task_type=args.task_type,
                prompt=args.prompt,
                priority=args.priority,
                agent_preference=args.agent,
                dependencies=args.depends_on or None,
                input_files=args.input_file or None,
                expected_outputs=args.expected_output or None,
                timeout_seconds=args.timeout,
                max_retries=args.max_retries,
                config=config,
            )
            tasks = [task]

        # Output results
        if args.json_output:
            if len(tasks) == 1:
                print(tasks[0].to_json())
            else:
                print(json.dumps([t.to_dict() for t in tasks], indent=2))
        else:
            for task in tasks:
                queue_dir = Path(config.paths.queue)
                if config.project_root:
                    queue_dir = config.project_root / config.paths.queue
                file_path = queue_dir / f"{task.id}.json"
                print(f"Created task: {task.id}")
                print(f"  Title: {task.title}")
                print(f"  Type: {task.type.value}")
                print(f"  Priority: {task.priority.value}")
                print(f"  Agent: {task.agent_preference}")
                print(f"  File: {file_path}")
                print()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
