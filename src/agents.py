from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT_DIR / "data" / "workflow_v1.json"


def validate_workflow(data: dict[str, Any]) -> None:
    """Validate the frozen v1.0 workflow specification."""

    if data.get("version") != "1.0":
        raise ValueError("Workflow version must be 1.0")

    if data.get("status") != "frozen":
        raise ValueError("Workflow status must be frozen")

    roles = data.get("roles")

    if not isinstance(roles, list):
        raise ValueError("Workflow roles must be a list")

    if len(roles) != 8:
        raise ValueError(
            f"Workflow must contain exactly 8 roles; found {len(roles)}"
        )

    required_fields = {"order", "id", "name", "handoff_to"}

    for index, role in enumerate(roles, start=1):
        if not isinstance(role, dict):
            raise ValueError(f"Role {index} must be an object")

        missing = required_fields - role.keys()
        if missing:
            raise ValueError(
                f"Role {index} is missing required fields: {sorted(missing)}"
            )

    orders = [role["order"] for role in roles]
    role_ids = [role["id"] for role in roles]
    role_names = [role["name"] for role in roles]

    if orders != list(range(1, 9)):
        raise ValueError(
            "Workflow role order must be exactly 1 through 8"
        )

    if len(set(role_ids)) != 8:
        raise ValueError("Workflow role IDs must be unique")

    if len(set(role_names)) != 8:
        raise ValueError("Workflow role names must be unique")

    for index, role in enumerate(roles):
        expected_handoff = (
            roles[index + 1]["id"]
            if index < len(roles) - 1
            else None
        )

        if role["handoff_to"] != expected_handoff:
            raise ValueError(
                f"Invalid handoff for {role['name']}: "
                f"expected {expected_handoff!r}, "
                f"found {role['handoff_to']!r}"
            )


def load_workflow(
    path: Path | str = WORKFLOW_PATH,
) -> dict[str, Any]:
    """Load and validate the frozen v1.0 workflow."""

    workflow_path = Path(path)

    if not workflow_path.exists():
        raise FileNotFoundError(
            f"Workflow specification not found: {workflow_path}"
        )

    with workflow_path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    validate_workflow(data)
    return data


def get_role_names() -> tuple[str, ...]:
    """Return canonical workflow role names in execution order."""

    workflow = load_workflow()
    return tuple(role["name"] for role in workflow["roles"])