# app/data_validator.py

cclass DataValidator:
    """
    [데이터 품질 검증 및 점수 산출 클래스]
    DB에서 가져온 실시간 대기 질 수치가 분석에 적합한지 검사하고,
    하이브리드 분석을 위한 객관적 점수를 생성합니다.
    """
    def __init__(self):
        # [통계적 임계값 설정] 대한민국 환경부 대기환경 기준 및 센서 특성을 참고한 범위입니다.
        self.pm10_max = 500  # PM10이 500을 넘으면 대기 상태가 아닌 '센서 오류' 혹은 '결측치(999)'로 간주합니다.
        self.pm10_min = 0    # 농도는 음수(-)가 될 수 없습니다.
        self.pm25_max = 300  # 초미세먼지(PM2.5)에 대한 물리적 한계치 설정
        self.pm25_min = 0

    def is_valid(self, pm10: float, pm25: float):
        """
        데이터가 정상 범위 내에 있는지 확인하여 이상치를 차단합니다.
        
        Args:
            pm10 (float): 미세먼지 농도
            pm25 (float): 초미세먼지 농도
            
        Returns:
            tuple: (유효 여부: bool, 메시지: str)
        """
        # 1. 결측치 체크 (Missing Value Handling)
        # DB에서 NULL이 넘어오거나 데이터가 유실된 경우를 먼저 잡아냅니다.
        if pm10 is None or pm25 is None:
            return False, "⚠️ 수치가 비어있습니다. (NULL 감지)"

        # 2. 미세먼지(PM10) 범위 체크 (Range Check)
        # 물리적으로 불가능한 수치나 공공데이터 결측치 표기법(999 등)을 필터링합니다.
        if not (self.pm10_min <= pm10 <= self.pm10_max):
            return False, f"⚠️ 미세먼지(PM10) 수치 이상: {pm10} (측정소 점검 또는 오류 의심)"

        # 3. 초미세먼지(PM2.5) 범위 체크
        if not (self.pm25_min <= pm25 <= self.pm25_max):
            return False, f"⚠️ 초미세먼지(PM25) 수치 이상: {pm25}"

        return True, "정상"

    def get_quality_score(self, pm10: float):
        """
        [객관적 수치 점수화]
        미세먼지 농도를 바탕으로 20~100점 사이의 점수를 부여합니다.
        이 점수는 나중에 BERT 모델이 판단한 주관적 점수와 가중 합산(Weighted Sum)됩니다.
        
        Args:
            pm10 (float): 미세먼지 농도
            
        Returns:
            int: 오염도 점수 (점수가 높을수록 대기 질이 나쁨을 의미)
        """
        # 환경부 등급 기준(좋음-보통-나쁨-매우나쁨)에 따른 페널티 점수 부여
        if pm10 <= 30: 
            return 20   # [좋음] 가장 낮은 오염 점수
        if pm10 <= 80: 
            return 50   # [보통] 중간 수준의 오염 점수
        if pm10 <= 150: 
            return 80  # [나쁨] 높은 오염 점수
        
        return 100      # [매우나쁨] 최대 오염 점수