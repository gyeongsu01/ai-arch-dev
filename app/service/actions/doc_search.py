from typing import Dict, Any, List
from app.data.rag import get_rag_service
import logging

logger = logging.getLogger(__name__)

def doc_search(query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    문서 검색 (RAG retrieval)

    Args:
        query: 검색 쿼리
        top_k: 반환할 최대 결과 수
        filters: 필터 조건 (현재 미사용, 향후 확장 가능)

    Returns:
        검색 결과
    """
    try:
        rag_service = get_rag_service()

        # RAG 검색 수행
        search_result = rag_service.search(query=query, n_results=top_k)

        if "error" in search_result:
            logger.error(f"검색 오류: {search_result['error']}")
            return {"results": []}

        # 결과를 registry.yaml 스키마에 맞게 포맷팅
        results = []
        for i, item in enumerate(search_result["results"]):
            metadata = item.get("metadata", {})

            result = {
                "doc_id": metadata.get("title", f"doc_{i}"),  # title을 doc_id로 사용
                "title": metadata.get("title", "제목 없음"),
                "snippet": item.get("content", "")[:200] + "..." if len(item.get("content", "")) > 200 else item.get("content", ""),  # 내용의 일부를 snippet으로
                "metadata": {
                    "score": item.get("score", 0),
                    "category": metadata.get("category", ""),
                    "grade": metadata.get("grade", ""),
                    "effective_date": metadata.get("effective_date", "")
                }
            }
            results.append(result)

        return {"results": results}

    except Exception as e:
        logger.error(f"문서 검색 실패: {e}")
        return {"results": []}