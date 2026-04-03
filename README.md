# Air Quality BERT-Hybrid Service

AirKorea 수치 데이터와 BERT 기반 감성 분석을 결합하여  
실시간 DB 수치 → 주관적 체감 분석 → 하이브리드 지수 산출까지 이어지는  
AI 서비스 구조를 구축한 프로젝트

---

### 1. 프로젝트 개요
PostgreSQL(mart)에 적재된 실시간 대기 질 데이터를 활용하고,  
Fine-tuned BERT 모델을 통해 사용자의 체감 텍스트를 분석하여  
객관적 수치와 주관적 인식을 결합한 통합 분석 정보를 제공한다.  
이 프로젝트는 단순 수치 제공을 넘어,  
AI 모델을 실제 서비스 파이프라인에 이식하고 활용하는 것을 목표로 한다.

### 2. 목적
* 실시간 DB 수치와 AI 추론 결과의 결합 구조 설계
* BERT 모델의 서비스 환경(FastAPI) 이식 및 최적화
* Docker 기반의 독립적인 마이크로서비스 환경 구성
* 데이터 검증(Validator) 로직을 통한 분석 신뢰성 확보
* 하이브리드 가중치 산식을 통한 새로운 지표 제안

### 3. 시스템 구성
**PostgreSQL (mart.air_quality)**
→ **FastAPI Service**
→ **Data Validator (이상치 필터링)  **
→ **BERT Model (Sentiment Analysis)**  
→ **Hybrid Scoring Logic**
→ **API Response (JSON)**

### 4. 기술 스택
* **Language:** Python
* **Web Framework:** FastAPI
* **Database:** PostgreSQL
* **AI Model:** BERT (klue/bert-base)
* **Infra:** Docker, Docker-compose

### 5. 프로젝트 구조
```text
air-quality-ai-service/
    ├── app/
    │   ├── main.py (API 및 하이브리드 로직)
    │   ├── predictor.py (BERT 추론 모듈)
    │   ├── database.py (PostgreSQL 연동)
    │   ├── data_validator.py (데이터 정제)
    │   └── schemas.py (데이터 규격 정의)
    ├── data/ (학습 데이터셋)
    ├── tests/ (API 및 DB 테스트)
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md
```
### 6. 데이터 처리 및 분석 흐름

1. **API 호출**: 지역명(station_name)과 체감 문장(text) 수신
2. **DB 조회**: PostgreSQL mart 계층에서 해당 지역의 최신 PM10/PM2.5 데이터 취득
3. **데이터 검증**: DataValidator를 통한 결측치(999) 및 이상치 처리
4. **AI 추론**: 입력 문장을 BERT 모델에 투입하여 감성 레이블 및 확률 도출
5. **지수 산출**: DB 수치 점수(40%)와 AI 분석 점수(60%) 가중 합산
6. **결과 반환**: 통합 메시지 및 분석 리포트 생성

### 7. 실행 방법

#### 7.1 서비스 빌드 및 실행

아래 명령어를 실행하면 컨테이너 기반의 전체 서비스가 빌드 및 구동된다.
```bash
docker-compose up --build
```
#### 7.2 API 엔드포인트 확인

서버 구동 후 다음 주소에서 인터랙티브 문서(Swagger UI)를 확인할 수 있다.
* URL: http://localhost:8000/docs

### 8. 하이브리드 분석 설계

본 프로젝트는 수치 데이터의 한계를 보완하기 위해 AI 분석값을 결합한 산식을 적용한다.

#### 8.1 가중치 적용 (Weighted Sum)

* 객관적 지표 (DB): PM10 농도 기준 (가중치 0.4)
* 주관적 지표 (AI): BERT 감성 분석 결과 (가중치 0.6)

#### 8.2 점수 산정 기준

* DB Score: 좋음(100) / 보통(60) / 나쁨(20)
* AI Score: 안전·좋음(100) / 주의·위험(30)
* 최종 판정: 80점 이상(매우 쾌적), 50점 이상(주의), 50점 미만(권고)

### 9. 코드 기반 검증 및 쿼리 로직

#### 9.1 데이터 무결성 검증 (DataValidator)

```python
# 결측치 및 이상치 필터링 로직
if pm10 == 999 or pm10 > 500:
    return False, "측정소 점검 또는 센서 오류"
```
#### 9.2 DB 연동 및 쿼리 (Database)

```sql
-- 마트 계층의 최신 수치 데이터 조회
SELECT station_name, pm10, pm25, measured_at 
FROM mart.air_quality 
WHERE station_name = %s 
ORDER BY measured_at DESC 
LIMIT 1;
```
### 10. 서비스 안정성 및 최적화
#### 10.1 모델 추론 최적화
Singleton 인스턴스: 모델 로딩 부하 방지를 위해 Predictor 객체를 전역 생성하여 재사용

#### 10.2 시스템 견고성 확보
Robustness: 999 수치(공공데이터 결측치) 및 이상치에 대한 예외 처리 로직 구현

Schema Validation: Pydantic을 이용한 입출력 데이터 규격 강제

#### 10.3 운영 가시성
Logging 체계: logs/app.log를 통한 요청 처리 과정 및 에러 추적

### 11. 향후 확장
다중 언어 지원을 위한 다국어 BERT 모델 교체

이미지 데이터(CCTV) 분석 연동을 통한 멀티모달 서비스 확장

Redis 도입을 통한 빈번한 조회 지역 캐싱 처리

### 12. 작성자
Um-koo

