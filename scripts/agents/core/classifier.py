"""Task Complexity Classifier for 9ake-kiro-agents.

Classifies user requests as 'small' (auto-dispatch immediately) or
'large' (present plan first, wait for user approval).

Heuristics:
- Small: single-file, simple verbs, short descriptions, clear scope
- Large: multi-file, architecture words, complex scope, design tasks
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ClassificationResult:
    """Result of classifying a task's complexity."""

    size: str  # "small" or "large"
    confidence: float  # 0.0 to 1.0
    reason: str  # Human-readable explanation

    @property
    def is_small(self) -> bool:
        return self.size == "small"

    @property
    def is_large(self) -> bool:
        return self.size == "large"


# Indicators that suggest a LARGE task
LARGE_INDICATORS = [
    # Architecture / redesign words
    r"\b(redesign|restructure|overhaul|architect|rearchitect)\b",
    r"\b(refactor\s+(the\s+)?entire|refactor\s+(all|everything))\b",
    r"\b(rewrite|rebuild)\s+(the\s+)?(system|architecture|codebase)\b",
    # Scope words
    r"\b(entire|all\s+\w+s|every|whole|system-wide|across\s+all)\b",
    r"\b(multiple\s+(files|modules|components|services))\b",
    # Design / planning
    r"\b(design\s+(a\s+)?new\s+(system|architecture|framework))\b",
    r"\b(create\s+(a\s+)?new\s+(system|framework|platform))\b",
    # Migration
    r"\b(migrat(e|ion)|convert\s+all|upgrade\s+all)\b",
]

# Indicators that suggest a SMALL task
SMALL_INDICATORS = [
    # Single-file verbs
    r"\b(fix|patch|typo|rename|update|tweak)\b",
    r"\b(add\s+(a|one|the)\s+\w+)\b",
    r"\b(implement|create|write)\s+(a\s+)?(\w+\.)?(py|ts|js|md|yaml|json)\b",
    # Scoped to one thing
    r"\b(in\s+\w+\.(py|ts|js|md))\b",
    r"\b(the\s+\w+\s+(function|method|class|test|file))\b",
    # Quick / simple
    r"\b(quick(ly)?|just|simply|small)\b",
]

# File extensions that help identify single-file scope
FILE_PATTERN = re.compile(r"\b[\w/]+\.\w{1,5}\b")


def classify_task(
    description: str,
    expected_outputs: Optional[List[str]] = None,
) -> ClassificationResult:
    """Classify a task as 'small' or 'large'.

    Args:
        description: The user's task description.
        expected_outputs: Expected output files (if known).

    Returns:
        ClassificationResult with size, confidence, and reason.
    """
    description_lower = description.lower().strip()

    # Score accumulators
    small_score = 0.0
    large_score = 0.0
    reasons: List[str] = []

    # Check large indicators
    for pattern in LARGE_INDICATORS:
        if re.search(pattern, description_lower):
            large_score += 2.0
            match = re.search(pattern, description_lower)
            if match:
                reasons.append(f"complex scope: '{match.group()}'")
            break  # One strong signal is enough

    # Check small indicators
    for pattern in SMALL_INDICATORS:
        if re.search(pattern, description_lower):
            small_score += 1.5
            match = re.search(pattern, description_lower)
            if match:
                reasons.append(f"simple scope: '{match.group()}'")
            break

    # Heuristic: description length
    if len(description) < 100:
        small_score += 1.0
        reasons.append("short description (<100 chars)")
    elif len(description) > 300:
        large_score += 1.5
        reasons.append("long description (>300 chars)")
    elif len(description) > 200:
        large_score += 0.5
        reasons.append("moderate description length")

    # Heuristic: file count in expected outputs
    if expected_outputs:
        if len(expected_outputs) <= 1:
            small_score += 1.5
            reasons.append(f"single expected output")
        else:
            large_score += 1.5
            reasons.append(f"{len(expected_outputs)} expected outputs")

    # Heuristic: number of files mentioned in description
    files_mentioned = FILE_PATTERN.findall(description)
    # Filter out things that aren't really files (e.g., "v1.0")
    files_mentioned = [f for f in files_mentioned if not re.match(r"v?\d+\.\d+", f)]
    if len(files_mentioned) == 1:
        small_score += 1.0
        reasons.append(f"mentions 1 file: {files_mentioned[0]}")
    elif len(files_mentioned) >= 3:
        large_score += 1.0
        reasons.append(f"mentions {len(files_mentioned)} files")

    # Heuristic: task type keywords
    if re.search(r"\b(implement|create|write|add)\s+\w+", description_lower):
        # Could be small or large — depends on other signals
        if not re.search(r"\b(system|architecture|framework|platform)\b", description_lower):
            small_score += 0.5
        else:
            large_score += 1.0
            reasons.append("mentions system/architecture/framework")

    # Decision
    total = small_score + large_score
    if total == 0:
        # No strong signals — default to small with low confidence
        return ClassificationResult(
            size="small",
            confidence=0.5,
            reason="No strong complexity signals; defaulting to small",
        )

    if small_score > large_score:
        confidence = min(small_score / (total + 1.0), 0.95)
        return ClassificationResult(
            size="small",
            confidence=confidence,
            reason="; ".join(reasons[:3]) if reasons else "Simple task",
        )
    else:
        confidence = min(large_score / (total + 1.0), 0.95)
        return ClassificationResult(
            size="large",
            confidence=confidence,
            reason="; ".join(reasons[:3]) if reasons else "Complex task",
        )


def select_agent_type(description: str) -> str:
    """Determine which agent type is best for a task.

    Args:
        description: Task description.

    Returns:
        Task type: 'reasoning', 'design', 'review', 'implementation', 'test', or 'refactor'.
    """
    desc_lower = description.lower()

    # Design / architecture
    if re.search(r"\b(design|architect|plan|propose|interface)\b", desc_lower):
        return "design"

    # Reasoning (check before review — 'analyze and decide' is reasoning not review)
    if re.search(r"\b(reason|think|compare|decide|explain\s+why|which\s+approach)\b", desc_lower):
        return "reasoning"

    # Review
    if re.search(r"\b(review|audit|check|analyze|evaluate)\b", desc_lower):
        return "review"

    # Test
    if re.search(r"\b(test|write\s+tests?|add\s+tests?|coverage)\b", desc_lower):
        return "test"

    # Refactor
    if re.search(r"\b(refactor|restructure|clean\s*up|reorganize)\b", desc_lower):
        return "refactor"

    # Default: implementation
    return "implementation"
