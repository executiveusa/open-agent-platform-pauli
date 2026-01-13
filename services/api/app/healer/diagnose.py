from dataclasses import dataclass
from typing import Any


@dataclass
class FailureContext:
    error: str
    stack: str | None
    logs: list[str]
    last_tool_input: str | None
    screenshot_url: str | None
    metadata: dict[str, Any]


@dataclass
class RecoveryProposal:
    summary: str
    patch: str
    confidence: float


def propose_recovery(context: FailureContext) -> RecoveryProposal:
    summary = "Review the last tool input and retry the failed step with updated parameters."
    patch = """--- a/README.md\n+++ b/README.md\n@@\n-Placeholder\n+Placeholder"""
    return RecoveryProposal(summary=summary, patch=patch, confidence=0.42)
