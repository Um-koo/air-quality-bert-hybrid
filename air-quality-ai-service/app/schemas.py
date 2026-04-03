#app/schemas.py
ffrom pydantic import BaseModel, Field
from typing import Optional, Dict

# ============================================================
# [데이터 규격 정의서]
# 이 파일은 사용자와 서버 간의 '데이터 약속'을 정의합니다.
# Pydantic 라이브러리를 사용하여 입력 데이터의 타입을 강제로 검증합니다.
# ============================================================

class PredictionRequest(BaseModel):
    """
    [요청 규격] 사용자가 API를 호출할 때 보내야 하는 데이터 구조입니다.
    """
    # Field를 사용하면 Swagger UI 문서에 예시와 설명을 자동으로 추가해줍니다.
    # '...'은 이 값이 생략될 수 없는 '필수값'임을 의미합니다.
    station_name: str = Field(..., example="서울", description="조회할 측정소 이름 (예: 종로구, 강남구)")
    text: str = Field(..., example="오늘 미세먼지 어때?", description="사용자의 주관적 체감 분석을 위한 문장")

class PredictionResponse(BaseModel):
    """
    [응답 규격] 서버가 분석을 마치고 사용자에게 돌려줄 최종 리포트 구조입니다.
    """
    # 분석 작업의 성공 여부 (success / error / blocked)
    status: str
    
    # 조회된 지역 이름
    station: str
    
    # [객관적 수치 데이터] DB에서 가져온 실시간 PM10, PM25 농도
    # Optional은 데이터가 없을 수도 있다는 뜻이며, 기본값은 None입니다.
    current_air: Optional[Dict[str, float]] = None
    
    # [AI 분석 결과] BERT 모델이 도출한 label(안전/주의/위험) 및 confidence 점수
    ai_analysis: Optional[Dict] = None
    
    # [경고 메시지] 999 수치 차단이나 데이터 부재 시 사용자에게 알릴 내용
    warning: Optional[str] = None
    
    # [최종 통합 메시지] DB 수치와 AI 분석을 결합한 하이브리드 판정 결과 문장
    combined_message: str