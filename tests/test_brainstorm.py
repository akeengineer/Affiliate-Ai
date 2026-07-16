"""Phase 5 brainstorming and bounded-learning tests.

All Claude and notification boundaries are mocked; no external call is made.

Ref: codex/tasks/008-agent-brainstorming.md
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.agent_runner import read_note
from scripts.agents.approval_handler import handle_approval
from scripts.agents.brainstorm import DISCUSSION_AGENTS, run_brainstorm
from scripts.agents.learn_from_results import (
    adjust_weights,
    learn_from_results,
    load_learning_config,
)
from scripts.agents.propose_idea import extract_ideas, propose_ideas


TIMESTAMP = "2026-07-16T00:00:00Z"
PRODUCT_ID = "prod-learning-lamp"


class SequentialRunner:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, Any, dict[str, Any]]] = []

    def run(
        self,
        agent_name: str,
        instructions: str,
        context: Any,
        output_schema: dict[str, Any],
    ) -> dict[str, Any]:
        self.calls.append((agent_name, instructions, context, output_schema))
        if not self.responses:
            raise AssertionError("Unexpected extra Claude call")
        return self.responses.pop(0)


class FakeNotifier:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def send_all(self, message_type: str, content: dict[str, Any]) -> list[Any]:
        self.calls.append((message_type, content))
        return []


def _write_markdown(path: Path, frontmatter: dict[str, Any], body: str = "# Test\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{payload}\n---\n\n{body}", encoding="utf-8")
    return path


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    root = tmp_path / "vault"
    _write_markdown(
        root / "products" / f"{PRODUCT_ID}.md",
        {
            "type": "product_candidate",
            "product_id": PRODUCT_ID,
            "product_name": "Learning Lamp",
            "marketplace": "Shopee Thailand",
            "currency": "THB",
            "niche": "gadgets",
            "search_keywords": ["adjustable desk lamp"],
            "demand_score": 90,
            "trend_velocity_score": 82,
            "marketplace_rank_score": 75,
            "commission_score": 30,
            "content_fit_score": 80,
            "competition_gap_score": 68,
            "risk_score": 20,
            "product_opportunity_score": 60,
            "actual_performance_score": 90,
            "created_at": TIMESTAMP,
            "updated_at": TIMESTAMP,
            "status": "scored",
        },
        "# Learning Lamp\n\nSanitized historical evidence.\n",
    )
    return root


def _brainstorm_responses() -> list[dict[str, Any]]:
    responses: list[dict[str, Any]] = [
        {"question": "Which bounded discovery improvement should be tested next?"}
    ]
    for index, _agent in enumerate(DISCUSSION_AGENTS):
        responses.append(
            {
                "analysis": f"Specialist {index + 1} reviewed the supplied evidence.",
                "ideas": [],
            }
        )
    responses.append(
        {
            "summary": "The specialists support one keyword test and one gated niche proposal.",
            "ideas": [
                {
                    "idea_type": "search_keyword",
                    "title": "Test an adjustable-lamp keyword",
                    "rationale": (
                        "The successful product record contains this bounded search phrase."
                    ),
                    "expected_impact": "One additional candidate set for comparison.",
                    "proposed_action": "Add the keyword to the next gadgets scan.",
                    "target_niche": "gadgets",
                    "target_keyword": "adjustable desk lamp",
                    "product_ids": [PRODUCT_ID],
                },
                {
                    "idea_type": "new_niche",
                    "title": "Evaluate the pets niche",
                    "rationale": "The meeting identified a research hypothesis, not authorization.",
                    "expected_impact": "A user-reviewed discovery experiment.",
                    "proposed_action": "Request user approval before activating pets.",
                    "target_niche": "pets",
                    "target_keyword": "",
                    "product_ids": [PRODUCT_ID],
                },
            ],
        }
    )
    return responses


def _make_meeting(vault: Path) -> tuple[Path, SequentialRunner]:
    runner = SequentialRunner(_brainstorm_responses())
    path = run_brainstorm(vault, "Improve the next scan", runner=runner)  # type: ignore[arg-type]
    return path, runner


def _proposal_note(vault: Path, proposal_id: str, **updates: Any) -> Path:
    frontmatter = {
        "type": "idea_proposal",
        "proposal_id": proposal_id,
        "meeting_id": "meeting-test",
        "idea_type": "workflow_change",
        "title": "Test proposal",
        "target_niche": "",
        "target_keyword": "",
        "requires_user_approval": True,
        "approval_status": "pending",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "status": "pending_review",
        **updates,
    }
    return _write_markdown(vault / "proposals" / f"{proposal_id}.md", frontmatter)


def test_brainstorm_multi_agent_flow(vault: Path) -> None:
    _meeting, runner = _make_meeting(vault)

    assert len(runner.calls) == len(DISCUSSION_AGENTS) + 2
    assert runner.calls[0][0] == "Brainstorm Chairman"
    assert [call[0] for call in runner.calls[1:-1]] == [name for name, _ in DISCUSSION_AGENTS]
    assert runner.calls[-1][0] == "Brainstorm Chairman"
    for index, call in enumerate(runner.calls[1:-1]):
        assert len(call[2]["prior_responses"]) == index
    assert len(runner.calls[-1][2]["transcript"]) == len(DISCUSSION_AGENTS)
    assert runner.responses == []


def test_brainstorm_output_format(vault: Path) -> None:
    meeting_path, _runner = _make_meeting(vault)
    note = read_note(meeting_path)

    assert note.frontmatter["type"] == "agent_meeting"
    assert note.frontmatter["product_ids"] == [PRODUCT_ID]
    assert note.frontmatter["idea_count"] == 2
    assert note.frontmatter["created_at"].endswith("Z")
    assert note.frontmatter["updated_at"].endswith("Z")
    assert "## Chairman Question" in note.body
    assert "## Sequential Discussion" in note.body
    assert "## Chairman Synthesis" in note.body
    assert "explicit user approval" in note.body.lower()


def test_propose_idea_extraction(vault: Path) -> None:
    meeting_path, _runner = _make_meeting(vault)
    notifier = FakeNotifier()

    ideas = extract_ideas(meeting_path)
    paths = propose_ideas(meeting_path, vault_root=vault, notifier=notifier)

    assert len(ideas) == 2
    assert len(paths) == 2
    assert len(notifier.calls) == 2
    assert all(call[0] == "idea_proposal" for call in notifier.calls)
    keyword_proposal = read_note(paths[0])
    assert keyword_proposal.frontmatter["type"] == "idea_proposal"
    assert keyword_proposal.frontmatter["approval_status"] == "pending"
    assert keyword_proposal.frontmatter["requires_user_approval"] is True
    assert keyword_proposal.frontmatter["notification_status"] == "sent"
    assert "## Rationale" in keyword_proposal.body
    assert "## Expected Impact" in keyword_proposal.body
    assert "## Required Approval" in keyword_proposal.body


def test_learning_weight_adjustment(vault: Path) -> None:
    log_path = learn_from_results(vault)
    log = read_note(log_path)
    nightly = read_note(vault / "config" / "next-nightly-config.md")

    assert log.frontmatter["type"] == "learning_log"
    assert log.frontmatter["source_record_count"] == 1
    assert log.frontmatter["updated_weight_emphasis"]["demand_score"] > 1.0
    assert log.frontmatter["updated_weight_emphasis"]["commission_score"] < 1.0
    assert "adjustable desk lamp" in log.frontmatter["keyword_additions"]["gadgets"]
    assert nightly.frontmatter["type"] == "nightly_config"
    assert "adjustable desk lamp" in nightly.frontmatter["search_keywords"]["gadgets"]
    assert nightly.frontmatter["active_niches"] == [
        "gadgets",
        "home-office",
        "health-beauty",
    ]


def test_learning_bounds_enforcement() -> None:
    config = load_learning_config()
    current = {field: 1.0 for field in config["weight_bounds"]["fields"]}
    requested = {field: 500 if index % 2 == 0 else -500 for index, field in enumerate(current)}

    adjusted = adjust_weights(current, requested, config)

    for field, value in adjusted.items():
        assert 0.90 <= value <= 1.10
        assert abs(value - current[field]) <= current[field] * 0.10 + 1e-9
    assert set(adjusted.values()) == {0.9, 1.1}


def test_approval_handler_approve(vault: Path) -> None:
    proposal = _proposal_note(
        vault,
        "proposal-pets",
        idea_type="new_niche",
        title="Evaluate pets",
        target_niche="pets",
    )

    output = handle_approval(proposal, "approve", vault_root=vault)
    approved = read_note(output)
    nightly = read_note(vault / "config" / "next-nightly-config.md")

    assert approved.frontmatter["approval_status"] == "approved"
    assert approved.frontmatter["approval_actor"] == "user"
    assert approved.frontmatter["nightly_config_note"].endswith("next-nightly-config.md")
    assert "pets" in nightly.frontmatter["active_niches"]
    assert "proposal-pets" in nightly.frontmatter["approved_proposal_ids"]
    assert nightly.frontmatter["approved_ideas"][0]["proposal_id"] == "proposal-pets"


def test_approval_handler_reject(vault: Path) -> None:
    proposal = _proposal_note(vault, "proposal-reject")

    output = handle_approval(proposal, "reject", vault_root=vault)
    rejected = read_note(output)

    assert rejected.frontmatter["approval_status"] == "rejected"
    assert rejected.frontmatter["status"] == "rejected"
    assert "**rejected**" in rejected.body
    assert not (vault / "config" / "next-nightly-config.md").exists()
