# Air Quality AI Service (Hybrid Analyzer)

실시간 대기 질 데이터(PostgreSQL)와 BERT AI 모델을 결합한 하이브리드 분석 서비스입니다.

## 1. 개요 (Overview)
본 프로젝트는 공공데이터 기반의 실시간 미세먼지 수치와 사용자의 주관적인 체감 문장을 결합하여, 보다 정밀한 대기 질 가이드를 제공하는 것을 목적으로 합니다.

## 2. 시스템 구조 (Architecture)
- Framework: FastAPI (Python 3.9+)
- Database: PostgreSQL (Airflow 수집 데이터 연동)
- AI Model: BERT (Sentiment Analysis Fine-tuned)
- Infrastructure: Docker & Docker Compose

## 3. 핵심 기능 (Key Features)
- POST /api/v1/predict: 하이브리드 분석 (DB 수치 + AI 문장 분석)
- GET /api/v1/status/{station}: 실시간 수치 요약 정보 제공
- Data Validation: 999 등 이상치 데이터 자동 차단 및 필터링

## 4. 하이브리드 산식 (Hybrid Logic)
최종 판정은 아래와 같은 가중치 합산 점수로 결정됩니다.
- 수치 점수 (40%): PM10 농도에 따른 객관적 등급
- AI 점수 (60%): BERT 모델의 문장 긍정/부정 분석 등급
- 결과 분류: [매우 쾌적] / [주의 필요] / [외출 자제 권고]

## 5. 시작하기 (Quick Start)
저장소를 복제한 후 루트 폴더에서 아래 명령어를 입력하세요.

$ docker-compose up --build -d

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc