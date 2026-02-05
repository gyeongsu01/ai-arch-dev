import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
import json
import os

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        try:
            # ChromaDB 클라이언트 초기화 (에러 처리 추가)
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
            
            # 컬렉션 생성
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"description": "문서 검색용 벡터 컬렉션"}
            )
            
            logger.info("✅ RAG 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ RAG 서비스 초기화 실패: {e}")
            raise

    def load_json_data(self, json_path: str) -> bool:
        """JSON 파일에서 문서 로드 및 추가"""
        try:
            if not os.path.isfile(json_path):
                logger.error(f"❌ 파일이 존재하지 않음: {json_path}")
                return False
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                logger.error(f"❌ JSON 데이터 형식 오류: 리스트가 아님")
                return False
            
            # JSON 데이터를 documents 형식으로 변환
            documents = []
            for item in data:
                doc = {
                    "id": item.get("id", f"doc_{len(documents)}"),
                    "content": item.get("content", ""),
                    "metadata": {
                        "title": item.get("title", ""),
                        "grade": item.get("metadata", {}).get("grade", ""),
                        "effective_date": item.get("metadata", {}).get("effective_date", ""),
                        "category": item.get("metadata", {}).get("category", "")
                    }
                }
                documents.append(doc)

            # 벡터화 및 저장
            success = self.add_documents(documents)
            if success:
                logger.info(f"✅ {len(documents)}개 문서 로드 및 추가 완료")
            return success  # ✅ 항상 bool 반환
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 문서 로드 실패: {e}")
            return False

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """문서 추가 및 벡터화 (배치 처리로 메모리 효율적)"""
        try:
            batch_size = 10
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                texts = [doc["content"] for doc in batch]
                metadatas = [doc.get("metadata", {}) for doc in batch]
                ids = [doc.get("id", f"doc_{i+j}") for j, doc in enumerate(batch)]
                
                # 임베딩 생성 (배치 처리)
                embeddings = self.embedding_model.encode(texts, batch_size=batch_size).tolist()
                
                # ChromaDB에 저장
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logger.info(f"✅ {len(documents)}개 문서 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 문서 추가 실패: {e}")
            return False

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """유사도 검색 (에러 처리 강화)"""
        try:
            if not query.strip():
                return {"results": [], "error": "빈 쿼리"}
            
            # 쿼리 임베딩
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # 검색 실행
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, 10),  # 최대 10개로 제한
                include=['documents', 'metadatas', 'distances']
            )
            
            # 결과 포맷팅
            formatted_results = []
            if results['documents']:
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "score": round(1 - dist, 3)  # 코사인 유사도
                    })
            
            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"❌ 검색 실패: {e}")
            return {"results": [], "error": str(e)}

# 전역 인스턴스 (싱글톤 패턴)
_rag_instance = None

def get_rag_service() -> RAGService:
    """RAG 서비스 싱글톤 인스턴스 반환"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance

# 편의용 전역 변수
rag_service = get_rag_service()