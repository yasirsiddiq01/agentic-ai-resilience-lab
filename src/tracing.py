from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TraceRecord:
    """One deterministic workflow-stage trace event."""

    scenario_id: str
    step: int
    workflow_stage: str
    input_source: str
    event: str
    evidence_state: str
    context_state: str
    failure_label: str | None
    control_response: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable representation of the trace record."""

        return asdict(self)