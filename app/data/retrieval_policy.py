# Data Reliability & Retrieval Policy
from __future__ import annotations
from typing import Any, Dict, List
import datetime as dt

# (예시) 신규/중요 문서 등급
# 점수: A=1.0, B=0.8, C=0.5 ...
TRUST_SCORES = {
    "A": 1.0,
    "B": 0.8,
    "C": 0.5,
    "U": 0.1  # Unknown
}

class RetrievalPolicy:
    """
    Data 신뢰성(Reliability)을 책임지는 정책 클래스.
    검색 전 필터링(Pre-filter)과 검색 후 스코어링(Post-scoring) 로직을 캡슐화.
    """

    def __init__(self, min_score_threshold: float = 0.4):
        self.min_score_threshold = min_score_threshold

    def apply_filters(self, docs: List[Dict[str, Any]], user_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        1차 필터링 (Metadata 기반)
        - 기본적으로 status='active'만 허용 (user_filters에 명시 없으면)
        """
        target_status = user_filters.get("status", "active")
        
        filtered = []
        for d in docs:
            meta = d.get("metadata", {})
            # 1) Status check
            if meta.get("status") != target_status:
                continue
            
            # 2) 만료일(expire_date) 체크 (예시)
            if "expire_date" in meta:
                # (실제론 날짜 파싱 필요하지만 여기선 문자열 비교 등으로 가정 or 생략)
                pass

            filtered.append(d)
        return filtered

    def score_document(self, doc: Dict[str, Any], query: str) -> float:
        """
        신뢰성 점수(Trust Score) + 관련성(Relevance) + 최신성(Recency) 종합 산출
        """
        meta = doc.get("metadata", {})
        
        # 1. 문서 신뢰 등급 (Trust)
        trust_grade = meta.get("grade", "U") # 기본 U
        trust_score = TRUST_SCORES.get(trust_grade, 0.1)

        # 2. 텍스트 관련성 (Relevance) - (MVP: naive keyword matching)
        text = (doc.get("title", "") + " " + doc.get("snippet", "")).lower()
        if query.lower() in text:
            relevance_score = 1.0
        else:
            relevance_score = 0.2

        # 3. 최신성 (Recency)
        recency_score = self._calc_recency(meta.get("effective_date"))

        # 종합 가중치 (비즈니스 로직에 따라 조정)
        # 예: 관련성(50%) + 신뢰도(30%) + 최신성(20%)
        final_score = (relevance_score * 0.5) + (trust_score * 0.3) + (recency_score * 0.2)
        
        return final_score

    def _calc_recency(self, effective_date: str | None) -> float:
        if not effective_date:
            return 0.5 # 중간값
        try:
            d = dt.date.fromisoformat(effective_date)
            now = dt.date.today()
            delta = (now - d).days
            # 1년(365일) 지나면 0에 수렴
            if delta < 0: return 0.5 # 미래 날짜?
            return max(0.0, 1.0 - (delta / 365.0))
        except:
            return 0.5

    def filter_by_score(self, scored_docs: List[tuple[float, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        최종 점수가 임계값(Threshold) 미만인 문서는 걸러냄 -> 품질 보장
        """
        results = []
        for score, doc in scored_docs:
            if score >= self.min_score_threshold:
                # 결과 반환 시 score도 같이 줄 수 있음
                doc["_score"] = round(score, 3)
                results.append(doc)
        return results
