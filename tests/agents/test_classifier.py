"""Tests for the Task Complexity Classifier."""

import pytest

from scripts.agents.core.classifier import ClassificationResult, classify_task, select_agent_type


class TestClassifySmallTasks:
    """Tasks that should be classified as 'small'."""

    def test_fix_typo(self):
        result = classify_task("fix the typo in utils.py")
        assert result.is_small

    def test_implement_single_file(self):
        result = classify_task("implement score_product.py")
        assert result.is_small

    def test_add_function(self):
        result = classify_task("add a validate_score function to the scorer")
        assert result.is_small

    def test_rename_variable(self):
        result = classify_task("rename getUserName to getUsername")
        assert result.is_small

    def test_update_file(self):
        result = classify_task("update the config.yaml with new settings")
        assert result.is_small

    def test_short_description(self):
        result = classify_task("fix the bug")
        assert result.is_small

    def test_single_expected_output(self):
        result = classify_task(
            "create the scoring module",
            expected_outputs=["scripts/dev/score_product.py"],
        )
        assert result.is_small

    def test_quick_task(self):
        result = classify_task("just add a docstring to the main function")
        assert result.is_small

    def test_write_specific_file(self):
        result = classify_task("write tests/test_score_product.py with threshold tests")
        assert result.is_small


class TestClassifyLargeTasks:
    """Tasks that should be classified as 'large'."""

    def test_redesign_system(self):
        result = classify_task("redesign the entire scoring architecture")
        assert result.is_large

    def test_refactor_everything(self):
        result = classify_task("refactor all agents to use the new plugin system")
        assert result.is_large

    def test_multiple_expected_outputs(self):
        result = classify_task(
            "create the scoring system",
            expected_outputs=["score.py", "validator.py", "reporter.py"],
        )
        assert result.is_large

    def test_migrate(self):
        result = classify_task("migrate the entire codebase from callbacks to async/await")
        assert result.is_large

    def test_overhaul(self):
        result = classify_task("overhaul the agent dispatch system")
        assert result.is_large

    def test_restructure(self):
        result = classify_task("restructure the project to separate core from plugins")
        assert result.is_large

    def test_long_description(self):
        long_desc = (
            "I need you to create a new module system that supports plugins, "
            "dynamic loading, hot reloading, and a registry. It should work with "
            "the existing agent system and integrate with the orchestrator. "
            "Also add tests for each component and update the documentation. "
            "Make sure it's backward compatible with the current system."
        )
        result = classify_task(long_desc)
        assert result.is_large

    def test_create_new_system(self):
        result = classify_task("design a new system architecture for multi-tenant support")
        assert result.is_large


class TestClassificationResult:
    """Tests for the result dataclass."""

    def test_confidence_range(self):
        result = classify_task("implement score.py")
        assert 0.0 <= result.confidence <= 1.0

    def test_has_reason(self):
        result = classify_task("fix typo in main.py")
        assert len(result.reason) > 0

    def test_is_small_property(self):
        r = ClassificationResult(size="small", confidence=0.8, reason="test")
        assert r.is_small
        assert not r.is_large

    def test_is_large_property(self):
        r = ClassificationResult(size="large", confidence=0.8, reason="test")
        assert r.is_large
        assert not r.is_small


class TestSelectAgentType:
    """Tests for agent type selection."""

    def test_design(self):
        assert select_agent_type("design the scoring interface") == "design"

    def test_review(self):
        assert select_agent_type("review the pull request") == "review"

    def test_test(self):
        assert select_agent_type("write tests for the parser") == "test"

    def test_refactor(self):
        assert select_agent_type("refactor the dispatcher module") == "refactor"

    def test_implementation_default(self):
        assert select_agent_type("implement scoring script") == "implementation"

    def test_build_is_implementation(self):
        assert select_agent_type("build the report generator") == "implementation"

    def test_reasoning(self):
        assert select_agent_type("analyze and decide which approach is better") == "reasoning"


class TestEdgeCases:
    """Edge cases for the classifier."""

    def test_empty_string(self):
        result = classify_task("")
        assert result.size in ("small", "large")
        assert result.confidence <= 0.6

    def test_ambiguous_defaults_to_small(self):
        result = classify_task("do the thing")
        assert result.is_small
        assert result.confidence < 0.7

    def test_none_outputs(self):
        result = classify_task("fix bug", expected_outputs=None)
        assert result.is_small
