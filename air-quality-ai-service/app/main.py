import logging
import os
from fastapi import FastAPI, HTTPException
from predictor import AirQualityPredictor
from database import AirDatabase
from data_validator import DataValidator
from .schemas import PredictionRequest, PredictionResponse

# ==========================================
# 1. 로깅 및 서비스 설정
# ==========================================

# 로그를 저장할 폴더가 없으면 자동으로 생성합니다.
os.makedirs("logs", exist_ok=True)

# 애플리케이션의 실행 기록(로그)을 설정합니다.
# 파일(app.log)과 터미널(Stream) 양쪽에 모두 기록을 남겨 추적이 용이하게 합니다.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 객체를 생성합니다. Swagger 문서 등에 표시될 메타 정보를 정의합니다.
app = FastAPI(
    title="Air Quality AI Service",
    description="실시간 DB 수치(PostgreSQL)와 BERT AI 모델을 결합한 하이브리드 대기 질 분석 서비스",
    version="1.0.0"
)

# ==========================================
# 2. 핵심 서비스 컴포넌트 초기화
# ==========================================
predictor = AirQualityPredictor()  # BERT 기반 감성 분석 모델 로드
db = AirDatabase()                 # PostgreSQL 데이터베이스 연결 관리
validator = DataValidator()        # 데이터 수치 유효성 검증기

def calculate_hybrid_score(db_pm10: float, ai_result: dict) -> str:
    """
    [하이브리드 산식 로직]
    객관적 수치(DB) 40%와 주관적 체감(AI) 60%를 결합하여 최종 상태를 판정합니다.
    
    Args:
        db_pm10 (float): DB에서 가져온 실제 미세먼지 농도
        ai_result (dict): BERT 모델이 분석한 문장 감성 결과 (label)
    
    Returns:
        str: 최종 판정 결과 메시지
    """
    
    # [Step 1] DB 미세먼지 수치에 따른 점수 산정 (객관적 지표)
    if db_pm10 < 30: 
        db_score = 100  # 좋음
    elif db_pm10 < 80: 
        db_score = 60   # 보통
    else: 
        db_score = 20   # 나쁨

    # [Step 2] AI 체감 문장에 따른 점수 산정 (주관적 지표)
    # 긍정/안전 내용이면 100점, 부정/위험 내용이면 30점을 부여합니다.
    ai_label = ai_result.get('label', '안전/좋음')
    ai_score = 100 if ai_label == '안전/좋음' else 30
    
    # [Step 3] 가중치 합산 (최종 점수 산출)
    # 수치보다는 사람이 느끼는 체감(AI)에 조금 더 높은 가중치(0.6)를 두었습니다.
    final_score = (db_score * 0.4) + (ai_score * 0.6)
    
    # [Step 4] 최종 점수에 따른 구간 판정
    if final_score >= 80: 
        return "매우 쾌적"
    elif final_score >= 50: 
        return "주의 필요"
    else: 
        return "외출 자제 권고"

# ==========================================
# 3. API 엔드포인트 (Routes)
# ==========================================

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_air_quality(query: PredictionRequest):
    """
    [종합 예측 API]
    특정 지역명과 체감 문장을 입력받아 하이브리드 분석 결과를 반환합니다.
    """
    logger.info(f"🔮 예측 요청 수신: 지역={query.station_name}, 텍스트={query.text[:15]}...")
    
    try:
        # 1. DB에서 해당 지역의 가장 최근 대기 데이터를 조회합니다.
        db_data = db.get_latest_data(query.station_name)
        if not db_data:
            logger.warning(f"❓ 데이터 없음: {query.station_name}")
            return {
                "status": "error",
                "station": query.station_name,
                "combined_message": f"현재 '{query.station_name}' 지역은 데이터 점검 중이거나 미지원 지역입니다."
            }

        # 2. 가져온 데이터의 수치가 정상적인지 검증합니다. (예: 999 같은 결측치 차단)
        pm10, pm25 = db_data['pm10'], db_data['pm25']
        is_ok, val_message = validator.is_valid(pm10, pm25)

        if not is_ok:
            logger.error(f"🚫 데이터 차단: {query.station_name} (수치: {pm10})")
            return {
                "status": "blocked",
                "station": query.station_name,
                "current_air": {"pm10": pm10, "pm25": pm25},
                "warning": val_message,
                "combined_message": f"⚠️ 경고: {val_message}"
            }

        # 3. BERT 모델을 통해 텍스트를 분석하고, 하이브리드 산식으로 최종 판정을 내립니다.
        ai_result = predictor.predict(query.text)
        final_decision = calculate_hybrid_score(pm10, ai_result)
        
        logger.info(f"✅ 분석 완료: {query.station_name} -> {final_decision}")

        # 4. 최종 결과 조립 및 반환
        return {
            "status": "success",
            "station": query.station_name,
            "current_air": {"pm10": pm10, "pm25": pm25},
            "ai_analysis": ai_result,
            "combined_message": f"[{final_decision}] 현재 {query.station_name} 수치는 {pm10}이며, AI 체감 분석은 '{ai_result['label']}'입니다."
        }

    except Exception as e:
        # 예상치 못한 시스템 에러 발생 시 로그를 남기고 500 에러를 반환합니다.
        logger.error(f"🔥 서버 에러 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@app.get("/api/v1/status/{station_name}")
async def get_air_status(station_name: str):
    """
    [간편 조회 API]
    텍스트 분석 없이 DB의 실시간 수치 데이터만 빠르게 확인합니다.
    """
    db_data = db.get_latest_data(station_name)
    if not db_data:
        return {"status": "error", "message": "데이터 없음"}
    
    pm10 = db_data['pm10']
    return {
        "status": "success",
        "station": station_name,
        "pm10": pm10,
        "summary": "쾌적" if pm10 < 35 else "주의"
    }

@app.get("/health")
def health_check():
    """앱의 가동 상태를 확인하기 위한 헬스체크 엔드포인트입니다."""
    return {"status": "ok"}