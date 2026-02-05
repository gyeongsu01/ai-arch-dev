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
