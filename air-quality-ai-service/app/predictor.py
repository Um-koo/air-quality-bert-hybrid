import re
import time
import os
from transformers import pipeline

class AirQualityPredictor:
    """
    [AI 모델 추론 클래스]
    BERT 모델을 로드하고, 사용자 문장을 입력받아 대기 질에 대한 
    주관적 감성(안전, 주의, 위험)을 분류하는 역할을 합니다.
    """

    def __init__(self, model_name="/app/app/models/fine_tuned_bert"):
        """
        클래스 생성 시 모델을 메모리에 올립니다. (Inference Engine 초기화)
        
        Args:
            model_name (str): 파인튜닝된 BERT 모델이 저장된 로컬 경로
        """
        
        # 1. 모델 경로 존재 여부 확인 (예외 처리)
        # 도커 환경에서 모델 파일이 누락되었을 경우를 대비해 기본 모델(KLUE-BERT)로 폴백합니다.
        if not os.path.exists(model_name):
            print(f"⚠️ 경고: 학습된 모델 폴더를 찾을 수 없습니다 ({model_name}). 기본 모델로 로딩합니다.")
            model_name = "klue/bert-base"
        
        print(f"⏳ BERT 모델 로딩 중: {model_name}... (이 작업은 수 초가 소요될 수 있습니다)")
        
        # 2. HuggingFace Pipeline 설정
        # 'text-classification': 텍스트 분류 태스크를 수행하겠다는 선언입니다.
        # 내부적으로 [Tokenizer -> Model -> Post-processor]가 연결된 파이프라인이 생성됩니다.
        self.classifier = pipeline(
            "text-classification", 
            model=model_name, 
            tokenizer=model_name
        )
        
        # 3. 레이블 매핑 (Label Indexing)
        # 모델은 숫자(LABEL_0 등)를 뱉으므로, 이를 통계적 의미가 있는 한글 텍스트로 변환합니다.
        # 주의: 학습 시 사용한 LabelEncoder의 순서와 반드시 일치해야 합니다.
        self.label_map = {
            "LABEL_0": "안전/좋음",
            "LABEL_1": "주의/보통",
            "LABEL_2": "위험/매우나쁨"
        }
        print("✅ 똑똑해진 BERT 모델 로드 완료!")

    def predict(self, text: str):
        """
        입력된 문장을 분석하여 감성 분류 결과를 반환합니다.
        
        Args:
            text (str): 사용자가 입력한 체감 문장 (예: "오늘 하늘이 너무 뿌옇네요")
            
        Returns:
            dict: 분석 결과 (레이블, 신뢰도 점수, 처리 시간 등)
        """
        # [성능 측정 시작] API 응답 속도(Latency) 관리를 위해 시간을 측정합니다.
        start_time = time.time()
        
        # 1. 텍스트 전처리 (Data Cleaning)
        # 정규표현식(re)을 사용하여 한글, 영문, 숫자, 공백을 제외한 특수문자를 제거합니다.
        # 이는 토크나이저의 불필요한 연산을 줄이고 예측 성능을 안정화하는 데 도움을 줍니다.
        clean_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
        
        # 2. 모델 추론 (Inference)
        # self.classifier는 내부적으로 다음 과정을 거칩니다:
        #   a) 문장을 숫자 벡터(Tokens)로 변환
        #   b) BERT 모델에 통과시켜 로짓(Logit) 값 산출
        #   c) Softmax를 통해 확률값(Score) 계산
        result = self.classifier(clean_text)[0]
        
        # [성능 측정 종료]
        latency = time.time() - start_time
        
        # 3. 결과 해석 (Post-processing)
        original_label = result['label']  # 예: "LABEL_0"
        korean_label = self.label_map.get(original_label, original_label)
        
        # 4. 모니터링용 로그 출력
        # 실제 서비스 운영 시 어떤 문장이 들어오고 결과가 무엇인지 터미널에서 확인하기 위함입니다.
        print(f"🔍 [Inference] Text: {clean_text[:15]}... | Label: {korean_label} | Time: {latency:.4f}s")
        
        # 5. 최종 결과 반환 (JSON 형식으로 API 응답에 전달됨)
        return {
            "original_sentence": text,        # 원문
            "clean_sentence": clean_text,      # 전처리된 문장
            "original_label": original_label,  # 모델의 원본 레이블
            "label": korean_label,            # 한글화된 레이블
            "confidence": round(result['score'], 4), # 신뢰도 (확률값 0~1)
            "latency_seconds": round(latency, 4)     # 추론 소요 시간
        }

# FastAPI 앱 시작 시 딱 한 번만 인스턴스를 생성하여 메모리에 상주시키도록 합니다. (Singleton 패턴 유사)
# 이렇게 해야 요청마다 모델을 새로 로드하는 대참사(엄청난 지연 시간)를 막을 수 있습니다.
# predictor = AirQualityPredictor()