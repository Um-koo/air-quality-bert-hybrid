# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 현재 폴더의 모든 파일을 컨테이너의 /app으로 복사
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 실행 위치를 app 폴더 내부로 지정
ENV PYTHONPATH=/app/app

# 서버 실행 (app 폴더 안의 main.py를 실행)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]