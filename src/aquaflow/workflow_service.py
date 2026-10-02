"""Application orchestration for operational workflows."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .workflow_models import normalize
from .workflow_rules import evaluate


class WorkflowService:
    """Run a normalized workflow and attach deterministic audit metadata."""

    def run(self, name: str, payload: dict[str, Any], received_at: datetime | None = None) -> dict[str, Any]:
        envelope = normalize(name, payload, received_at)
        result = evaluate(envelope.name, envelope.payload)
        result["workflow"] = envelope.name
        result["audit"] = {
            "contract": envelope.payload["_contract"],
            "required_fields": list(envelope.payload["_required"]),
            "received_at": envelope.received_at.isoformat(),
            "evidence_keys": sorted(result["evidence"]),
            "input_snapshot": {
                key: value for key, value in envelope.payload.items() if not key.startswith("_")
            },
            "components": ["workflow_models", "workflow_rules", "workflow_service"],
        }
        return result

