FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지 설치
RUN pip install web3 python-dotenv fastapi uvicorn requests

COPY api_server.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "api_server.py"]
