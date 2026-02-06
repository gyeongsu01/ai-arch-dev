# Graph-related functionality

from __future__ import annotations
from typing import Dict, Any
import uuid

from langgraph.graph import StateGraph, END

from app.common.types import GraphState, ToolCall
from app.service.registry import ActionRegistry
from app.platform.policy import enforce, Deny, _mask_pii
from app.service.tools import get_tool_map
from app.platform.audit import build_audit_event
from app.infra.llm import LLMClient


REGISTRY = ActionRegistry("app/service/actions/registry.yaml")
LLM = LLMClient() # LLM Interface
TOOLS = get_tool_map()


def _agent_decide(state: GraphState) -> Dict[str, Any]:
    """
    LLM Based Decision Node
    - 기존 Rule-based Router 대신 LLM에게 도구 제안을 받음
    """
    # 디버깅: 시작 시 쿼리 출력
    print(f"[DECIDE] Thinking... Query: {state.question}")
    
    # 1. Action 목록(Spec) 로드
    actions_desc = []
    for aid in REGISTRY.list_ids():
        spec = REGISTRY.get(aid)
        required_fields = spec.input_schema.get("required", [])
        params_desc = f" (필수 매개변수: {', '.join(required_fields)})" if required_fields else ""
        actions_desc.append(f"- {spec.id}: {spec.description}{params_desc}")
    desc_text = "\n".join(actions_desc)
    
    # 2. LLM Call (Predict Tool)
    tool_proposal = LLM.predict_tool_call(
        system_prompt="You are a helpful assistant. Select a tool if needed. Use exact parameter names from the tool description. For loan calculation, convert years to months (e.g., 30 years = 360 months) and use percentage for rates.",
        user_query=state.question,
        tools_desc=desc_text
    )

    # 3. Decision
    if tool_proposal:
        # LLM이 제안한 도구 호출 객체 생성
        tc = ToolCall(
            action_id=tool_proposal["action_id"],
            params=tool_proposal["params"]
        )
        # 디버깅: 도구 선택 시 출력
        print(f"[DECIDE] Tool Selected: {tc.action_id} Params: {tc.params}")
        return {"tool_call": tc}
    
    # No tool -> 바로 답변 생성
    # 디버깅: 도구 미선택 시 출력
    print("[DECIDE] No tool needed.")
    return {"answer": LLM.generate_response(state.question, [])}


def _execute_tool(state: GraphState) -> Dict[str, Any]:
    tc = state.tool_call
    if tc is None:
        return {"answer": state.answer or "(no tool)"}

    # 디버깅: 도구 실행 시작 출력
    print(f"[EXECUTE] Running tool: {tc.action_id}")
    
    spec = REGISTRY.get(tc.action_id)
    if spec is None:
        # registry miss → deny
        event = build_audit_event(state.trace_id, state.user.id, tc.action_id, "DENY", params=tc.params, reason="action_not_registered")
        TOOLS["audit.write"]({"event": event})
        # 디버깅: 에러 발생 시 출력
        print(f"[EXECUTE] Error: action_not_registered ({tc.action_id})")
        return {"answer": f"DENY: action_not_registered ({tc.action_id})"}

    # 정책 적용 (범위/스키마/허용 목록/PII/속도 제한)
    try:
        # enforce는 정리된 매개변수를 반환!
        safe_params = enforce(state.user, spec, tc.params)
        decision = "PERMIT"
        reason = None
    except Deny as e:
        decision = "DENY"
        reason = e.reason
        event = build_audit_event(state.trace_id, state.user.id, tc.action_id, decision, params=tc.params, reason=reason)
        TOOLS["audit.write"]({"event": event})
        # 디버깅: 에러 발생 시 출력
        print(f"[EXECUTE] Error: {reason}")
        return {"answer": f"DENY: {reason}"}

    # 보호된 매개변수로 실행
    tool_fn = TOOLS.get(tc.action_id)
    if tool_fn is None:
        event = build_audit_event(state.trace_id, state.user.id, tc.action_id, "DENY", params=safe_params, reason="tool_not_implemented")
        TOOLS["audit.write"]({"event": event})
        # 디버깅: 에러 발생 시 출력
        print(f"[EXECUTE] Error: tool_not_implemented ({tc.action_id})")
        return {"answer": f"DENY: tool_not_implemented ({tc.action_id})"}

    result = tool_fn(safe_params)
    event = build_audit_event(state.trace_id, state.user.id, tc.action_id, decision, params=safe_params, result=result, reason=reason)
    TOOLS["audit.write"]({"event": event})

    # 최종 답변 생성 (LLM)
    final_ans = LLM.generate_response(state.question, [result])
    # 디버깅: 실행 결과 출력
    print(f"[EXECUTE] Result: {result}")
    return {
        "tool_result": result,
        "answer": final_ans
    }


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("agent", _agent_decide)
    g.add_node("tool", _execute_tool)

    g.set_entry_point("agent")
    g.add_edge("agent", "tool")
    g.add_edge("tool", END)

    return g.compile()


GRAPH = build_graph()


def run_graph(user: Dict[str, Any], question: str) -> Dict[str, Any]:
    trace_id = str(uuid.uuid4())
    
    # LLM 호출 전에 PII 마스킹 적용
    masked_question = _mask_pii(question)
    
    state = GraphState(trace_id=trace_id, user=user, question=masked_question)
    out = GRAPH.invoke(state)
    # out은 dict 형태로 업데이트된 state 조각이 들어올 수 있어, GraphState로 재구성
    # LangGraph 특성상 최종 반환을 그대로 사용
    return {"trace_id": trace_id, **out}
