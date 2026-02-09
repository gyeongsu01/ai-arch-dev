import os
import json
import time
import pika
# 기존에 만들어둔 RAG 로직 재사용
from app.data.rag import RAGService 

# K8s 환경 변수 (없으면 기본값)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "embedding_queue"

def process_message(ch, method, properties, body):
    """메시지 처리: 문서를 받아 임베딩 후 DB 저장"""
    print(f" [x] Task Received")
    try:
        doc_data = json.loads(body)
        title = doc_data.get('title', 'Untitled')
        content = doc_data.get('content', '')
        
        print(f"Processing document: {title}")
        
        # RAG 서비스 초기화 (ChromaDB 연결)
        rag = RAGService()
        
        # 문서가 리스트 형태가 아니면 리스트로 변환 (RAGService 규격 맞춤)
        # 실제로는 여기서 Text Splitter 등을 수행해야 하지만, 일단 통째로 저장
        rag.load_json_data([doc_data]) 
        
        print(f"Successfully embedded: {title}")
        
        # 작업 완료 통보 (ACK)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f" [!] Error processing {doc_data.get('title')}: {e}")
        # 에러 시 메시지를 다시 큐에 넣지 않음 (무한 루프 방지) -> Dead Letter Queue가 정석이지만 여기선 Nack
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    
    # RabbitMQ가 뜰 때까지 기다리는 재시도 로직
    while True:
        try:
            print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
            )
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 5s...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(' [*] Worker Ready. Waiting for messages...')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    channel.start_consuming()

if __name__ == "__main__":
    main()