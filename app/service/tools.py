# Tool definitions

from __future__ import annotations
from typing import Any, Dict, Callable
from app.service.actions.doc_search import doc_search
from app.platform.audit import write_audit


ToolFn = Callable[[Dict[str, Any]], Dict[str, Any]]


def get_tool_map() -> Dict[str, ToolFn]:
    return {
        "doc.search": _tool_doc_search,
        "audit.write": _tool_audit_write,
        "fin.calc_loan": _tool_loan_calc,
    }


def _tool_doc_search(params: Dict[str, Any]) -> Dict[str, Any]:
    # enforce()에서 이미 PII 마스킹이 적용된 params가 전달됨
    return doc_search(
        query=params["query"],
        top_k=int(params.get("top_k", 5)),
        filters=params.get("filters", {"status": "active"}),
    )


def _tool_audit_write(params: Dict[str, Any]) -> Dict[str, Any]:
    write_audit(params["event"])
    return {"ok": True}


def _tool_loan_calc(params: Dict[str, Any]) -> Dict[str, Any]:
    # 대출 원금, 연간 이율, 기간(개월)을 입력받아 월 상환액과 총 이자를 계산
    principal = params["principal"]
    annual_rate = params["annual_rate"]
    months = params["months"]
    
    # 월 이율 계산
    monthly_rate = annual_rate / 100 / 12
    
    # 상환 공식: P * r * (1+r)^n / ((1+r)^n - 1)
    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    
    # 총 이자 = 총 상환액 - 원금
    total_payments = monthly_payment * months
    total_interest = total_payments - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2)
    }
