"""Configuration loader and dataclasses for 9ake-kiro-agents."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class AgentConfig:
    """Configuration for a single CLI agent (Claude or Codex)."""

    name: str
    command: str
    flags: List[str] = field(default_factory=list)
    system_prompt: str = ""
    max_turns: Optional[int] = None
    max_budget_usd: Optional[float] = None
    task_types: List[str] = field(default_factory=list)
    fallback_to: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "AgentConfig":
        """Create AgentConfig from a config dictionary."""
        return cls(
            name=name,
            command=data.get("command", name),
            flags=data.get("flags", []),
            system_prompt=data.get("system_prompt", ""),
            max_turns=data.get("max_turns"),
            max_budget_usd=data.get("max_budget_usd"),
            task_types=data.get("task_types", []),
            fallback_to=data.get("fallback_to"),
        )


@dataclass
class DispatchConfig:
    """Configuration for task dispatch behavior."""

    retry_max: int = 2
    retry_backoff_seconds: List[int] = field(default_factory=lambda: [5, 15])
    fallback_enabled: bool = True
    parallel_max: int = 2
    default_timeout_seconds: int = 300

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DispatchConfig":
        """Create DispatchConfig from a config dictionary."""
        return cls(
            retry_max=data.get("retry_max", 2),
            retry_backoff_seconds=data.get("retry_backoff_seconds", [5, 15]),
            fallback_enabled=data.get("fallback_enabled", True),
            parallel_max=data.get("parallel_max", 2),
            default_timeout_seconds=data.get("default_timeout_seconds", 300),
        )


@dataclass
class SSHConfig:
    """Configuration for SSH remote execution."""

    host: str = ""
    project_path: str = ""
    user: str = "ubuntu"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SSHConfig":
        """Create SSHConfig from a config dictionary."""
        return cls(
            host=data.get("host", ""),
            project_path=data.get("project_path", ""),
            user=data.get("user", "ubuntu"),
        )

    @property
    def ssh_target(self) -> str:
        """Return user@host string for SSH commands."""
        if self.user:
            return f"{self.user}@{self.host}"
        return self.host


@dataclass
class ValidationConfig:
    """Configuration for result validation."""

    run_tests: bool = True
    test_command: str = "python -m pytest"
    check_files_exist: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationConfig":
        """Create ValidationConfig from a config dictionary."""
        return cls(
            run_tests=data.get("run_tests", True),
            test_command=data.get("test_command", "python -m pytest"),
            check_files_exist=data.get("check_files_exist", True),
        )


@dataclass
class PathsConfig:
    """Configuration for directory paths."""

    queue: str = ".agents/queue"
    results: str = ".agents/results"
    state: str = ".agents/state"
    reports: str = ".agents/reports"
    prompts: str = ".agents/prompts"
    schemas: str = ".agents/schemas"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PathsConfig":
        """Create PathsConfig from a config dictionary."""
        return cls(
            queue=data.get("queue", ".agents/queue"),
            results=data.get("results", ".agents/results"),
            state=data.get("state", ".agents/state"),
            reports=data.get("reports", ".agents/reports"),
            prompts=data.get("prompts", ".agents/prompts"),
            schemas=data.get("schemas", ".agents/schemas"),
        )

    def resolve(self, project_root: Path) -> "PathsConfig":
        """Return a new PathsConfig with paths resolved against project root."""
        return PathsConfig(
            queue=str(project_root / self.queue),
            results=str(project_root / self.results),
            state=str(project_root / self.state),
            reports=str(project_root / self.reports),
            prompts=str(project_root / self.prompts),
            schemas=str(project_root / self.schemas),
        )


@dataclass
class ProjectConfig:
    """Top-level project configuration loaded from .agents/config.yaml."""

    project_name: str = ""
    package_name: str = "9ake-kiro-agents"
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    dispatch: DispatchConfig = field(default_factory=DispatchConfig)
    ssh: SSHConfig = field(default_factory=SSHConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    config_path: Optional[Path] = None
    project_root: Optional[Path] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], config_path: Optional[Path] = None) -> "ProjectConfig":
        """Create ProjectConfig from a parsed YAML dictionary."""
        agents_data = data.get("agents", {})
        agents = {
            name: AgentConfig.from_dict(name, agent_data)
            for name, agent_data in agents_data.items()
        }

        project_root = config_path.parent.parent if config_path else None

        return cls(
            project_name=data.get("project_name", ""),
            package_name=data.get("package_name", "9ake-kiro-agents"),
            agents=agents,
            dispatch=DispatchConfig.from_dict(data.get("dispatch", {})),
            ssh=SSHConfig.from_dict(data.get("ssh", {})),
            validation=ValidationConfig.from_dict(data.get("validation", {})),
            paths=PathsConfig.from_dict(data.get("paths", {})),
            config_path=config_path,
            project_root=project_root,
        )

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "ProjectConfig":
        """Load configuration from a YAML file.

        If no path is given, searches upward from CWD for .agents/config.yaml.

        Args:
            config_path: Explicit path to config.yaml, or None for auto-discovery.

        Returns:
            Loaded ProjectConfig instance.

        Raises:
            FileNotFoundError: If no config file is found.
            yaml.YAMLError: If config file is invalid YAML.
        """
        if config_path:
            path = Path(config_path)
        else:
            path = cls._discover_config()

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid config format in {path}: expected YAML mapping")

        return cls.from_dict(data, config_path=path.resolve())

    @classmethod
    def _discover_config(cls) -> Path:
        """Search upward from CWD to find .agents/config.yaml.

        Returns:
            Path to the discovered config file.

        Raises:
            FileNotFoundError: If no config file is found in any parent.
        """
        current = Path.cwd()
        while True:
            candidate = current / ".agents" / "config.yaml"
            if candidate.exists():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent
        raise FileNotFoundError(
            "No .agents/config.yaml found in current directory or any parent. "
            "Run 'orchestrate init' to create one."
        )

    def get_agent_for_task_type(self, task_type: str) -> Optional[AgentConfig]:
        """Find the agent configured to handle a given task type.

        Args:
            task_type: The task type string (e.g., 'implementation', 'reasoning').

        Returns:
            The matching AgentConfig or None if no agent handles this type.
        """
        for agent in self.agents.values():
            if task_type in agent.task_types:
                return agent
        return None

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get a specific agent by name.

        Args:
            name: Agent name (e.g., 'claude', 'codex').

        Returns:
            AgentConfig or None.
        """
        return self.agents.get(name)

    def get_fallback_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Get the fallback agent for a given agent.

        Args:
            agent_name: Name of the agent that failed.

        Returns:
            The fallback AgentConfig or None.
        """
        agent = self.agents.get(agent_name)
        if agent and agent.fallback_to:
            return self.agents.get(agent.fallback_to)
        return None
