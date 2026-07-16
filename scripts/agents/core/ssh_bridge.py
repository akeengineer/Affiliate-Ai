"""SSH Bridge for 9ake-kiro-agents remote execution.

Enables Kiro (Windows) to dispatch tasks to agents running on EC2 via SSH.
Uses subprocess with ssh/scp commands — no extra dependencies (no paramiko).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from scripts.agents.core.models.config import ProjectConfig, SSHConfig


@dataclass
class RemoteResult:
    """Result from a remote command execution."""

    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        """Whether the command succeeded."""
        return self.returncode == 0


class SSHBridge:
    """Bridge for executing commands and transferring files over SSH.

    Provides:
    - Remote command execution via SSH
    - File push (local -> remote) via SCP
    - File pull (remote -> local) via SCP
    - Remote dispatch: push task, run dispatcher, pull results
    """

    def __init__(
        self,
        config: ProjectConfig,
        ssh_config: Optional[SSHConfig] = None,
        timeout: int = 120,
    ) -> None:
        """Initialize SSH bridge.

        Args:
            config: Project configuration.
            ssh_config: SSH config override. Defaults to config.ssh.
            timeout: Default timeout for SSH commands in seconds.
        """
        self.config = config
        self.ssh = ssh_config or config.ssh
        self.timeout = timeout
        self._project_root = config.project_root or Path.cwd()

    @property
    def ssh_target(self) -> str:
        """SSH connection target (user@host or host alias)."""
        return self.ssh.ssh_target or self.ssh.host

    @property
    def remote_project_path(self) -> str:
        """Remote project directory path."""
        return self.ssh.project_path

    def _build_ssh_command(
        self,
        remote_command: str,
        options: Optional[List[str]] = None,
    ) -> List[str]:
        """Build an SSH command list.

        Args:
            remote_command: Command to run on the remote host.
            options: Additional SSH options (e.g., ['-o', 'StrictHostKeyChecking=no']).

        Returns:
            List of command parts for subprocess.
        """
        cmd = ["ssh"]
        if options:
            cmd.extend(options)
        cmd.append(self.ssh_target)
        cmd.append(remote_command)
        return cmd

    def _build_scp_push_command(
        self,
        local_path: str,
        remote_path: str,
        recursive: bool = False,
    ) -> List[str]:
        """Build an SCP command to push files to remote.

        Args:
            local_path: Local file/directory path.
            remote_path: Remote destination path.
            recursive: Whether to copy directories recursively.

        Returns:
            List of command parts for subprocess.
        """
        cmd = ["scp"]
        if recursive:
            cmd.append("-r")
        cmd.append(local_path)
        cmd.append(f"{self.ssh_target}:{remote_path}")
        return cmd

    def _build_scp_pull_command(
        self,
        remote_path: str,
        local_path: str,
        recursive: bool = False,
    ) -> List[str]:
        """Build an SCP command to pull files from remote.

        Args:
            remote_path: Remote file/directory path.
            local_path: Local destination path.
            recursive: Whether to copy directories recursively.

        Returns:
            List of command parts for subprocess.
        """
        cmd = ["scp"]
        if recursive:
            cmd.append("-r")
        cmd.append(f"{self.ssh_target}:{remote_path}")
        cmd.append(local_path)
        return cmd

    def run_remote(
        self,
        command: str,
        timeout: Optional[int] = None,
    ) -> RemoteResult:
        """Execute a command on the remote host via SSH.

        Args:
            command: Shell command to run remotely.
            timeout: Command timeout in seconds (default: self.timeout).

        Returns:
            RemoteResult with stdout, stderr, and return code.
        """
        ssh_cmd = self._build_ssh_command(command)
        effective_timeout = timeout or self.timeout

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
            )
            return RemoteResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return RemoteResult(
                stdout="",
                stderr=f"SSH command timed out after {effective_timeout}s",
                returncode=-1,
            )
        except FileNotFoundError:
            return RemoteResult(
                stdout="",
                stderr="SSH client not found. Ensure 'ssh' is in PATH.",
                returncode=-2,
            )

    def push_files(
        self,
        local_paths: List[str],
        remote_dir: Optional[str] = None,
    ) -> RemoteResult:
        """Push local files to the remote host via SCP.

        Args:
            local_paths: List of local file paths to push.
            remote_dir: Remote directory to push to.
                Defaults to the remote project path.

        Returns:
            RemoteResult (last SCP result, or aggregated errors).
        """
        target_dir = remote_dir or self.remote_project_path
        all_stderr: List[str] = []
        last_result = RemoteResult(stdout="", stderr="", returncode=0)

        for local_path in local_paths:
            path = Path(local_path)
            is_dir = path.is_dir()
            cmd = self._build_scp_push_command(
                local_path=str(path),
                remote_path=target_dir,
                recursive=is_dir,
            )

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    all_stderr.append(f"Failed to push {local_path}: {result.stderr}")
                last_result = RemoteResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                )
            except subprocess.TimeoutExpired:
                all_stderr.append(f"SCP timed out pushing {local_path}")
                last_result = RemoteResult(stdout="", stderr="SCP timeout", returncode=-1)
            except FileNotFoundError:
                all_stderr.append("SCP client not found")
                last_result = RemoteResult(stdout="", stderr="SCP not found", returncode=-2)
                break

        if all_stderr:
            return RemoteResult(
                stdout="",
                stderr="\n".join(all_stderr),
                returncode=1,
            )
        return last_result

    def pull_files(
        self,
        remote_paths: List[str],
        local_dir: Optional[str] = None,
    ) -> RemoteResult:
        """Pull files from the remote host via SCP.

        Args:
            remote_paths: List of remote file paths to pull.
            local_dir: Local directory to pull to.
                Defaults to the local project root.

        Returns:
            RemoteResult (last SCP result, or aggregated errors).
        """
        target_dir = local_dir or str(self._project_root)
        all_stderr: List[str] = []
        last_result = RemoteResult(stdout="", stderr="", returncode=0)

        for remote_path in remote_paths:
            cmd = self._build_scp_pull_command(
                remote_path=remote_path,
                local_path=target_dir,
            )

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    all_stderr.append(f"Failed to pull {remote_path}: {result.stderr}")
                last_result = RemoteResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                )
            except subprocess.TimeoutExpired:
                all_stderr.append(f"SCP timed out pulling {remote_path}")
                last_result = RemoteResult(stdout="", stderr="SCP timeout", returncode=-1)
            except FileNotFoundError:
                all_stderr.append("SCP client not found")
                last_result = RemoteResult(stdout="", stderr="SCP not found", returncode=-2)
                break

        if all_stderr:
            return RemoteResult(
                stdout="",
                stderr="\n".join(all_stderr),
                returncode=1,
            )
        return last_result

    def dispatch_remote(
        self,
        task_file: str,
        dispatcher_args: str = "",
    ) -> RemoteResult:
        """Full remote dispatch cycle: push task, run dispatcher, pull result.

        Steps:
        1. Push task file to remote queue
        2. Run the dispatcher on the remote host
        3. Pull the result file back

        Args:
            task_file: Local path to the task JSON file.
            dispatcher_args: Additional args for the remote dispatcher.

        Returns:
            RemoteResult from the dispatcher execution.
        """
        task_path = Path(task_file)
        if not task_path.exists():
            return RemoteResult(
                stdout="",
                stderr=f"Task file not found: {task_file}",
                returncode=-3,
            )

        # Step 1: Push task to remote queue
        remote_queue = f"{self.remote_project_path}/.agents/queue/"
        push_result = self.push_files([str(task_path)], remote_dir=remote_queue)
        if not push_result.success:
            return RemoteResult(
                stdout="",
                stderr=f"Failed to push task to remote: {push_result.stderr}",
                returncode=push_result.returncode,
            )

        # Step 2: Run dispatcher on remote
        remote_cmd = (
            f"cd {self.remote_project_path} && "
            f"python scripts/agents/orchestrate.py dispatch {dispatcher_args}"
        )
        dispatch_result = self.run_remote(remote_cmd, timeout=600)
        if not dispatch_result.success:
            return dispatch_result

        # Step 3: Pull result back
        task_id = task_path.stem  # filename without .json
        remote_result_path = f"{self.remote_project_path}/.agents/results/{task_id}.json"
        local_results_dir = str(self._project_root / ".agents" / "results")
        pull_result = self.pull_files([remote_result_path], local_dir=local_results_dir)

        if not pull_result.success:
            # Dispatch succeeded but couldn't pull result — still return dispatch output
            return RemoteResult(
                stdout=dispatch_result.stdout,
                stderr=f"Dispatch OK but failed to pull result: {pull_result.stderr}",
                returncode=0,
            )

        return dispatch_result

    def check_remote_status(self) -> RemoteResult:
        """Check if the remote host is reachable and the project is set up.

        Runs basic checks:
        - SSH connectivity
        - Project directory exists
        - Python available
        - Agent tools available (claude, codex)

        Returns:
            RemoteResult with status information.
        """
        check_cmd = (
            f"echo 'SSH OK' && "
            f"test -d {self.remote_project_path} && echo 'Project dir OK' && "
            f"cd {self.remote_project_path} && "
            f"python3 --version && "
            f"which claude 2>/dev/null && echo 'claude OK' || echo 'claude NOT FOUND' && "
            f"which codex 2>/dev/null && echo 'codex OK' || echo 'codex NOT FOUND'"
        )
        return self.run_remote(check_cmd, timeout=30)

    def get_remote_queue_status(self) -> RemoteResult:
        """Get the status of the remote task queue.

        Returns:
            RemoteResult with queue file listing.
        """
        cmd = f"ls -la {self.remote_project_path}/.agents/queue/*.json 2>/dev/null || echo 'Queue empty'"
        return self.run_remote(cmd, timeout=15)
