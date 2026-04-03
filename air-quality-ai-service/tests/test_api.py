import requests

def test_predict(station, text):
    url = "http://localhost:8000/api/v1/predict"
    payload = {
        "station_name": station,
        "text": text
    }
    
    print(f"\n🚀 테스트 시작: [{station}] 데이터 요청 중...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"📡 서버 응답 상태: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"✅ 결과: {result['combined_message']}")
        else:
            print(f"🔴 차단됨: {result['warning']}")
    else:
        print(f"❌ 에러 발생: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # 케이스 1: 정상 데이터 (서울)
    test_predict("서울", "오늘 날씨가 정말 맑고 화창하네요!")
    
    # 케이스 2: 이상 데이터 (대구 999)
    test_predict("대구", "미세먼지 농도가 궁금합니다.")