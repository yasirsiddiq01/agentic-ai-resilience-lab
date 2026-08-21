from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.agents import load_workflow
from src.scenarios import load_scenarios
from src.tracing import TraceRecord


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
        result["trace"] = [record.to_dict() for record in self.trace]
        result["fault_reaches"] = list(self.fault_reaches)
        return result


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return one validated frozen scenario by ID."""

    registry = load_scenarios()

    for scenario in registry["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario

    raise KeyError(f"Unknown scenario ID: {scenario_id}")


def execute_scenario(scenario_id: str) -> ExecutionResult:
    """
    Execute one deterministic v1.0 scenario.

    Step 5 intentionally supports only scenarios with no active
    containment/recovery control. Controlled scenarios are rejected
    until their control behaviour is implemented in later checkpoints.
    """

    workflow = load_workflow()
    scenario = get_scenario(scenario_id)

    selected_control = scenario["selected_control"]

    if selected_control != "NONE":
        raise NotImplementedError(
            f"{scenario_id} requires control {selected_control!r}. "
            "Controlled execution is not implemented at Step 5."
        )

    roles = workflow["roles"]
    stage_names = [role["name"] for role in roles]

    fault_type = scenario["fault_type"]
    fault_source = scenario["fault_source"]
    scenario_evidence = scenario["evidence_state"]

    has_fault = fault_type != "NONE"

    fault_index: int | None = None

    if has_fault:
        if fault_source is None:
            raise ValueError(
                f"{scenario_id}: fault_type is {fault_type!r} "
                "but fault_source is null"
            )

        try:
            fault_index = stage_names.index(fault_source)
        except ValueError as exc:
            raise ValueError(
                f"{scenario_id}: fault source {fault_source!r} "
                "is not in the canonical workflow"
            ) from exc

    trace: list[TraceRecord] = []
    fault_reaches: list[str] = []

    for index, role in enumerate(roles):
        stage_name = role["name"]

        input_source = (
            "external_input"
            if index == 0
            else roles[index - 1]["name"]
        )

        event = "nominal_processing"
        evidence_state = "SUPPORTED"
        context_state = "CLEAN"
        failure_label: str | None = None
        status = "PROCESSED"

        if has_fault and fault_index is not None:
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
                control_response="NONE",
                status=status,
            )
        )

    if has_fault:
        final_state = "FAILED_UNCONTAINED"
    else:
        final_state = "COMPLETED"

    blast_radius = len(fault_reaches)
    propagation_depth = len(fault_reaches)

    return ExecutionResult(
        scenario_id=scenario_id,
        trace=tuple(trace),
        fault_reaches=tuple(fault_reaches),
        blast_radius=blast_radius,
        propagation_depth=propagation_depth,
        containment_point=None,
        control_response="NONE",
        final_state=final_state,
        rollback_to=None,
    )