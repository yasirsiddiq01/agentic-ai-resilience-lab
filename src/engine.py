from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.agents import load_workflow
from src.controls import (
    ControlDecision,
    evaluate_evidence_gate,
    evaluate_safety_guard,
)
from src.scenarios import load_scenarios
from src.tracing import TraceRecord


SUPPORTED_CONTROLS = {
    "NONE",
    "EVIDENCE_GATE",
    "SAFETY_GUARD",
}

CONTROL_POINTS = {
    "EVIDENCE_GATE": "Verification Agent",
    "SAFETY_GUARD": "Safety Agent",
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
        """Return a fully serialisable result including trace records."""

        result = asdict(self)
        result["trace"] = [
            record.to_dict()
            for record in self.trace
        ]
        result["fault_reaches"] = list(self.fault_reaches)
        return result


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return one validated frozen scenario by ID."""

    registry = load_scenarios()

    for scenario in registry["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario

    raise KeyError(f"Unknown scenario ID: {scenario_id}")


def evaluate_control(
    selected_control: str,
    evidence_state: str,
    fault_type: str,
) -> ControlDecision:
    """Evaluate one supported deterministic v1.0 control."""

    if selected_control == "EVIDENCE_GATE":
        return evaluate_evidence_gate(evidence_state)

    if selected_control == "SAFETY_GUARD":
        return evaluate_safety_guard(fault_type)

    raise ValueError(
        f"Control {selected_control!r} has no evaluator"
    )


def execute_scenario(scenario_id: str) -> ExecutionResult:
    """
    Execute one deterministic v1.0 scenario.

    EvidenceGate and Safety Guard are implemented as bounded
    deterministic controls. CASCADE isolation and rollback remain
    deliberately unavailable until their dedicated implementation
    checkpoint.
    """

    workflow = load_workflow()
    scenario = get_scenario(scenario_id)

    selected_control = scenario["selected_control"]

    if selected_control not in SUPPORTED_CONTROLS:
        raise NotImplementedError(
            f"{scenario_id} requires control "
            f"{selected_control!r}. "
            "This control is not implemented yet."
        )

    stages = workflow["roles"]
    stage_names = [
        stage["name"]
        for stage in stages
    ]

    fault_type = scenario["fault_type"]
    fault_source = scenario["fault_source"]
    scenario_evidence = scenario["evidence_state"]

    has_fault = fault_type != "NONE"

    fault_index: int | None = None

    if has_fault:
        if fault_source is None:
            raise ValueError(
                f"{scenario_id}: fault_type is "
                f"{fault_type!r} but fault_source is null"
            )

        try:
            fault_index = stage_names.index(fault_source)
        except ValueError as exc:
            raise ValueError(
                f"{scenario_id}: fault source "
                f"{fault_source!r} is not in the "
                "canonical workflow"
            ) from exc

    control_point = CONTROL_POINTS.get(selected_control)

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
            event = "not_executed_after_control"
            evidence_state = "SUPPORTED"
            context_state = "PROTECTED"
            failure_label = None
            status = "NOT_EXECUTED"

        elif has_fault and fault_index is not None:
            if index == fault_index:
                event = f"fault_injected:{fault_type}"
                evidence_state = scenario_evidence
                context_state = "CONTAMINATED"
                failure_label = fault_type
                status = "FAULT_SOURCE"

            elif index > fault_index:
                event = f"fault_propagated:{fault_type}"
                evidence_state = scenario_evidence
                context_state = "CONTAMINATED"
                failure_label = fault_type
                status = "CONTAMINATED"

                fault_reaches.append(stage_name)

            fault_present_here = index >= fault_index

            if (
                selected_control != "NONE"
                and fault_present_here
                and stage_name == control_point
            ):
                decision = evaluate_control(
                    selected_control=selected_control,
                    evidence_state=scenario_evidence,
                    fault_type=fault_type,
                )

                stage_control_response = decision.response
                control_response = decision.response

                if decision.terminal_state is not None:
                    containment_point = stage_name
                    final_state = decision.terminal_state

                    event = (
                        f"control_applied:"
                        f"{selected_control}:"
                        f"{decision.response}"
                    )

                    context_state = "CONTAINED"
                    status = decision.response
                    workflow_stopped = True

        trace.append(
            TraceRecord(
                scenario_id=scenario_id,
                step=index + 1,
                workflow_stage=stage_name,
                input_source=input_source,
                event=event,
                evidence_state=evidence_state,
                context_state=context_state,
                failure_label=failure_label,
                control_response=stage_control_response,
                status=status,
            )
        )

    blast_radius = len(fault_reaches)
    propagation_depth = len(fault_reaches)

    return ExecutionResult(
        scenario_id=scenario_id,
        trace=tuple(trace),
        fault_reaches=tuple(fault_reaches),
        blast_radius=blast_radius,
        propagation_depth=propagation_depth,
        containment_point=containment_point,
        control_response=control_response,
        final_state=final_state,
        rollback_to=None,
    )