# test_db_logic.py
from database import AirDatabase       # 'app.'을 제거
from data_validator import DataValidator # 'app.'을 제거

def test_integration():
    db = AirDatabase()
    validator = DataValidator()
    
    # 1. DB에서 가장 최근 데이터 가져오기 (아까 넣은 '대구' 999 수치를 테스트)
    print("\n📡 DB에서 최신 데이터를 조회합니다...")
    target_station = "대구"
    data = db.get_latest_data(target_station)
    
    if data:
        print(f"✅ 조회 성공: {data}")
        
        # 2. Validator로 수치 검증
        pm10 = data['pm10']
        pm25 = data['pm25']
        
        is_ok, message = validator.is_valid(pm10, pm25)
        
        print(f"\n🛡️  데이터 검증 결과 ({target_station}):")
        if is_ok:
            print(f"🟢 [통과] {message}")
        else:
            print(f"🔴 [차단] {message}")
    else:
        print(f"❌ '{target_station}' 데이터를 찾을 수 없습니다. DB의 mart.air_quality 테이블을 확인하세요.")

if __name__ == "__main__":
    test_integration()