import redis
import pika
import sys

def check_redis():
    print("🔄 Redis 연결 시도 중...", end=" ")
    try:
        # 포트 포워딩된 로컬 주소와 비밀번호(redispassword) 사용
        r = redis.Redis(host='localhost', port=6379, password='redispassword', decode_responses=True)
        if r.ping():
            print("✅ 성공! (PONG)")
            return True
    except Exception as e:
        print(f"\n❌ Redis 실패: {e}")
        return False

def check_rabbitmq():
    print("🔄 RabbitMQ 연결 시도 중...", end=" ")
    try:
        # 포트 포워딩된 로컬 주소와 계정(user/rabbitmqpassword) 사용
        credentials = pika.PlainCredentials('user', 'rabbitmqpassword')
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        
        if connection.is_open:
            print("✅ 성공! (Connection Open)")
            connection.close()
            return True
    except Exception as e:
        print(f"\n❌ RabbitMQ 실패: {e}")
        return False

if __name__ == "__main__":
    print("--- 📡 인프라 연결 테스트 시작 ---")
    redis_status = check_redis()
    rabbit_status = check_rabbitmq()
    print("--------------------------------")
    
    if redis_status and rabbit_status:
        print("🎉 모든 시스템 정상! Mission 2-3 완료.")
    else:
        print("⚠️ 실패: 포트 포워딩이 켜져 있는지 확인해주세요.")