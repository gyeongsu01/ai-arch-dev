# Policy definitions

from __future__ import annotations
from typing import Any, Dict, Tuple
import re
import time
from app.service.registry import ActionSpec
from app.common.types import UserContext

# Rate Limit 저장소 (MVP: In-memory)
_RATE_LIMIT_STORE = {}

class Deny(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason

def _has_scopes(user: UserContext, required: list[str]) -> bool:
    """사용자 권한(스코프) 검증"""
    if not required:
        return True
    s = set(user.scopes)
    return all(r in s for r in required)

def _check_rate_limit(user_id: str, limit: int = 10, window_sec: int = 60) -> bool:
    """간단한 Rate Limiting (MVP: In-memory)"""
    now = time.time()
    history = _RATE_LIMIT_STORE.get(user_id, [])
    # 윈도우 지난 기록 제거
    history = [t for t in history if now - t < window_sec]
    
    if len(history) >= limit:
        return False
    
    history.append(now)
    _RATE_LIMIT_STORE[user_id] = history
    return True

def _mask_pii(text: str) -> str:
    """PII(개인정보) 마스킹 정책"""
    # 1️⃣ 주민등록번호 마스킹 (YYMMDD-NNNNNNN)
    text = re.sub(r'(\d{6})-(\d{7})', r'\1-*******', text)
    # 2️⃣ Email Masking
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '<EMAIL_MASKED>', text)
    # 3️⃣ Phone Masking (010-XXXX-XXXX)
    text = re.sub(r'(01[0-9])-?(\d{4})-?(\d{4})', r'\1-****-\3', text)
    # 4️⃣ 카드번호 마스킹
    text = re.sub(r'(\d{4})-(\d{4})-(\d{4})-(\d{4})', r'\1-****-****-\4', text)
    return text

def _sanitize_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """입력 파라미터 내 PII 마스킹 적용"""
    sanitized = {}
    for k, v in params.items():
        if isinstance(v, str):
            sanitized[k] = _mask_pii(v)
        else:
            sanitized[k] = v
    return sanitized

def _validate_schema_and_allowlist(params: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
    """스키마 및 허용값(Allowlist) 검증"""
    # 1) Required check
    req = schema.get("required", [])
    for k in req:
        if k not in params:
            return False, f"missing_required_field: {k}"
            
    # 2) Enum (Allowlist) check
    props = schema.get("properties", {})
    for k, v in params.items():
        if k in props:
            # Check Enum allowlist
            allowed = props[k].get("enum")
            if allowed and v not in allowed:
                return False, f"value_not_allowed: key={k}, value={v}, allowed={allowed}"
                
    return True, "ok"

def enforce(user: UserContext, spec: ActionSpec, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    정책 적용 및 검증.
    Returns: PII 등이 마스킹(Sanitize)된 안전한 Params
    """
    # 1) Rate Limit
    if not _check_rate_limit(user.id):
        raise Deny("rate_limit_exceeded")

    # 2) Scope check
    if not _has_scopes(user, spec.scopes_required):
        raise Deny(f"missing_scopes: required={spec.scopes_required}")

    # 3) Schema & Allowlist check
    ok, msg = _validate_schema_and_allowlist(params, spec.input_schema)
    if not ok:
        raise Deny(f"schema_invalid: {msg}")
        
    # 4) PII Masking (Transformation Policy)
    safe_params = _sanitize_params(params)
    
    return safe_params

