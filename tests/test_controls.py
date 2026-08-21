import pytest

from src.controls import (
    evaluate_evidence_gate,
    evaluate_safety_guard,
)


@pytest.mark.parametrize(
    ("evidence_state", "response", "terminal_state"),
    [
        ("SUPPORTED", "ALLOW", None),
        ("MISSING", "ESCALATE", "ESCALATED"),
        ("STALE", "BLOCK", "BLOCKED"),
        ("UNSUPPORTED", "BLOCK", "BLOCKED"),
        ("CONTAMINATED", "BLOCK", "BLOCKED"),
    ],
)
def test_evidence_gate(
    evidence_state,
    response,
    terminal_state,
):
    decision = evaluate_evidence_gate(evidence_state)

    assert decision.control == "EVIDENCE_GATE"
    assert decision.response == response
    assert decision.terminal_state == terminal_state


def test_evidence_gate_rejects_unknown_state():
    with pytest.raises(ValueError):
        evaluate_evidence_gate("UNKNOWN")


def test_safety_guard_blocks_false_verification():
    decision = evaluate_safety_guard("FALSE_VERIFICATION")

    assert decision.response == "BLOCK"
    assert decision.terminal_state == "BLOCKED"


def test_safety_guard_requires_human_for_overpermission():
    decision = evaluate_safety_guard("OVER_PERMISSIONED_ACTION")

    assert decision.response == "REQUIRE_HUMAN_APPROVAL"
    assert decision.terminal_state == "HUMAN_APPROVAL_REQUIRED"


def test_safety_guard_allows_other_fault_types():
    decision = evaluate_safety_guard("OTHER")

    assert decision.response == "ALLOW"
    assert decision.terminal_state is None
