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

---

## 9. 실습 기록: 2026-02-05

### 실습 목표
5계층 AI 아키텍처에서 Service Layer, Agent Layer, Domain Integrity를 강화하여 확장성, 오케스트레이션, 신뢰성을 확보한다.

### 9.1 Service Layer: 설정 기반의 유연한 확장성 확보 (Scalability)

#### 작업 내용
- **registry.yaml에 새로운 액션 추가**: `fin.calc_loan` (대출 상환액 계산)
- **tools.py에 도구 함수 구현**: `_tool_loan_calc` 함수 추가

#### 수정된 파일
1. **app/service/actions/registry.yaml**
   - 새로운 액션 `fin.calc_loan` 등록
   - 입력 스키마: `principal` (원금), `annual_rate` (연 이율 %), `months` (기간)
   - 출력 스키마: `monthly_payment` (월 상환액), `total_interest` (총 이자)
   - `audit_level: "NONE"`, `scopes_required: []` 설정

2. **app/service/tools.py**
   - `_tool_loan_calc(params)` 함수 구현
   - 상환 공식: `P * r * (1+r)^n / ((1+r)^n - 1)` 적용
   - `get_tool_map()`에 `"fin.calc_loan": _tool_loan_calc` 등록

#### 핵심 개념
- **설정 기반 확장**: YAML 파일에 액션 정의만 추가하면 새로운 도구를 쉽게 등록 가능
- **스키마 검증**: 입력/출력 스키마를 통해 데이터 정합성 보장
- **도구 맵핑**: `get_tool_map()` 딕셔너리로 액션 ID와 핸들러 함수 연결

---

### 9.2 Agent Layer: 자율적 오케스트레이션 및 의사결정 최적화 (Orchestration)

#### 작업 내용
- **graph.py에 디버깅 print 문 추가**: 의사결정 과정 추적
- **LLM 프롬프트 개선**: 정확한 매개변수 이름 사용 유도

#### 수정된 파일
1. **app/agent/graph.py**
   - `_agent_decide()`: 쿼리 시작, 도구 선택/미선택 시 출력 추가
   - `_execute_tool()`: 도구 실행 시작, 결과, 에러 시 출력 추가
   - 도구 설명에 필수 매개변수 정보 포함
   - LLM 프롬프트에 단위 변환 지침 추가

#### 디버깅 출력 예시
```
[DECIDE] Thinking... Query: 1억 원을 연 4.5% 금리로 30년 동안 빌리면?
[DECIDE] Tool Selected: fin.calc_loan Params: {'principal': 100000000, 'annual_rate': 4.5, 'months': 360}
[EXECUTE] Running tool: fin.calc_loan
[EXECUTE] Result: {'monthly_payment': 506685.18, 'total_interest': 82406665.2}
```

#### 핵심 개념
- **LLM 기반 의사결정**: `_agent_decide()`에서 LLM이 적절한 도구를 선택
- **관찰성(Observability)**: print 문으로 실행 흐름 추적
- **프롬프트 엔지니어링**: LLM이 스키마에 맞는 매개변수를 생성하도록 유도

---

### 9.3 Domain Integrity: 금융 로직의 정합성 및 할루시네이션 통제 (Reliability)

#### 작업 내용
- **스키마 검증 오류 해결**: LLM이 잘못된 매개변수 이름을 사용하는 문제 수정
- **프롬프트 개선으로 할루시네이션 방지**

#### 발생한 문제
- LLM이 `annual_interest_rate`, `loan_term_years` 대신 `annual_rate`, `months`를 사용해야 함
- 스키마 검증 실패: `schema_invalid: missing_required_field: annual_rate`

#### 해결 방법
1. **도구 설명에 필수 매개변수 명시**
   ```python
   required_fields = spec.input_schema.get("required", [])
   params_desc = f" (필수 매개변수: {', '.join(required_fields)})"
   ```

2. **LLM 프롬프트에 단위 변환 지침 추가**
   ```python
   system_prompt="... Use exact parameter names from the tool description. For loan calculation, convert years to months (e.g., 30 years = 360 months) and use percentage for rates."
   ```

#### 핵심 개념
- **스키마 기반 검증**: `enforce()` 함수에서 입력 데이터 검증
- **할루시네이션 통제**: LLM이 임의로 매개변수 이름을 생성하지 않도록 프롬프트로 제어
- **정합성 보장**: 금융 계산 로직이 정확한 입력을 받도록 보장

---

### 9.4 학습 포인트 요약

| 계층 | 목표 | 구현 방법 | 결과 |
|------|------|----------|------|
| Service Layer | Scalability | YAML 기반 액션 등록, 도구 맵핑 | 새 도구 쉽게 추가 가능 |
| Agent Layer | Orchestration | LLM 의사결정, 디버깅 출력 | 실행 흐름 추적 가능 |
| Domain Integrity | Reliability | 스키마 검증, 프롬프트 개선 | 할루시네이션 방지 |
