"""Report Generator for 9ake-kiro-agents.

Generates Markdown and JSON summary reports from orchestration results.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus


class Reporter:
    """Generates orchestration reports from collected results.

    Produces:
    - Markdown report for human reading (and Obsidian compatibility)
    - JSON summary for programmatic consumption
    """

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize reporter.

        Args:
            config: Project configuration.
        """
        self.config = config
        self._project_root = config.project_root or Path.cwd()

    def generate(
        self,
        results: Optional[List[AgentResult]] = None,
        title: Optional[str] = None,
    ) -> Path:
        """Generate a full report and save to disk.

        Args:
            results: Results to report on. If None, loads from disk.
            title: Optional report title.

        Returns:
            Path to the generated Markdown report.
        """
        if results is None:
            results = self._load_results()

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        report_title = title or f"Orchestration Report {timestamp}"

        markdown = self.generate_markdown(results, report_title)
        summary = self.generate_summary(results)

        # Save markdown
        reports_dir = self._project_root / self.config.paths.reports
        reports_dir.mkdir(parents=True, exist_ok=True)

        md_path = reports_dir / f"{timestamp}-report.md"
        md_path.write_text(markdown, encoding="utf-8")

        # Save JSON summary
        json_path = reports_dir / f"{timestamp}-summary.json"
        json_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        return md_path

    def generate_markdown(
        self,
        results: List[AgentResult],
        title: str = "Orchestration Report",
    ) -> str:
        """Generate a Markdown report from results.

        Args:
            results: List of agent results.
            title: Report title.

        Returns:
            Markdown string.
        """
        lines: List[str] = []
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Header
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"**Generated:** {timestamp}")
        lines.append(f"**Project:** {self.config.project_name}")
        lines.append(f"**Total tasks:** {len(results)}")
        lines.append("")

        if not results:
            lines.append("No results to report.")
            return "\n".join(lines)

        # Summary section
        lines.append("## Summary")
        lines.append("")

        succeeded = sum(1 for r in results if r.status == ResultStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == ResultStatus.FAIL)
        partial = sum(1 for r in results if r.status == ResultStatus.PARTIAL)
        timeout = sum(1 for r in results if r.status == ResultStatus.TIMEOUT)

        lines.append(f"| Status | Count |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Success | {succeeded} |")
        lines.append(f"| Failed | {failed} |")
        lines.append(f"| Partial | {partial} |")
        lines.append(f"| Timeout | {timeout} |")
        lines.append("")

        # Agent utilization
        lines.append("## Agent Utilization")
        lines.append("")

        agent_counts = Counter(r.agent for r in results)
        for agent_name, count in agent_counts.most_common():
            agent_success = sum(1 for r in results if r.agent == agent_name and r.is_success)
            lines.append(f"- **{agent_name}**: {count} task(s), {agent_success} succeeded")

        fallback_count = sum(1 for r in results if r.is_fallback)
        if fallback_count:
            lines.append(f"- Fallback executions: {fallback_count}")
        lines.append("")

        # Task details
        lines.append("## Task Details")
        lines.append("")

        for result in results:
            status_emoji = {"success": "+", "fail": "x", "partial": "~", "timeout": "!"}
            icon = status_emoji.get(result.status.value, "?")
            fallback_tag = " (fallback)" if result.is_fallback else ""

            lines.append(f"### [{icon}] {result.task_id[:8]}...{fallback_tag}")
            lines.append("")
            lines.append(f"- **Agent:** {result.agent}")
            lines.append(f"- **Status:** {result.status.value}")
            lines.append(f"- **Attempt:** {result.attempt}")
            lines.append(f"- **Duration:** {result.duration_seconds:.1f}s")
            lines.append(f"- **Summary:** {result.summary}")

            if result.files_modified:
                lines.append(f"- **Files modified:** {', '.join(result.files_modified)}")
            if result.files_created:
                lines.append(f"- **Files created:** {', '.join(result.files_created)}")
            if result.tests_run:
                passed_text = "PASSED" if result.tests_passed else "FAILED"
                lines.append(f"- **Tests:** `{result.tests_run}` -> {passed_text}")
            if result.errors:
                lines.append("- **Errors:**")
                for err in result.errors:
                    lines.append(f"  - {err}")
            if result.next_steps:
                lines.append("- **Next steps:**")
                for step in result.next_steps:
                    lines.append(f"  - {step}")
            lines.append("")

        # Duration stats
        total_duration = sum(r.duration_seconds for r in results)
        lines.append("## Performance")
        lines.append("")
        lines.append(f"- **Total execution time:** {total_duration:.1f}s")
        if results:
            avg_duration = total_duration / len(results)
            lines.append(f"- **Average per task:** {avg_duration:.1f}s")
        lines.append("")

        return "\n".join(lines)

    def generate_summary(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Generate a JSON-serializable summary from results.

        Args:
            results: List of agent results.

        Returns:
            Dictionary with summary data.
        """
        agent_counts = Counter(r.agent for r in results)
        status_counts = Counter(r.status.value for r in results)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_name": self.config.project_name,
            "total_tasks": len(results),
            "status_counts": dict(status_counts),
            "agent_utilization": dict(agent_counts),
            "fallback_count": sum(1 for r in results if r.is_fallback),
            "total_duration_seconds": sum(r.duration_seconds for r in results),
            "average_duration_seconds": (
                sum(r.duration_seconds for r in results) / len(results)
                if results else 0.0
            ),
            "files_modified": sorted(set(
                f for r in results for f in r.files_modified
            )),
            "files_created": sorted(set(
                f for r in results for f in r.files_created
            )),
            "all_errors": [
                {"task_id": r.task_id, "errors": r.errors}
                for r in results if r.errors
            ],
            "results": [r.to_dict() for r in results],
        }

    def _load_results(self) -> List[AgentResult]:
        """Load all results from disk.

        Returns:
            List of AgentResult objects.
        """
        results_dir = self._project_root / self.config.paths.results
        if not results_dir.exists():
            return []

        results = []
        for file_path in sorted(results_dir.glob("*.json")):
            try:
                result = AgentResult.load(file_path)
                results.append(result)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return results
