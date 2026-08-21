from src.ui_adapter import (
    get_scenario_catalog,
    get_trace_rows,
    get_workflow_stages,
)


def test_ui_adapter_uses_canonical_workflow():
    stages = get_workflow_stages()

    assert len(stages) == 8
    assert stages[0] == "User Report"
    assert stages[-1] == "Report Agent"


def test_ui_adapter_exposes_all_frozen_scenarios():
    catalog = get_scenario_catalog()

    assert len(catalog) == 8

    scenario_ids = [
        metadata["scenario_id"]
        for metadata in catalog.values()
    ]

    assert scenario_ids == [
        "S01",
        "S02",
        "S03",
        "S04",
        "S05",
        "S06",
        "S07",
        "S08",
    ]


def test_ui_trace_is_generated_from_engine():
    rows = get_trace_rows("S04")

    fault_rows = [
        row
        for row in rows
        if row["status"] == "fault seed"
    ]

    contaminated_rows = [
        row
        for row in rows
        if row["status"] == "warning"
    ]

    assert len(fault_rows) == 1
    assert fault_rows[0]["agent"] == "Knowledge Agent"

    assert [
        row["agent"]
        for row in contaminated_rows
    ] == [
        "Action Agent",
        "Verification Agent",
        "Safety Agent",
        "Report Agent",
    ]


def test_rollback_trace_remains_visible_to_ui():
    rows = get_trace_rows("S08")

    events = [
        row["event"]
        for row in rows
    ]

    assert any(
        event.startswith("rollback_restored:")
        for event in events
    )

    assert "reexecuted_after_rollback" in events