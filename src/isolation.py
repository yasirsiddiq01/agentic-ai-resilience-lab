from __future__ import annotations

from dataclasses import dataclass


TRUSTED_CONTEXT_STATES = {
    "CLEAN",
    "SANITIZED",
    "RESTORED",
}


@dataclass(frozen=True)
class WorkflowContext:
    """
    Synthetic workflow context passed between stages.

    The payload is represented by deterministic claim markers.
    No live agent memory, LLM context, or production state is used.
    """

    claims: tuple[str, ...]
    evidence_state: str
    state: str
    source_stage: str


@dataclass(frozen=True)
class TrustedSnapshot:
    """Frozen copy of a trusted simulated workflow state."""

    stage: str
    context: WorkflowContext


@dataclass(frozen=True)
class IsolationResult:
    """Result of quarantining contaminated simulated context."""

    quarantined: WorkflowContext
    sanitized: WorkflowContext


def create_clean_context(
    stage_name: str,
) -> WorkflowContext:
    """Create the initial trusted synthetic context."""

    return WorkflowContext(
        claims=(f"processed:{stage_name}",),
        evidence_state="SUPPORTED",
        state="CLEAN",
        source_stage=stage_name,
    )


def advance_trusted_context(
    context: WorkflowContext,
    stage_name: str,
) -> WorkflowContext:
    """
    Deterministically advance trusted context to another stage.

    Contaminated or quarantined context cannot use this function.
    """

    if context.state not in TRUSTED_CONTEXT_STATES:
        raise ValueError(
            "Only trusted context can advance through the "
            "trusted-context path"
        )

    return WorkflowContext(
        claims=context.claims + (f"processed:{stage_name}",),
        evidence_state="SUPPORTED",
        state="CLEAN",
        source_stage=stage_name,
    )


def inject_fault(
    context: WorkflowContext,
    fault_type: str,
    source_stage: str,
) -> WorkflowContext:
    """Inject one explicit synthetic fault marker."""

    if context.state not in TRUSTED_CONTEXT_STATES:
        raise ValueError(
            "Fault injection requires a trusted starting context"
        )

    return WorkflowContext(
        claims=context.claims + (f"fault:{fault_type}",),
        evidence_state="CONTAMINATED",
        state="CONTAMINATED",
        source_stage=source_stage,
    )


def propagate_contaminated_context(
    context: WorkflowContext,
    stage_name: str,
) -> WorkflowContext:
    """Propagate already-contaminated synthetic context."""

    if context.state != "CONTAMINATED":
        raise ValueError(
            "Only contaminated context can use the "
            "contamination-propagation path"
        )

    return WorkflowContext(
        claims=context.claims,
        evidence_state=context.evidence_state,
        state="CONTAMINATED",
        source_stage=stage_name,
    )


def isolate_context(
    context: WorkflowContext,
    containment_stage: str,
) -> IsolationResult:
    """
    Quarantine contaminated context and construct a sanitized copy.

    Fault markers remain in the quarantined copy and are excluded
    from the sanitized downstream context.
    """

    if context.state != "CONTAMINATED":
        raise ValueError(
            "CASCADE isolation requires contaminated context"
        )

    fault_claims = tuple(
        claim
        for claim in context.claims
        if claim.startswith("fault:")
    )

    if not fault_claims:
        raise ValueError(
            "Contaminated context must contain a fault marker"
        )

    trusted_claims = tuple(
        claim
        for claim in context.claims
        if not claim.startswith("fault:")
    )

    quarantined = WorkflowContext(
        claims=context.claims,
        evidence_state=context.evidence_state,
        state="QUARANTINED",
        source_stage=containment_stage,
    )

    sanitized = WorkflowContext(
        claims=trusted_claims,
        evidence_state="SUPPORTED",
        state="SANITIZED",
        source_stage=containment_stage,
    )

    return IsolationResult(
        quarantined=quarantined,
        sanitized=sanitized,
    )


def snapshot_trusted_context(
    stage_name: str,
    context: WorkflowContext,
) -> TrustedSnapshot:
    """Capture an immutable trusted-state checkpoint."""

    if context.state not in TRUSTED_CONTEXT_STATES:
        raise ValueError(
            "Only trusted context can be snapshotted"
        )

    if context.evidence_state != "SUPPORTED":
        raise ValueError(
            "Trusted snapshot requires supported evidence"
        )

    return TrustedSnapshot(
        stage=stage_name,
        context=context,
    )


def restore_snapshot(
    snapshot: TrustedSnapshot,
) -> WorkflowContext:
    """
    Restore the exact trusted payload stored in a snapshot.

    The restored context contains no state introduced after
    the checkpoint.
    """

    return WorkflowContext(
        claims=snapshot.context.claims,
        evidence_state=snapshot.context.evidence_state,
        state="RESTORED",
        source_stage=snapshot.stage,
    )