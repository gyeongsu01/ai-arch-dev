import os
import json
import pika
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# RabbitMQ 설정 (환경변수 없으면 서비스명 사용)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "embedding_queue")

class DocumentRequest(BaseModel):
    content: str

def publish_message(message: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2))
        connection.close()
    except Exception as e:
        print(f"MQ Error: {e}")

@app.post("/ingest")
def ingest_document(request: DocumentRequest):
    print(f"Received content: {request.content}")
    publish_message({"type": "ingest", "content": request.content})
    return {"status": "queued", "content": request.content}

@app.get("/")
def health_check():
    return {"status": "healthy"}
