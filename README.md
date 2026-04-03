# 🌤️ Air Quality BERT-Hybrid Service

"공공데이터의 객관적 수치와 사용자의 주관적 체감을 결합한 차세대 대기 질 분석 시스템"

---

## 🚀 프로젝트 개요
단순히 미세먼지 수치만 보여주는 것을 넘어, 사용자가 느끼는 실제 대기 상태를 BERT AI 모델로 분석하고 이를 실시간 DB 수치와 결합하여 **하이브리드 지수**를 산출합니다.

## 🏗️ 시스템 아키텍처
1. **Data Layer**: Airflow를 통해 수집된 공공데이터가 PostgreSQL(mart 스키마)에 적재됩니다.
2. **AI Layer**: 파이튜닝된 `klue/bert-base` 모델이 텍스트의 감성(안전/주의/위험)을 분류합니다.
3. **Service Layer**: FastAPI 서버가 DB 수치와 AI 결과를 가중 합산하여 최종 결과를 반환합니다.

## 📊 하이브리드 판정 로직 (Hybrid Decision Logic)
통계적 신뢰도와 사용자 체감을 모두 반영하기 위해 다음과 같은 가중치를 적용합니다.

$$Final Score = (DB 수치 점수 \times 0.4) + (AI 감성 점수 \times 0.6)$$

- **DB 점수**: PM10 수치에 따라 100(좋음) / 60(보통) / 20(나쁨) 차등 부여
- **AI 점수**: 긍정(안전) 문장 시 100점 / 부정(위험) 문장 시 30점 부여
- **최종 판정**: 
  - **80점 이상**: "매우 쾌적"
  - **50점 이상**: "주의 필요"
  - **50점 미만**: "외출 자제 권고"

## 🛠️ 실행 방법 (One-Click)
```bash
docker-compose up --build
```
실행 후 http://localhost:8000/docs (Swagger UI)에서 테스트 가능합니다.

---

## 🧠 2. 오늘 작업의 핵심 요약 (이해 쏙쏙 버전)

통계학 전공자로서 이 프로젝트의 본질을 한눈에 정리해 드릴게요. 오늘 우리는 **'데이터의 신뢰성'**과 **'모델의 서비스화'**를 동시에 잡았습니다.

### **① 데이터 흐름 (Pipeline)**
* **DB(`database.py`)**: `psycopg2`를 통해 SQL 쿼리를 날려 **최신 시계열 데이터**를 뽑아왔습니다. (통계 분석의 표본 추출 단계)
* **검증(`data_validator.py`)**: 결측치(999)나 이상치를 필터링하여 **데이터 무결성**을 확보했습니다. (전처리 단계)

### **② AI 모델 응용 (`predictor.py`)**
* BERT라는 거대한 인코더 기반 모델을 `pipeline`으로 감싸서 실시간 추론(Inference)을 가능하게 했습니다.
* 문장을 벡터로 만들고, 가중치 행렬을 곱해 **소프트맥스(Softmax)** 확률로 '감성 점수'를 냈습니다.

### **③ 하이브리드 산식 (`main.py`)**
* 객관적 지표(수치)와 주관적 지표(감성)를 **가중 평균(Weighted Average)** 냈습니다. 
* 단순 평균이 아니라 AI에 0.6을 준 이유는 "사람이 느끼는 체감이 서비스 만족도에 더 큰 영향을 준다"는 가정을 세운 것입니다.

---

## 🛠️ 3. 중복 리드미 정리하기

1. **폴더 안의 리드미 삭제:** `air-quality-ai-service/README.md` 파일은 이제 필요 없으니 삭제하셔도 됩니다.
2. **최종 Push:** 위 내용을 최상단 리드미에 저장한 후, VS Code 터미널에서 아래 명령어로 정리하세요.

```powershell
git pull origin main
git add .
git commit -m "docs: finalize main README and clean up duplicate"
git push origin main
