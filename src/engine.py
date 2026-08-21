from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.agents import load_workflow
from src.controls import (
    ControlDecision,
    evaluate_evidence_gate,
    evaluate_safety_guard,
)
from src.isolation import (
    advance_trusted_context,
    create_clean_context,
    inject_fault,
    isolate_context,
    propagate_contaminated_context,
    restore_snapshot,
    snapshot_trusted_context,
)
from src.scenarios import load_scenarios
from src.tracing import TraceRecord


SUPPORTED_CONTROLS = {
    "NONE",
    "EVIDENCE_GATE",
    "SAFETY_GUARD",
    "CASCADE_ISOLATION",
    "CASCADE_ISOLATION_WITH_ROLLBACK",
}

STANDARD_CONTROL_POINTS = {
    "EVIDENCE_GATE": "Verification Agent",
    "SAFETY_GUARD": "Safety Agent",
}

CASCADE_CONTROLS = {
    "CASCADE_ISOLATION",
    "CASCADE_ISOLATION_WITH_ROLLBACK",
}


@dataclass(frozen=True)
class ExecutionResult:
    """Deterministic result of one scenario execution."""

    scenario_id: str
    trace: tuple[TraceRecord, ...]
    fault_reaches: tuple[str, ...]
    blast_radius: int
    propagation_depth: int
    containment_point: str | None
    control_response: str
    final_state: str
    rollback_to: str | None

    def to_summary(self) -> dict[str, Any]:
        """Return the evaluation-relevant result fields."""

        return {
            "scenario_id": self.scenario_id,
            "fault_reaches": list(self.fault_reaches),
            "blast_radius": self.blast_radius,
            "propagation_depth": self.propagation_depth,
            "containment_point": self.containment_point,
            "control_response": self.control_response,
            "final_state": self.final_state,
            "rollback_to": self.rollback_to,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable result including trace records."""

        result = asdict(self)

        result["trace"] = [
            record.to_dict()
            for record in self.trace
        ]

        result["fault_reaches"] = list(
            self.fault_reaches
        )

        return result


def get_scenario(
    scenario_id: str,
) -> dict[str, Any]:
    """Return one validated frozen scenario by ID."""

    registry = load_scenarios()

    for scenario in registry["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario

    raise KeyError(
        f"Unknown scenario ID: {scenario_id}"
    )


def evaluate_control(
    selected_control: str,
    evidence_state: str,
    fault_type: str,
) -> ControlDecision:
    """Evaluate one standard deterministic control."""

    if selected_control == "EVIDENCE_GATE":
        return evaluate_evidence_gate(
            evidence_state
        )

    if selected_control == "SAFETY_GUARD":
        return evaluate_safety_guard(
            fault_type
        )

    raise ValueError(
        f"Control {selected_control!r} "
        "has no standard evaluator"
    )


def _execute_standard_scenario(
    workflow: dict[str, Any],
    scenario: dict[str, Any],
) -> ExecutionResult:
    """Execute NONE, EvidenceGate, or Safety Guard."""

    scenario_id = scenario["id"]
    selected_control = scenario[
        "selected_control"
    ]

    stages = workflow["roles"]

    stage_names = [
        stage["name"]
        for stage in stages
    ]

    fault_type = scenario["fault_type"]
    fault_source = scenario["fault_source"]
    scenario_evidence = scenario[
        "evidence_state"
    ]

    has_fault = fault_type != "NONE"

    fault_index: int | None = None

    if has_fault:
        if fault_source is None:
            raise ValueError(
                f"{scenario_id}: fault_type is "
                f"{fault_type!r} but "
                "fault_source is null"
            )

        try:
            fault_index = stage_names.index(
                fault_source
            )
        except ValueError as exc:
            raise ValueError(
                f"{scenario_id}: fault source "
                f"{fault_source!r} is not in "
                "the canonical workflow"
            ) from exc

    control_point = STANDARD_CONTROL_POINTS.get(
        selected_control
    )

    trace: list[TraceRecord] = []
    fault_reaches: list[str] = []

    containment_point: str | None = None
    control_response = "NONE"

    final_state = (
        "FAILED_UNCONTAINED"
        if has_fault
        else "COMPLETED"
    )

    workflow_stopped = False

    for index, stage in enumerate(stages):
        stage_name = stage["name"]

        input_source = (
            "external_input"
            if index == 0
            else stages[index - 1]["name"]
        )

        event = "nominal_processing"
        evidence_state = "SUPPORTED"
        context_state = "CLEAN"
        failure_label: str | None = None
        stage_control_response = "NONE"
        status = "PROCESSED"

        if workflow_stopped:
            event = (
                "not_executed_after_control"
            )
            evidence_state = "SUPPORTED"
            context_state = "PROTECTED"
            failure_label = None
            status = "NOT_EXECUTED"

        elif (
            has_fault
            and fault_index is not None
        ):
            if index == fault_index:
                event = (
                    f"fault_injected:"
                    f"{fault_type}"
                )
                evidence_state = (
                    scenario_evidence
                )
                context_state = (
                    "CONTAMINATED"
                )
                failure_label = fault_type
                status = "FAULT_SOURCE"

            elif index > fault_index:
                event = (
                    f"fault_propagated:"
                    f"{fault_type}"
                )
                evidence_state = (
                    scenario_evidence
                )
                context_state = (
                    "CONTAMINATED"
                )
                failure_label = fault_type
                status = "CONTAMINATED"

                fault_reaches.append(
                    stage_name
                )

            fault_present_here = (
                index >= fault_index
            )

            if (
                selected_control != "NONE"
                and fault_present_here
                and stage_name
                == control_point
            ):
                decision = evaluate_control(
                    selected_control=(
                        selected_control
                    ),
                    evidence_state=(
                        scenario_evidence
                    ),
                    fault_type=fault_type,
                )

                stage_control_response = (
                    decision.response
                )

                control_response = (
                    decision.response
                )

                if (
                    decision.terminal_state
                    is not None
                ):
                    containment_point = (
                        stage_name
                    )

                    final_state = (
                        decision.terminal_state
                    )

                    event = (
                        "control_applied:"
                        f"{selected_control}:"
                        f"{decision.response}"
                    )

                    context_state = (
                        "CONTAINED"
                    )

                    status = (
                        decision.response
                    )

                    workflow_stopped = True

        trace.append(
            TraceRecord(
                scenario_id=scenario_id,
                step=index + 1,
                workflow_stage=stage_name,
                input_source=input_source,
                event=event,
                evidence_state=(
                    evidence_state
                ),
                context_state=(
                    context_state
                ),
                failure_label=(
                    failure_label
                ),
                control_response=(
                    stage_control_response
                ),
                status=status,
            )
        )

    blast_radius = len(fault_reaches)
    propagation_depth = len(
        fault_reaches
    )

    return ExecutionResult(
        scenario_id=scenario_id,
        trace=tuple(trace),
        fault_reaches=tuple(
            fault_reaches
        ),
        blast_radius=blast_radius,
        propagation_depth=(
            propagation_depth
        ),
        containment_point=(
            containment_point
        ),
        control_response=(
            control_response
        ),
        final_state=final_state,
        rollback_to=None,
    )


def _execute_cascade_scenario(
    workflow: dict[str, Any],
    scenario: dict[str, Any],
) -> ExecutionResult:
    """
    Execute deterministic simulated context isolation.

    CASCADE acts at the first downstream workflow stage
    receiving contaminated context.
    """

    scenario_id = scenario["id"]

    selected_control = scenario[
        "selected_control"
    ]

    fault_type = scenario["fault_type"]
    fault_source = scenario["fault_source"]
    scenario_evidence = scenario[
        "evidence_state"
    ]

    stages = workflow["roles"]

    stage_names = [
        stage["name"]
        for stage in stages
    ]

    if fault_source is None:
        raise ValueError(
            f"{scenario_id}: CASCADE scenario "
            "requires a fault source"
        )

    fault_index = stage_names.index(
        fault_source
    )

    containment_index = (
        fault_index + 1
    )

    if containment_index >= len(
        stage_names
    ):
        raise ValueError(
            f"{scenario_id}: no downstream "
            "stage exists for containment"
        )

    containment_point = stage_names[
        containment_index
    ]

    trace: list[TraceRecord] = []

    def append_trace(
        stage_index: int,
        event: str,
        evidence_state: str,
        context_state: str,
        failure_label: str | None,
        control_response: str,
        status: str,
        input_source: str | None = None,
    ) -> None:
        stage_name = stage_names[
            stage_index
        ]

        if input_source is None:
            input_source = (
                "external_input"
                if stage_index == 0
                else stage_names[
                    stage_index - 1
                ]
            )

        trace.append(
            TraceRecord(
                scenario_id=scenario_id,
                step=len(trace) + 1,
                workflow_stage=stage_name,
                input_source=input_source,
                event=event,
                evidence_state=(
                    evidence_state
                ),
                context_state=(
                    context_state
                ),
                failure_label=(
                    failure_label
                ),
                control_response=(
                    control_response
                ),
                status=status,
            )
        )

    # Establish trusted context up to the
    # stage immediately before fault injection.
    context = create_clean_context(
        stage_names[0]
    )

    append_trace(
        stage_index=0,
        event="nominal_processing",
        evidence_state="SUPPORTED",
        context_state="CLEAN",
        failure_label=None,
        control_response="NONE",
        status="PROCESSED",
    )

    last_trusted_snapshot = None

    if fault_index > 0:
        last_trusted_snapshot = (
            snapshot_trusted_context(
                stage_names[0],
                context,
            )
        )

    for index in range(
        1,
        fault_index,
    ):
        context = (
            advance_trusted_context(
                context,
                stage_names[index],
            )
        )

        last_trusted_snapshot = (
            snapshot_trusted_context(
                stage_names[index],
                context,
            )
        )

        append_trace(
            stage_index=index,
            event="nominal_processing",
            evidence_state="SUPPORTED",
            context_state="CLEAN",
            failure_label=None,
            control_response="NONE",
            status="PROCESSED",
        )

    # Process the source stage, then inject
    # the controlled synthetic fault.
    if fault_index > 0:
        context = (
            advance_trusted_context(
                context,
                fault_source,
            )
        )

    context = inject_fault(
        context,
        fault_type,
        fault_source,
    )

    append_trace(
        stage_index=fault_index,
        event=(
            f"fault_injected:"
            f"{fault_type}"
        ),
        evidence_state=(
            scenario_evidence
        ),
        context_state="CONTAMINATED",
        failure_label=fault_type,
        control_response="NONE",
        status="FAULT_SOURCE",
    )

    # First downstream stage receives the
    # contaminated context.
    context = (
        propagate_contaminated_context(
            context,
            containment_point,
        )
    )

    fault_reaches = [
        containment_point
    ]

    isolation = isolate_context(
        context,
        containment_point,
    )

    if (
        selected_control
        == "CASCADE_ISOLATION"
    ):
        # The containment stage produces a
        # sanitized downstream context.
        context = (
            advance_trusted_context(
                isolation.sanitized,
                containment_point,
            )
        )

        append_trace(
            stage_index=(
                containment_index
            ),
            event=(
                "control_applied:"
                "CASCADE_ISOLATION:"
                "ISOLATE"
            ),
            evidence_state="SUPPORTED",
            context_state="SANITIZED",
            failure_label=fault_type,
            control_response="ISOLATE",
            status="ISOLATED",
        )

        # Downstream stages receive only the
        # trusted sanitized context.
        for index in range(
            containment_index + 1,
            len(stage_names),
        ):
            context = (
                advance_trusted_context(
                    context,
                    stage_names[index],
                )
            )

            append_trace(
                stage_index=index,
                event=(
                    "protected_after_"
                    "isolation"
                ),
                evidence_state=(
                    "SUPPORTED"
                ),
                context_state="CLEAN",
                failure_label=None,
                control_response="NONE",
                status="PROTECTED",
            )

        return ExecutionResult(
            scenario_id=scenario_id,
            trace=tuple(trace),
            fault_reaches=tuple(
                fault_reaches
            ),
            blast_radius=1,
            propagation_depth=1,
            containment_point=(
                containment_point
            ),
            control_response="ISOLATE",
            final_state="CONTAINED",
            rollback_to=None,
        )

    if (
        selected_control
        != "CASCADE_ISOLATION_WITH_ROLLBACK"
    ):
        raise ValueError(
            f"Unexpected CASCADE control: "
            f"{selected_control!r}"
        )

    if last_trusted_snapshot is None:
        raise ValueError(
            f"{scenario_id}: no trusted "
            "snapshot exists for rollback"
        )

    append_trace(
        stage_index=containment_index,
        event=(
            "control_applied:"
            "CASCADE_ISOLATION_WITH_"
            "ROLLBACK:"
            "ROLLBACK_AND_REEXECUTE"
        ),
        evidence_state="SUPPORTED",
        context_state="QUARANTINED",
        failure_label=fault_type,
        control_response=(
            "ROLLBACK_AND_REEXECUTE"
        ),
        status="ROLLBACK_TRIGGERED",
    )

    restored = restore_snapshot(
        last_trusted_snapshot
    )

    rollback_index = stage_names.index(
        last_trusted_snapshot.stage
    )

    append_trace(
        stage_index=rollback_index,
        event=(
            "rollback_restored:"
            f"{last_trusted_snapshot.stage}"
        ),
        evidence_state="SUPPORTED",
        context_state="RESTORED",
        failure_label=None,
        control_response=(
            "ROLLBACK_AND_REEXECUTE"
        ),
        status="RESTORED",
        input_source="CASCADE_ISOLATION",
    )

    # Deterministically re-execute every
    # stage following the trusted checkpoint.
    context = restored

    for index in range(
        rollback_index + 1,
        len(stage_names),
    ):
        context = (
            advance_trusted_context(
                context,
                stage_names[index],
            )
        )

        append_trace(
            stage_index=index,
            event=(
                "reexecuted_after_rollback"
            ),
            evidence_state="SUPPORTED",
            context_state="CLEAN",
            failure_label=None,
            control_response="NONE",
            status="REEXECUTED",
        )

    return ExecutionResult(
        scenario_id=scenario_id,
        trace=tuple(trace),
        fault_reaches=tuple(
            fault_reaches
        ),
        blast_radius=1,
        propagation_depth=1,
        containment_point=(
            containment_point
        ),
        control_response=(
            "ROLLBACK_AND_REEXECUTE"
        ),
        final_state="RECOVERED",
        rollback_to=(
            last_trusted_snapshot.stage
        ),
    )


def execute_scenario(
    scenario_id: str,
) -> ExecutionResult:
    """Execute one deterministic frozen v1.0 scenario."""

    workflow = load_workflow()
    scenario = get_scenario(
        scenario_id
    )

    selected_control = scenario[
        "selected_control"
    ]

    if (
        selected_control
        not in SUPPORTED_CONTROLS
    ):
        raise NotImplementedError(
            f"{scenario_id} requires "
            f"unsupported control "
            f"{selected_control!r}"
        )

    if selected_control in CASCADE_CONTROLS:
        return _execute_cascade_scenario(
            workflow,
            scenario,
        )

    return _execute_standard_scenario(
        workflow,
        scenario,
    )