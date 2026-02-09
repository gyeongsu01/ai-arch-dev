# verify_platform.py
import time
from app.common.types import UserContext
from app.platform.audit import write_audit, build_audit_event 
from app.platform.policy import enforce, Deny

# --- 테스트를 위한 Mock(모의) 객체 ---
class MockActionSpec:
    def __init__(self, scopes, schema):
        self.scopes_required = scopes
        self.input_schema = schema
        self.id = "mock_search" # Audit 테스트용 ID 추가

# --- 테스트 시나리오 ---
def run_tests():
    print("=== [Platform Layer] 검증 시작 ===\n")

    # 1. 사용자 및 도구 정의
    admin_user = UserContext(id="admin_kim", role="admin", scopes=["search.read", "admin"])
    guest_user = UserContext(id="guest_lee", role="guest", scopes=["search.read"])
    
    # 검색 도구 명세
    search_spec = MockActionSpec(
        scopes=["search.read"], 
        schema={"required": ["query"]}
    )

    # ---------------------------------------------------------
    # [Test 1] PII 마스킹 (개인정보 가리기)
    # ---------------------------------------------------------
    print("Test 1: PII(개인정보) 마스킹 테스트")
    unsafe_params = {
        "query": "내 전화번호는 010-1234-5678 이고, 메일은 test@example.com 입니다."
    }
    
    try:
        # enforce 함수가 실행되면서 내부적으로 _mask_pii가 동작해야 함
        safe_params = enforce(admin_user, search_spec, unsafe_params)
        print(f"   [Input]  {unsafe_params['query']}")
        print(f"   [Output] {safe_params['query']}")
        
        if "<PHONE_MASKED>" in safe_params['query'] or "<EMAIL_MASKED>" in safe_params['query']:
            print("   -> 결과: 성공 (개인정보가 가려짐)")
        else:
            print("   -> 결과: 실패 (마스킹 안됨)")
            
    except Exception as e:
        print(f"   -> 에러 발생: {e}")
    print("-" * 50)


    # ---------------------------------------------------------
    # [Test 2] Audit 로깅 (감사 로그)
    # ---------------------------------------------------------
    print("Test 2: Audit 로그 기록 확인")
    
    # 현재 구조상 enforce()가 자동으로 audit을 남기지 않으므로,
    # 시스템이 Audit을 남기는 상황을 시뮬레이션합니다.
    try:
        # 1. 이벤트 생성
        audit_event = build_audit_event(
            trace_id="trace_test_001",
            user_id=admin_user.id,
            action_id=search_spec.id,
            decision="PERMIT",
            params=safe_params, # 위에서 마스킹된 파라미터 기록
            reason="policy_passed"
        )
        
        # 2. 로그 기록 (화면 출력 확인)
        print("   [Log Write 시도]...")
        write_audit(audit_event)
        print("   -> 결과: 성공 (로그가 기록됨)")
        
    except Exception as e:
        print(f"   -> 결과: 실패 ({e})")
    
    print("-" * 50)


    # ---------------------------------------------------------
    # [Test 3] Rate Limit (도배 방지)
    # ---------------------------------------------------------
    print("Test 3: Rate Limit (속도 제한) 테스트")
    # policy.py 내부의 _RATE_LIMIT_STORE를 확인
    
    print("   -> 연속 호출 시도 중...")
    blocked_count = 0
    
    # 이미 앞선 테스트에서 호출이 있었으므로, 추가로 호출하며 차단 확인
    for i in range(1, 15):
        try:
            enforce(guest_user, search_spec, {"query": f"test_{i}"})
            # print(f"   - {i}회: 허용됨") 
        except Deny as e:
            if "rate_limit" in str(e):
                print(f"   - {i}회차부터 차단됨 (Rate Limit 작동 확인)")
                blocked_count += 1
                break # 차단 확인되면 루프 종료
            else:
                print(f"   - {i}회: 다른 에러 ({e})")
                
    if blocked_count > 0:
        print("   -> 결과: 성공 (Rate Limit 작동 확인)")
    else:
        print("   -> 결과: 실패 (모두 허용됨 - 제한 수치나 윈도우 확인 필요)")

if __name__ == "__main__":
    run_tests()