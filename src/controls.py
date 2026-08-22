from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlDecision:
    """Deterministic decision returned by a simulated control."""

    control: str
    response: str
    terminal_state: str | None


def evaluate_evidence_gate(evidence_state: str) -> ControlDecision:
    """
    Evaluate evidence availability/quality.

    This is a bounded deterministic simulation rule, not an empirical
    evidence-verification system.
    """

    valid_states = {
        "SUPPORTED",
        "MISSING",
        "STALE",
        "UNSUPPORTED",
        "CONTAMINATED",
    }

    if evidence_state not in valid_states:
        raise ValueError(
            f"Unknown evidence state: {evidence_state!r}"
        )

    if evidence_state == "SUPPORTED":
        return ControlDecision(
            control="EVIDENCE_GATE",
            response="ALLOW",
            terminal_state=None,
        )

    if evidence_state == "MISSING":
        return ControlDecision(
            control="EVIDENCE_GATE",
            response="ESCALATE",
            terminal_state="ESCALATED",
        )

    return ControlDecision(
        control="EVIDENCE_GATE",
        response="BLOCK",
        terminal_state="BLOCKED",
    )


def evaluate_safety_guard(
    fault_type: str,
) -> ControlDecision:
    """
    Evaluate the two bounded v1.0 safety conditions.

    No real infrastructure permission check is performed.
    """

    if fault_type == "FALSE_VERIFICATION":
        return ControlDecision(
            control="SAFETY_GUARD",
            response="BLOCK",
            terminal_state="BLOCKED",
        )

    if fault_type == "OVER_PERMISSIONED_ACTION":
        return ControlDecision(
            control="SAFETY_GUARD",
            response="REQUIRE_HUMAN_APPROVAL",
            terminal_state="HUMAN_APPROVAL_REQUIRED",
        )

    return ControlDecision(
        control="SAFETY_GUARD",
        response="ALLOW",
        terminal_state=None,
    )