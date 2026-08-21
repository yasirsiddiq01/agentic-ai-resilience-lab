from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.agents import get_role_names


ROOT_DIR = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT_DIR / "data" / "scenarios.json"

EXPECTED_SCENARIO_IDS = [
    "S01",
    "S02",
    "S03",
    "S04",
    "S05",
    "S06",
    "S07",
    "S08",
]

EXPECTED_RESULT_FIELDS = {
    "fault_reaches",
    "blast_radius",
    "propagation_depth",
    "containment_point",
    "control_response",
    "final_state",
    "rollback_to",
}


def validate_scenarios(data: dict[str, Any]) -> None:
    """Validate the frozen v1.0 scenario registry."""

    if data.get("version") != "1.0":
        raise ValueError("Scenario registry version must be 1.0")

    if data.get("status") != "frozen":
        raise ValueError("Scenario registry status must be frozen")

    scenarios = data.get("scenarios")

    if not isinstance(scenarios, list):
        raise ValueError("Scenarios must be a list")

    if len(scenarios) != 8:
        raise ValueError(
            f"Scenario registry must contain exactly 8 scenarios; "
            f"found {len(scenarios)}"
        )

    scenario_ids = [scenario.get("id") for scenario in scenarios]

    if scenario_ids != EXPECTED_SCENARIO_IDS:
        raise ValueError(
            "Scenario IDs must be exactly S01 through S08 "
            "in canonical order"
        )

    if len(set(scenario_ids)) != 8:
        raise ValueError("Scenario IDs must be unique")

    evidence_states = set(data.get("evidence_states", []))
    controls = set(data.get("controls", []))
    role_names = set(get_role_names())

    if not evidence_states:
        raise ValueError("At least one evidence state must be defined")

    if not controls:
        raise ValueError("At least one control must be defined")

    for scenario in scenarios:
        scenario_id = scenario["id"]

        fault_source = scenario.get("fault_source")
        if fault_source is not None and fault_source not in role_names:
            raise ValueError(
                f"{scenario_id}: unknown fault source {fault_source!r}"
            )

        evidence_state = scenario.get("evidence_state")
        if evidence_state not in evidence_states:
            raise ValueError(
                f"{scenario_id}: unknown evidence state "
                f"{evidence_state!r}"
            )

        selected_control = scenario.get("selected_control")
        if selected_control not in controls:
            raise ValueError(
                f"{scenario_id}: unknown control "
                f"{selected_control!r}"
            )

        expected = scenario.get("expected")

        if not isinstance(expected, dict):
            raise ValueError(
                f"{scenario_id}: expected result must be an object"
            )

        missing = EXPECTED_RESULT_FIELDS - expected.keys()
        if missing:
            raise ValueError(
                f"{scenario_id}: expected result is missing fields "
                f"{sorted(missing)}"
            )

        fault_reaches = expected["fault_reaches"]

        if not isinstance(fault_reaches, list):
            raise ValueError(
                f"{scenario_id}: fault_reaches must be a list"
            )

        unknown_roles = [
            role for role in fault_reaches
            if role not in role_names
        ]

        if unknown_roles:
            raise ValueError(
                f"{scenario_id}: fault_reaches contains unknown roles "
                f"{unknown_roles}"
            )

        blast_radius = expected["blast_radius"]

        if not isinstance(blast_radius, int) or blast_radius < 0:
            raise ValueError(
                f"{scenario_id}: blast_radius must be "
                "a non-negative integer"
            )

        if blast_radius != len(fault_reaches):
            raise ValueError(
                f"{scenario_id}: blast_radius does not match "
                "the number of affected downstream roles"
            )

        propagation_depth = expected["propagation_depth"]

        if (
            not isinstance(propagation_depth, int)
            or propagation_depth < 0
        ):
            raise ValueError(
                f"{scenario_id}: propagation_depth must be "
                "a non-negative integer"
            )

        containment_point = expected["containment_point"]

        if (
            containment_point is not None
            and containment_point not in role_names
        ):
            raise ValueError(
                f"{scenario_id}: unknown containment point "
                f"{containment_point!r}"
            )

        rollback_to = expected["rollback_to"]

        if rollback_to is not None and rollback_to not in role_names:
            raise ValueError(
                f"{scenario_id}: unknown rollback target "
                f"{rollback_to!r}"
            )


def load_scenarios(
    path: Path | str = SCENARIOS_PATH,
) -> dict[str, Any]:
    """Load and validate the frozen v1.0 scenario registry."""

    scenarios_path = Path(path)

    if not scenarios_path.exists():
        raise FileNotFoundError(
            f"Scenario specification not found: {scenarios_path}"
        )

    with scenarios_path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    validate_scenarios(data)
    return data