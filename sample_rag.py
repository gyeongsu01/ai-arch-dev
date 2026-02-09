from app.data.rag import rag_service

def init_sample_documents():
    """샘플 문서로 RAG 초기화"""
    sample_docs = [
        {
            "id": "interest_rate_2025",
            "content": """
            최신 금리 정보 (2025-12-01 기준):
            - 한국은행 기준금리: 3.5%
            - 시중은행 변동금리: 4.2% ~ 5.1%
            - 예금금리: 3.0% ~ 3.8%
            - 대출금리: 4.5% ~ 6.2%
            
            최근 금리 동향:
            - 인플레이션 안정으로 기준금리 동결 유지
            - 시장 금리는 소폭 상승 추세
            """,
            "metadata": {
                "category": "finance",
                "date": "2025-12-01",
                "source": "bank_report"
            }
        },
        {
            "id": "market_trends_2025",
            "content": """
            2025년 금융시장 전망:
            - 주식시장: 기술주 중심 상승 예상
            - 부동산: 금리 안정으로 수요 증가
            - 암호화폐: 규제 강화로 변동성 확대
            
            투자 전략:
            - 분산 투자 권장
            - 장기적 관점 유지
            """,
            "metadata": {
                "category": "finance", 
                "date": "2025-12-01",
                "source": "market_analysis"
            }
        }
    ]
    
    rag_service.add_documents(sample_docs)
    print(f"✅ {len(sample_docs)}개 문서가 RAG에 추가되었습니다.")

if __name__ == "__main__":
    init_sample_documents()