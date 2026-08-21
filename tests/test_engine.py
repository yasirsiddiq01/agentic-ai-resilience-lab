import pytest

from src.engine import execute_scenario
from src.scenarios import load_scenarios


def frozen_expectations():
    registry = load_scenarios()

    return {
        scenario["id"]: scenario["expected"]
        for scenario in registry["scenarios"]
    }


@pytest.mark.parametrize(
    "scenario_id",
    [
        "S01",
        "S02",
        "S03",
        "S04",
        "S05",
        "S06",
        "S07",
        "S08",
    ],
)
def test_scenario_matches_frozen_expectation(scenario_id):
    expected = frozen_expectations()[scenario_id]

    actual = execute_scenario(scenario_id).to_summary()
    actual.pop("scenario_id")

    assert actual == expected


def test_nominal_scenario_has_clean_completion():
    result = execute_scenario("S01")

    assert result.final_state == "COMPLETED"
    assert result.blast_radius == 0
    assert result.fault_reaches == ()

    assert all(
        record.context_state == "CLEAN"
        for record in result.trace
    )


def test_uncontrolled_fault_propagates_downstream():
    result = execute_scenario("S04")

    assert result.final_state == "FAILED_UNCONTAINED"

    assert result.fault_reaches == (
        "Action Agent",
        "Verification Agent",
        "Safety Agent",
        "Report Agent",
    )

    assert result.blast_radius == 4
    assert result.containment_point is None


def test_cascade_isolation_protects_downstream_workflow():
    result = execute_scenario("S05")

    assert result.final_state == "CONTAINED"
    assert result.containment_point == "Log Analysis Agent"
    assert result.fault_reaches == ("Log Analysis Agent",)

    protected = [
        record
        for record in result.trace
        if record.status == "PROTECTED"
    ]

    assert protected


def test_rollback_is_explicitly_visible_in_trace():
    result = execute_scenario("S08")

    assert result.final_state == "RECOVERED"
    assert result.rollback_to == "Log Analysis Agent"

    events = [
        record.event
        for record in result.trace
    ]

    assert any(
        event.startswith("rollback_restored:")
        for event in events
    )

    assert "reexecuted_after_rollback" in events


def test_execution_is_deterministic():
    first = execute_scenario("S08").to_dict()
    second = execute_scenario("S08").to_dict()

    assert first == second


def test_unknown_scenario_is_rejected():
    with pytest.raises(KeyError):
        execute_scenario("S99")
