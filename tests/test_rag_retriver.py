from app.data.rag import rag_service

def test_rag():
    print("🔍 RAG 검색 테스트\n")
    
    queries = ["금리 정보", "투자 전략", "부동산"]
    
    for query in queries:
        print(f"--- '{query}' 검색 ---")
        result = rag_service.search(query, n_results=2)
        
        if result.get("error"):
            print(f"❌ 오류: {result['error']}\n")
            continue
            
        print(f"📊 결과 {result['total_found']}개 발견")
        for i, item in enumerate(result["results"], 1):
            print(f"  {i}. 점수: {item['score']:.3f}")
            print(f"     카테고리: {item['metadata'].get('category', 'N/A')}")
            print(f"     내용: {item['content'][:80].strip()}...")
        print()

if __name__ == "__main__":
    test_rag()