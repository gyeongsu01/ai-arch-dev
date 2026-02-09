# Audit functionality

from __future__ import annotations
from typing import Any, Dict
import json
import time


def build_audit_event(
    trace_id: str,
    user_id: str,
    action_id: str,
    decision: str,
    params: Dict[str, Any] | None = None,
    result: Dict[str, Any] | None = None,
    reason: str | None = None,
) -> Dict[str, Any]:
    return {
        "ts": int(time.time() * 1000),
        "trace_id": trace_id,
        "user_id": user_id,
        "action_id": action_id,
        "decision": decision,  # PERMIT / DENY
        "reason": reason,
        "params": params or {},
        "result": result or {},
    }


def write_audit(event: Dict[str, Any]) -> None:
    # MVP: stdout. 나중에 Kafka/ES/DB로 교체
    print("[AUDIT]", json.dumps(event, ensure_ascii=False))
