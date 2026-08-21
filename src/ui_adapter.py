from __future__ import annotations

from typing import Any

from src.agents import get_role_names
from src.engine import execute_scenario
from src.scenarios import load_scenarios


STATUS_MAP = {
    "PROCESSED": "normal",
    "FAULT_SOURCE": "fault seed",
    "CONTAMINATED": "warning",
    "BLOCK": "blocked",
    "ESCALATE": "escalated",
    "REQUIRE_HUMAN_APPROVAL": "escalated",
    "NOT_EXECUTED": "contained",
    "ISOLATED": "contained",
    "PROTECTED": "contained",
    "ROLLBACK_TRIGGERED": "contained",
    "RESTORED": "evidence",
    "REEXECUTED": "evidence",
}


RISK_INDICATOR = {
    "PROCESSED": 0.10,
    "FAULT_SOURCE": 0.90,
    "CONTAMINATED": 0.80,
    "BLOCK": 0.75,
    "ESCALATE": 0.70,
    "REQUIRE_HUMAN_APPROVAL": 0.70,
    "NOT_EXECUTED": 0.20,
    "ISOLATED": 0.30,
    "PROTECTED": 0.15,
    "ROLLBACK_TRIGGERED": 0.40,
    "RESTORED": 0.20,
    "REEXECUTED": 0.15,
}


def get_workflow_stages() -> tuple[str, ...]:
    """Return canonical workflow stages for the UI."""

    return get_role_names()


def get_scenario_catalog() -> dict[str, dict[str, Any]]:
    """
    Build Streamlit-facing scenario metadata from the frozen registry
    and actual canonical engine results.
    """

    registry = load_scenarios()

    catalog: dict[str, dict[str, Any]] = {}

    for scenario in registry["scenarios"]:
        scenario_id = scenario["id"]
        result = execute_scenario(scenario_id)

        display_name = (
            f"{scenario_id} — {scenario['name']}"
        )

        catalog[display_name] = {
            "scenario_id": scenario_id,
            "objective": scenario["description"],
            "summary": (
                f"Canonical deterministic execution finished in "
                f"{result.final_state}. "
                f"Control response: {result.control_response}."
            ),
            "root_cause": (
                scenario["fault_source"]
                if scenario["fault_source"] is not None
                else "None"
            ),
            "containment": (
                result.containment_point
                if result.containment_point is not None
                else "Not required"
            ),
            "final_state": result.final_state,
        }

    return catalog


def get_trace_rows(
    scenario_id: str,
) -> list[dict[str, Any]]:
    """
    Translate canonical execution trace records into the existing
    Streamlit table/chart representation.

    risk_score is a fixed presentation-only heuristic indicator.
    It is not an empirical probability or calibrated risk estimate.
    """

    result = execute_scenario(scenario_id)

    rows: list[dict[str, Any]] = []

    for record in result.trace:
        rows.append(
            {
                "step": record.step,
                "agent": record.workflow_stage,
                "event": record.event,
                "status": STATUS_MAP.get(
                    record.status,
                    "normal",
                ),
                "risk_score": RISK_INDICATOR.get(
                    record.status,
                    0.10,
                ),
                "evidence_state": record.evidence_state,
                "context_state": record.context_state,
                "control_response": record.control_response,
            }
        )

    return rows