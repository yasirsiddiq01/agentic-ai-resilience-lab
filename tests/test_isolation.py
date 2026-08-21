from src.isolation import (
    advance_trusted_context,
    create_clean_context,
    inject_fault,
    isolate_context,
    propagate_contaminated_context,
    restore_snapshot,
    snapshot_trusted_context,
)


def test_isolation_quarantines_fault_and_sanitizes_context():
    context = create_clean_context("User Report")
    context = advance_trusted_context(context, "Triage Agent")

    context = inject_fault(
        context,
        "INSTRUCTION_CONTAMINATION",
        "Triage Agent",
    )

    context = propagate_contaminated_context(
        context,
        "Log Analysis Agent",
    )

    result = isolate_context(
        context,
        "Log Analysis Agent",
    )

    assert result.quarantined.state == "QUARANTINED"
    assert result.sanitized.state == "SANITIZED"

    assert any(
        claim.startswith("fault:")
        for claim in result.quarantined.claims
    )

    assert not any(
        claim.startswith("fault:")
        for claim in result.sanitized.claims
    )


def test_rollback_restores_exact_last_trusted_state():
    context = create_clean_context("User Report")
    context = advance_trusted_context(context, "Triage Agent")
    context = advance_trusted_context(
        context,
        "Log Analysis Agent",
    )

    snapshot = snapshot_trusted_context(
        "Log Analysis Agent",
        context,
    )

    contaminated = advance_trusted_context(
        context,
        "Knowledge Agent",
    )

    contaminated = inject_fault(
        contaminated,
        "CONTEXT_CONTAMINATION",
        "Knowledge Agent",
    )

    restored = restore_snapshot(snapshot)

    assert restored.state == "RESTORED"
    assert restored.claims == snapshot.context.claims
    assert "processed:Knowledge Agent" not in restored.claims

    assert not any(
        claim.startswith("fault:")
        for claim in restored.claims
    )


def test_execution_can_resume_after_rollback():
    context = create_clean_context("User Report")
    context = advance_trusted_context(context, "Triage Agent")

    snapshot = snapshot_trusted_context(
        "Triage Agent",
        context,
    )

    restored = restore_snapshot(snapshot)

    resumed = advance_trusted_context(
        restored,
        "Log Analysis Agent",
    )

    assert resumed.state == "CLEAN"
    assert resumed.evidence_state == "SUPPORTED"
