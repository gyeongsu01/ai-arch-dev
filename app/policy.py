# Policy definitions

from __future__ import annotations
from typing import Any, Dict, Tuple
from app.registry import ActionSpec
from app.types import UserContext


class Deny(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _has_scopes(user: UserContext, required: list[str]) -> bool:
    if not required:
        return True
    s = set(user.scopes)
    return all(r in s for r in required)


def _validate_min_schema(params: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
    """
    여기선 '최소 검증'만 한다 (라이브러리 없이).
    - required 필드 존재 여부
    - type=object 가정
    """
    req = schema.get("required", [])
    for k in req:
        if k not in params:
            return False, f"missing_required_field: {k}"
    return True, "ok"


def enforce(user: UserContext, spec: ActionSpec, params: Dict[str, Any]) -> None:
    # 1) Scope check
    if not _has_scopes(user, spec.scopes_required):
        raise Deny(f"missing_scopes: required={spec.scopes_required}, user={user.scopes}")

    # 2) Schema check(최소)
    ok, msg = _validate_min_schema(params, spec.input_schema)
    if not ok:
        raise Deny(f"schema_invalid: {msg}")
