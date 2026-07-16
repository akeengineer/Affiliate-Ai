"""Kiro Dispatch Helper — Background execution wrapper for CLI agents.

This script is spawned by Kiro as a background process to dispatch tasks
to Claude-CLI or Codex-CLI agents. It handles:
- Config loading and CLI command construction
- Process execution with timeout
- Real-time progress output (stdout)
- Final result output (JSON after ===RESULT=== marker)

Usage (spawned by Kiro via control_pwsh_process):
    python scripts/agents/kiro_dispatch.py --agent codex --type implementation --prompt "..."
    python scripts/agents/kiro_dispatch.py --agent claude --type design --prompt "..." --remote
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskType

# Marker that Kiro looks for to find the JSON result
RESULT_MARKER = "===RESULT==="


def log(msg: str) -> None:
    """Print a timestamped log message to stdout for Kiro to read."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def build_agent_command(
    agent: AgentConfig,
    prompt: str,
    task_id: str,
    task_type: str,
    project_root: Path,
) -> List[str]:
    """Build the CLI command to invoke the agent.

    Args:
        agent: Agent configuration.
        prompt: Task prompt.
        task_id: UUID of the task.
        task_type: Type of the task.
        project_root: Project root path.

    Returns:
        Command list for subprocess.
    """
    cmd = [agent.command] + list(agent.flags)

    if agent.name == "claude":
        # Add system prompt
        if agent.system_prompt:
            prompt_path = project_root / agent.system_prompt
            if prompt_path.exists():
                cmd.extend(["--system-prompt-file", str(prompt_path)])
        # Add limits
        if agent.max_turns:
            cmd.extend(["--max-turns", str(agent.max_turns)])
        if agent.max_budget_usd:
            cmd.extend(["--max-budget-usd", str(agent.max_budget_usd)])

    # Build full prompt with task metadata
    full_prompt = (
        f"TASK_ID: {task_id}\n"
        f"TASK_TYPE: {task_type}\n\n"
        f"INSTRUCTION:\n{prompt}\n\n"
        f"Return your result as JSON with fields: status, summary, files_modified, "
        f"files_created, tests_run, tests_passed, errors, next_steps"
    )
    cmd.append(full_prompt)

    return cmd


def execute_agent(
    cmd: List[str],
    timeout_seconds: int,
    cwd: str,
) -> tuple:
    """Execute the agent CLI command.

    Args:
        cmd: Command to execute.
        timeout_seconds: Max execution time.
        cwd: Working directory.

    Returns:
        Tuple of (returncode, stdout, stderr, duration_seconds).
    """
    start_time = time.time()

    try:
        log(f"Executing: {cmd[0]} ...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd,
        )
        duration = time.time() - start_time
        return result.returncode, result.stdout, result.stderr, duration

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return -1, "", f"TIMEOUT: exceeded {timeout_seconds}s", duration

    except FileNotFoundError as e:
        duration = time.time() - start_time
        return 127, "", f"Command not found: {cmd[0]} ({e})", duration


def parse_agent_output(stdout: str) -> Optional[dict]:
    """Parse JSON from agent output.

    Tries:
    1. Direct JSON parse of entire stdout
    2. Find JSON between { and }

    Args:
        stdout: Raw agent output.

    Returns:
        Parsed dict or None.
    """
    if not stdout or not stdout.strip():
        return None

    text = stdout.strip()

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Try finding JSON object
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace + 1]
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    return None


def create_result(
    task_id: str,
    agent_name: str,
    returncode: int,
    stdout: str,
    stderr: str,
    duration: float,
) -> dict:
    """Create a result dict from execution output.

    Args:
        task_id: Task UUID.
        agent_name: Agent that executed.
        returncode: Process return code.
        stdout: Agent stdout.
        stderr: Agent stderr.
        duration: Execution time.

    Returns:
        Result dictionary matching the agent result schema.
    """
    # Handle timeout
    if returncode == -1:
        return {
            "task_id": task_id,
            "agent": agent_name,
            "status": "timeout",
            "summary": f"Agent timed out after {duration:.0f}s",
            "files_modified": [],
            "files_created": [],
            "tests_run": None,
            "tests_passed": None,
            "errors": [stderr],
            "duration_seconds": duration,
            "next_steps": ["Increase timeout or simplify task"],
        }

    # Handle command not found
    if returncode == 127:
        return {
            "task_id": task_id,
            "agent": agent_name,
            "status": "fail",
            "summary": f"Agent command not found: {agent_name}",
            "files_modified": [],
            "files_created": [],
            "tests_run": None,
            "tests_passed": None,
            "errors": [stderr],
            "duration_seconds": duration,
            "next_steps": [f"Install {agent_name} CLI or check PATH"],
        }

    # Handle non-zero exit
    if returncode != 0:
        return {
            "task_id": task_id,
            "agent": agent_name,
            "status": "fail",
            "summary": f"Agent exited with code {returncode}",
            "files_modified": [],
            "files_created": [],
            "tests_run": None,
            "tests_passed": None,
            "errors": [stderr or f"Exit code {returncode}"],
            "duration_seconds": duration,
            "next_steps": ["Check agent logs for details"],
        }

    # Parse structured output
    parsed = parse_agent_output(stdout)
    if parsed:
        # Use agent's structured response
        return {
            "task_id": task_id,
            "agent": agent_name,
            "status": parsed.get("status", "success"),
            "summary": parsed.get("summary", "Task completed"),
            "files_modified": parsed.get("files_modified", []),
            "files_created": parsed.get("files_created", []),
            "tests_run": parsed.get("tests_run"),
            "tests_passed": parsed.get("tests_passed"),
            "errors": parsed.get("errors", []),
            "duration_seconds": duration,
            "next_steps": parsed.get("next_steps", []),
        }

    # Fallback: unstructured output
    return {
        "task_id": task_id,
        "agent": agent_name,
        "status": "partial",
        "summary": "Agent completed but did not return structured JSON",
        "files_modified": [],
        "files_created": [],
        "tests_run": None,
        "tests_passed": None,
        "errors": ["Output was not valid JSON"],
        "duration_seconds": duration,
        "raw_output": stdout[:2000],  # Truncate for safety
        "next_steps": ["Review raw output manually"],
    }


def save_result(result: dict, config: ProjectConfig) -> Path:
    """Save result to the results directory.

    Args:
        result: Result dict.
        config: Project config.

    Returns:
        Path to saved file.
    """
    project_root = config.project_root or Path.cwd()
    results_dir = project_root / config.paths.results
    results_dir.mkdir(parents=True, exist_ok=True)

    task_id = result.get("task_id", str(uuid.uuid4()))
    file_path = results_dir / f"{task_id}.json"

    # Add timestamp
    result["completed_at"] = datetime.now(timezone.utc).isoformat()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return file_path


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Kiro Dispatch Helper — spawn CLI agents for task execution",
    )
    parser.add_argument(
        "--agent",
        required=True,
        choices=["claude", "codex", "agy"],
        help="Agent to dispatch to",
    )
    parser.add_argument(
        "--type",
        dest="task_type",
        default="implementation",
        choices=["reasoning", "design", "review", "implementation", "test", "refactor", "research", "debug", "investigate"],
        help="Task type",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Task prompt/instruction",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to config.yaml (default: auto-discover)",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Execute on remote host via SSH",
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help="Task ID (auto-generated if not provided)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command-line arguments.

    Returns:
        Exit code (0=success, 1=fail).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    task_id = args.task_id or str(uuid.uuid4())

    log(f"Task ID: {task_id}")
    log(f"Agent: {args.agent}")
    log(f"Type: {args.task_type}")
    log(f"Timeout: {args.timeout}s")
    log("")

    # Load config
    try:
        config = ProjectConfig.load(args.config)
        log(f"Config loaded: {config.project_name}")
    except FileNotFoundError:
        log("WARNING: No .agents/config.yaml found, using defaults")
        config = None

    # Get agent config
    if config:
        agent_config = config.get_agent(args.agent)
        if not agent_config:
            log(f"ERROR: Agent '{args.agent}' not found in config")
            result = {
                "task_id": task_id,
                "agent": args.agent,
                "status": "fail",
                "summary": f"Agent '{args.agent}' not configured",
                "errors": [f"Add '{args.agent}' to .agents/config.yaml"],
            }
            print(f"\n{RESULT_MARKER}")
            print(json.dumps(result, indent=2))
            return 1
        project_root = config.project_root or Path.cwd()
    else:
        # Fallback defaults
        from scripts.agents.core.models.config import AgentConfig
        if args.agent == "claude":
            agent_config = AgentConfig(
                name="claude",
                command="claude",
                flags=["-p", "--dangerously-skip-permissions", "--output-format", "json"],
                task_types=["reasoning", "design", "review"],
            )
        else:
            agent_config = AgentConfig(
                name="codex",
                command="codex",
                flags=["-q", "--approval-mode", "full-auto"],
                task_types=["implementation", "test", "refactor"],
            )
        project_root = Path.cwd()

    # Handle remote execution
    if args.remote:
        if not config or not config.ssh.host:
            log("ERROR: No SSH host configured for remote execution")
            result = {
                "task_id": task_id,
                "agent": args.agent,
                "status": "fail",
                "summary": "Remote execution requested but no SSH host configured",
                "errors": ["Set ssh.host in .agents/config.yaml"],
            }
            print(f"\n{RESULT_MARKER}")
            print(json.dumps(result, indent=2))
            return 1

        log(f"Remote execution on: {config.ssh.host}")
        # Build remote command (activate venv + ensure CLI tools in PATH)
        remote_prompt = args.prompt.replace('"', '\\"')
        remote_cmd = (
            f"export PATH=/home/ubuntu/.local/bin:/root/.local/bin:$PATH && "
            f"cd {config.ssh.project_path} && "
            f"source .venv/bin/activate && "
            f"python3 scripts/agents/kiro_dispatch.py "
            f"--agent {args.agent} --type {args.task_type} "
            f'--prompt "{remote_prompt}" --task-id {task_id} --timeout {args.timeout}'
        )
        cmd = ["ssh", config.ssh.ssh_target, remote_cmd]
    else:
        # Local execution
        log("Local execution")
        cmd = build_agent_command(
            agent=agent_config,
            prompt=args.prompt,
            task_id=task_id,
            task_type=args.task_type,
            project_root=project_root,
        )

    # Execute
    log(f"Dispatching to {args.agent}...")
    log("")
    returncode, stdout, stderr, duration = execute_agent(
        cmd=cmd,
        timeout_seconds=args.timeout,
        cwd=str(project_root),
    )
    log("")
    log(f"Agent finished in {duration:.1f}s (exit code: {returncode})")

    # Create result
    result = create_result(
        task_id=task_id,
        agent_name=args.agent,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )

    # Save result to disk
    if config:
        saved_path = save_result(result, config)
        log(f"Result saved: {saved_path}")

    # Output result with marker (Kiro reads this)
    print(f"\n{RESULT_MARKER}")
    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
