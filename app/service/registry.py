# Registry functionality

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import yaml
from pathlib import Path


@dataclass(frozen=True)
class ActionSpec:
    id: str
    description: str
    scopes_required: List[str]
    timeout_ms: int
    retry: int
    idempotent: bool
    audit_level: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class ActionRegistry:
    def __init__(self, path: str):
        self.path = Path(path)
        self._by_id: Dict[str, ActionSpec] = {}
        self._load()

    def _load(self) -> None:
        raw = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        for a in raw.get("actions", []):
            spec = ActionSpec(
                id=a["id"],
                description=a.get("description", ""),
                scopes_required=a.get("scopes_required", []),
                timeout_ms=int(a.get("timeout_ms", 1000)),
                retry=int(a.get("retry", 0)),
                idempotent=bool(a.get("idempotent", True)),
                audit_level=a.get("audit_level", "BASIC"),
                input_schema=a.get("input_schema", {"type": "object"}),
                output_schema=a.get("output_schema", {"type": "object"}),
            )
            self._by_id[spec.id] = spec

    def get(self, action_id: str) -> Optional[ActionSpec]:
        return self._by_id.get(action_id)

    def list_ids(self) -> List[str]:
        return sorted(self._by_id.keys())
