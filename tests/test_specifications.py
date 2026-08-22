from src.agents import get_role_names, load_workflow
from src.scenarios import load_scenarios


EXPECTED_STAGES = (
    "User Report",
    "Triage Agent",
    "Log Analysis Agent",
    "Knowledge Agent",
    "Action Agent",
    "Verification Agent",
    "Safety Agent",
    "Report Agent",
)


def test_frozen_workflow_has_eight_canonical_stages():
    workflow = load_workflow()

    assert workflow["version"] == "1.0"
    assert workflow["status"] == "frozen"
    assert get_role_names() == EXPECTED_STAGES


def test_workflow_handoffs_are_sequential():
    workflow = load_workflow()
    roles = workflow["roles"]

    for index, role in enumerate(roles[:-1]):
        assert role["handoff_to"] == roles[index + 1]["id"]

    assert roles[-1]["handoff_to"] is None


def test_frozen_registry_contains_s01_to_s08():
    registry = load_scenarios()

    assert registry["version"] == "1.0"
    assert registry["status"] == "frozen"

    assert [s["id"] for s in registry["scenarios"]] == [
        "S01",
        "S02",
        "S03",
        "S04",
        "S05",
        "S06",
        "S07",
        "S08",
    ]
