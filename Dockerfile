FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /code

# 필수 라이브러리 설치 (캐시 없이 가볍게)
RUN pip install --no-cache-dir pika chromadb sentence_transformers fastapi uvicorn

# 소스 코드 복사 (Host의 app 폴더 -> 컨테이너의 /code/app)
COPY app ./app

# Python 경로 설정
ENV PYTHONPATH=/code

# 실행 명령어
CMD ["python", "-m", "app.worker"]
