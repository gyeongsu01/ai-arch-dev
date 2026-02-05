# Service Router
from __future__ import annotations
from typing import Dict, Any, Optional
from app.service.registry import ActionRegistry, ActionSpec
from app.common.types import ToolCall

class ToolRouter:
    """
    사용자의 질문(Question)을 분석하여 적절한 Action(Tool)으로 매핑하는 라우터.
    Simple Rule-based (MVP) -> Semantic Router (Future) 교체 가능 설계
    """
    def __init__(self, registry: ActionRegistry):
        self.registry = registry

    def route(self, question: str) -> Optional[ToolCall]:
        """
        질문을 입력받아 실행할 도구(ToolCall)를 반환하거나, 없으면 None 반환(대화 모드).
        """
        q = question.lower()

        # 1. Iterate over all registered actions
        # registry.yaml에 정의된 description을 기반으로 매칭하는 것이 이상적이나,
        # MVP 단계에서는 키워드 매칭 로직을 여기서 동적으로 구성할 수도 있음.
        
        # [MVP] 단순 키워드 매핑 (확장 가능 구조)
        # 실제로는 여기서 LLM을 호출하여 'user query' -> 'action selection'을 수행해야 함.
        # 비용 절감을 위해 여기선 Rule-based로 예시 구현.
        
        if self._is_search_intent(q):
            # doc.search 스펙 확인
            action_id = "doc.search"
            spec = self.registry.get(action_id)
            if spec:
                return ToolCall(
                    action_id=action_id,
                    params=self._extract_search_params(q)
                )

        if self._is_audit_intent(q):
             # audit.write 스펙 확인 (예시용, 보통 사용자가 직접 호출하진 않음)
             pass

        # 매칭되는 도구가 없으면 일반 대화로 간주
        return None

    def _is_search_intent(self, q: str) -> bool:
        keywords = ["찾아", "검색", "알려줘", "조회", "search", "find"]
        return any(k in q for k in keywords)

    def _extract_search_params(self, q: str) -> Dict[str, Any]:
        """
        질문에서 검색 파라미터 추출 (MVP: 전체 쿼리 사용)
        """
        return {
            "query": q,
            "top_k": 5,
            "filters": {"status": "active"} 
        }

    def _is_audit_intent(self, q: str) -> bool:
        return "로그" in q and "기록" in q
