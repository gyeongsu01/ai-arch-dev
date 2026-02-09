# verify_data.py
import datetime as dt
from app.data.retrieval_policy import RetrievalPolicy
from app.data.rag import rag_service  # 실제 RAG 서비스 사용

def run_data_test():
    print("=== [Data Layer] Retrieval Policy(실제 VectorDB 데이터) 검증 ===\n")

    # 1. 정책 초기화
    policy = RetrievalPolicy(min_score_threshold=0.4)
    
    # 2. 실제 VectorDB에서 데이터 검색
    query = "금리 대출"  # 금융 관련 쿼리
    search_result = rag_service.search(query, n_results=10)  # 최대 10개 가져오기
    
    if not search_result.get("results"):
        print("❌ VectorDB에 데이터가 없거나 검색 실패")
        return
    
    print(f"🔎 Query: '{query}' (실제 VectorDB 검색 결과 사용)\n")
    print(f"{'Rank':<5} | {'ID':<15} | {'Total':<6} | {'Trust':<6} | {'Recency':<8} | {'제목'}")
    print("-" * 100)

    # 3. 실제 검색 결과로 점수 재계산
    scored_results = []
    for item in search_result["results"]:
        # 실제 검색 결과에서 metadata 추출
        metadata = item.get("metadata", {})
        
        # RetrievalPolicy용 문서 형식으로 변환
        doc = {
            "id": metadata.get("id", "unknown"),
            "title": metadata.get("title", ""),
            "snippet": item.get("content", "")[:100] + "...",  # 100자 제한
            "metadata": {
                "grade": metadata.get("grade", "U"),
                "effective_date": metadata.get("effective_date", ""),
                "status": "active"
            }
        }
        
        # 점수 계산 (실제 relevance + 가중치)
        score = policy.score_document(doc, query)
        
        scored_results.append((score, doc, metadata.get("grade", "U")))

    # 점수 높은 순 정렬
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # 4. 결과 출력
    for rank, (score, doc, grade) in enumerate(scored_results, 1):
        title = doc['title'][:30] + "..." if len(doc['title']) > 30 else doc['title']
        print(f"{rank:<5} | {doc['id']:<15} | {score:.3f}  | {grade:<6} | {doc['metadata'].get('effective_date', 'N/A'):<8} | {title}")

    print("-" * 100)
    
    # 5. 검증 결과 판정
    if scored_results:
        first_place = scored_results[0][1]
        print(f"\n🏆 1위 문서: {first_place['title']}")
        print(f"   신뢰도: {first_place['metadata']['grade']}")
        print(f"   날짜: {first_place['metadata']['effective_date']}")
        print(f"   총점: {scored_results[0][0]:.3f}")
        
        # A등급 문서가 상위에 있는지 확인
        a_grade_count = sum(1 for _, doc, _ in scored_results[:3] if doc['metadata']['grade'] == 'A')
        if a_grade_count >= 1:
            print("✅ 결과: 신뢰도 A등급 문서가 상위권에 포함됨")
        else:
            print("⚠️ 결과: 신뢰도 A등급 문서가 상위권에 없음 (가중치 조정 필요)")
    else:
        print("\n❌ 결과: 검색 결과 없음")

def run_vector_db_status():
    """VectorDB 상태 확인"""
    print("\n=== [Data Layer] VectorDB 상태 확인 ===\n")
    
    try:
        # ChromaDB 컬렉션 정보
        collection = rag_service.collection
        total_docs = collection.count()
        
        print(f"📊 총 문서 수: {total_docs}")
        
        if total_docs > 0:
            # 샘플 문서 확인
            results = collection.get(limit=3, include=['metadatas'])
            print(f"📄 샘플 문서:")
            for i, meta in enumerate(results['metadatas'], 1):
                print(f"   {i}. ID: {meta.get('id', 'N/A')}, Grade: {meta.get('grade', 'N/A')}, Date: {meta.get('effective_date', 'N/A')}")
        
        return total_docs > 0
        
    except Exception as e:
        print(f"❌ VectorDB 연결 실패: {e}")
        return False

if __name__ == "__main__":
    # VectorDB 상태 먼저 확인
    if run_vector_db_status():
        run_data_test()
    else:
        print("❌ VectorDB에 데이터가 없어 테스트를 진행할 수 없습니다.")
        print("💡 먼저 sample_rag.py를 실행해서 데이터를 로드하세요.")