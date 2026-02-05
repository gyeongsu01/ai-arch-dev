# AI 아키텍처 프로젝트 공부 가이드

## 1. Conversation Overview
- **Primary Objectives**: 금융 RAG 시스템 구축, ChromaDB 벡터 데이터베이스 설정, PII 마스킹 적용, API 통합 및 테스트, 프로젝트 정리(.gitignore)
- **Session Context**: 초기 RAG 구축 요청 → ChromaDB 설정 → 데이터 임베딩 → 검색 기능 구현 → PII 마스킹 추가 → API 테스트 → 검증 스크립트 실행 → .gitignore 생성
- **User Intent Evolution**: 단순 RAG 구축에서 시작해 마스킹, 검증, 프로젝트 관리까지 확장

## 2. Technical Foundation
- **ChromaDB**: 벡터 데이터베이스, 문서 임베딩 저장 및 유사도 검색
- **Sentence Transformers**: 텍스트 임베딩 모델(paraphrase-MiniLM-L3-v2), 쿼리와 문서 벡터화
- **FastAPI**: 웹 API 프레임워크, /ask 엔드포인트 제공
- **LangGraph**: AI 워크플로우 관리, LLM과 도구 호출 상태 머신
- **Python 정규표현식**: PII 마스킹 패턴 구현

## 3. Codebase Status
### app/data/rag.py
- **Purpose**: ChromaDB와 임베딩 모델 관리
- **Current State**: RAGService 클래스, search/load_json_data 메서드 구현
- **Key Code Segments**: RAGService.__init__(ChromaDB 초기화), search(유사도 검색), load_json_data(JSON 데이터 로드)
- **Dependencies**: sentence_transformers, chromadb

### app/platform/policy.py
- **Purpose**: 보안 정책 및 PII 마스킹
- **Current State**: _mask_pii 함수에 주민등록번호, 전화번호, 이메일, 카드번호 패턴 추가
- **Key Code Segments**: _mask_pii(정규표현식 기반 마스킹), enforce(권한 검증)
- **Dependencies**: re 모듈

### app/service/tools.py
- **Purpose**: 도구 정의 및 실행
- **Current State**: doc_search 함수 통합, PII 마스킹 적용
- **Key Code Segments**: _tool_doc_search(RAG 검색 호출), get_tool_map(도구 맵핑)
- **Dependencies**: app.data.rag, app.platform.policy

### veriify_data.py
- **Purpose**: Retrieval Policy 검증
- **Current State**: 실제 VectorDB 데이터로 가중치 테스트
- **Key Code Segments**: run_data_test(검색 결과 점수 계산), run_vector_db_status(DB 상태 확인)
- **Dependencies**: app.data.retrieval_policy, app.data.rag

## 4. Problem Resolution
- **Issues Encountered**: PII 마스킹이 LLM 호출 후 적용되어 개인정보가 노출되는 문제, 모듈 경로 오류, JSON 데이터 로드 실패
- **Solutions Implemented**: graph.py에서 LLM 호출 전 마스킹 적용, PYTHONPATH 설정, load_json_data 메서드 수정
- **Debugging Context**: 마스킹 테스트 스크립트 실행, API 로그 확인으로 문제 식별
- **Lessons Learned**: 마스킹은 데이터 입력 단계에서 적용해야 효과적, 싱글톤 패턴으로 리소스 관리 효율적

## 5. Progress Tracking
- **Completed Tasks**: ChromaDB 설정, 금융 데이터 임베딩, RAG 검색 구현, PII 마스킹 적용, API 통합, 검증 스크립트 실행
- **Partially Complete Work**: Git 저장소 초기화 준비
- **Validated Outcomes**: RAG 검색 결과 확인, PII 마스킹 패턴 작동 검증, API 응답 정상

## 6. Active Work State
- **Current Focus**: 프로젝트 정리 및 Git 설정
- **Recent Context**: veriify_data.py 실행으로 VectorDB 상태 확인, uvicorn 서버 실행으로 API 테스트 완료
- **Working Code**: .gitignore 파일 생성
- **Immediate Context**: 요약 전에 .gitignore 생성 작업 중

## 7. Recent Operations
- **Last Agent Commands**: create_file 도구로 .gitignore 파일 생성
- **Tool Results Summary**: .gitignore 파일이 성공적으로 생성됨, Python 프로젝트 표준 항목 + ChromaDB, 가상환경 등 포함
- **Pre-Summary State**: .gitignore 생성 작업 중, 프로젝트 정리 단계
- **Operation Context**: RAG 시스템 구축 완료 후 프로젝트 관리를 위한 Git 설정, 사용자 목표(시스템 구축)의 마무리 단계

## 8. Continuation Plan
- **Git 저장소 초기화**: .gitignore 설정 후 git init, add, commit 실행
- **추가 검증**: 실제 금융 쿼리로 RAG 응답 테스트
- **문서화**: README.md 작성으로 프로젝트 설명
- **Priority Information**: Git 설정이 가장 긴급, 이후 추가 기능 확장 가능
- **Next Action**: "git init && git add . && git commit -m 'Initial RAG system implementation'" 실행
