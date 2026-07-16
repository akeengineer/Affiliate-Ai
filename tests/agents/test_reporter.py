"""Tests for the Report Generator."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.result import AgentResult
from scripts.agents.core.reporter import Reporter


MINIMAL_CONFIG = {
    "project_name": "Test Project",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {"command": "claude", "flags": [], "task_types": ["reasoning"]},
        "codex": {"command": "codex", "flags": [], "task_types": ["implementation"]},
    },
    "dispatch": {"retry_max": 2, "parallel_max": 2},
    "ssh": {"host": ""},
    "validation": {"run_tests": True},
    "paths": {
        "queue": ".agents/queue",
        "results": ".agents/results",
        "state": ".agents/state",
        "reports": ".agents/reports",
        "prompts": ".agents/prompts",
        "schemas": ".agents/schemas",
    },
}


@pytest.fixture
def project_dir(tmp_path):
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports"]:
        (agents_dir / sub).mkdir()
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


@pytest.fixture
def reporter(config):
    return Reporter(config)


@pytest.fixture
def sample_results():
    """Create a mix of sample results."""
    return [
        AgentResult.create(
            task_id="11111111-1111-1111-1111-111111111111",
            agent="codex",
            status="success",
            summary="Implemented scoring script",
            duration_seconds=45.2,
            files_created=["scripts/dev/score_product.py"],
            files_modified=[],
            tests_run="python -m pytest tests/",
            tests_passed=True,
        ),
        AgentResult.create(
            task_id="22222222-2222-2222-2222-222222222222",
            agent="claude",
            status="success",
            summary="Designed the interface",
            duration_seconds=12.8,
            next_steps=["Implement the designed interface"],
        ),
        AgentResult.create(
            task_id="33333333-3333-3333-3333-333333333333",
            agent="codex",
            status="fail",
            summary="Could not find input file",
            duration_seconds=5.0,
            errors=["FileNotFoundError: vault/samples/product.md"],
            attempt=2,
        ),
        AgentResult.create(
            task_id="44444444-4444-4444-4444-444444444444",
            agent="claude",
            status="success",
            summary="Fallback review completed",
            duration_seconds=20.0,
            is_fallback=True,
        ),
    ]


class TestGenerateMarkdown:
    """Tests for Markdown report generation."""

    def test_generates_markdown_with_results(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "# Orchestration Report" in md
        assert "Test Project" in md
        assert "Total tasks:** 4" in md

    def test_contains_summary_table(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "| Success | 3 |" in md
        assert "| Failed | 1 |" in md

    def test_contains_agent_utilization(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "**codex**" in md
        assert "**claude**" in md
        assert "Fallback executions: 1" in md

    def test_contains_task_details(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "Implemented scoring script" in md
        assert "Designed the interface" in md
        assert "Could not find input file" in md
        assert "FileNotFoundError" in md

    def test_contains_files_info(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "scripts/dev/score_product.py" in md

    def test_contains_test_info(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "python -m pytest tests/" in md
        assert "PASSED" in md

    def test_contains_performance(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results)
        assert "Total execution time:" in md
        assert "Average per task:" in md

    def test_empty_results(self, reporter):
        md = reporter.generate_markdown([])
        assert "No results to report" in md

    def test_custom_title(self, reporter, sample_results):
        md = reporter.generate_markdown(sample_results, title="Weekly Run")
        assert "# Weekly Run" in md


class TestGenerateSummary:
    """Tests for JSON summary generation."""

    def test_summary_structure(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert summary["project_name"] == "Test Project"
        assert summary["total_tasks"] == 4
        assert "generated_at" in summary

    def test_status_counts(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert summary["status_counts"]["success"] == 3
        assert summary["status_counts"]["fail"] == 1

    def test_agent_utilization(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert summary["agent_utilization"]["codex"] == 2
        assert summary["agent_utilization"]["claude"] == 2

    def test_fallback_count(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert summary["fallback_count"] == 1

    def test_duration_stats(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert summary["total_duration_seconds"] == pytest.approx(83.0, abs=0.1)
        assert summary["average_duration_seconds"] == pytest.approx(20.75, abs=0.1)

    def test_files_collected(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert "scripts/dev/score_product.py" in summary["files_created"]

    def test_errors_collected(self, reporter, sample_results):
        summary = reporter.generate_summary(sample_results)
        assert len(summary["all_errors"]) == 1
        assert summary["all_errors"][0]["task_id"] == "33333333-3333-3333-3333-333333333333"

    def test_empty_results_summary(self, reporter):
        summary = reporter.generate_summary([])
        assert summary["total_tasks"] == 0
        assert summary["average_duration_seconds"] == 0.0


class TestSaveToDisk:
    """Tests for report persistence."""

    def test_generate_saves_markdown(self, reporter, sample_results, project_dir):
        path = reporter.generate(sample_results, title="Test Report")
        assert path.exists()
        assert path.suffix == ".md"
        content = path.read_text(encoding="utf-8")
        assert "# Test Report" in content

    def test_generate_saves_json_summary(self, reporter, sample_results, project_dir):
        md_path = reporter.generate(sample_results)
        json_path = md_path.with_name(md_path.stem.replace("-report", "-summary") + ".json")
        assert json_path.exists()
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["total_tasks"] == 4

    def test_generate_loads_from_disk(self, reporter, sample_results, project_dir):
        # Save results to disk first
        results_dir = project_dir / ".agents" / "results"
        for result in sample_results:
            result.save(results_dir)

        # Generate without passing results (should load from disk)
        path = reporter.generate()
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Total tasks:** 4" in content

    def test_reports_dir_created(self, config, project_dir):
        # Remove reports dir
        reports_dir = project_dir / ".agents" / "reports"
        import shutil
        shutil.rmtree(reports_dir)

        reporter = Reporter(config)
        path = reporter.generate([])
        assert path.exists()
        assert reports_dir.exists()
