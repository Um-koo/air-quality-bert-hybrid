import psycopg2
from psycopg2.extras import RealDictCursor

class AirDatabase:
    """
    [데이터베이스 커넥터 클래스]
    PostgreSQL(Airflow 관리 DB)에 접속하여 분석에 필요한 
    실시간 미세먼지 수치 데이터를 가져오는 역할을 합니다.
    """

    def __init__(self):
        """
        DB 접속을 위한 설정값을 초기화합니다.
        이 설정은 docker-compose.yml 파일의 DB 서비스 설정과 일치해야 합니다.
        """
        self.conn_params = {
            # host.docker.internal: 도커 컨테이너 내부에서 호스트 PC의 로컬 DB에 접속할 때 사용하는 특수 주소입니다.
            "host": "host.docker.internal",
            "database": "airflow",         # 분석 대상 데이터가 적재된 DB 이름
            "user": "airflow",
            "password": "airflow",
            "port": 5433                  # 호스트 PC와 연결된 포트 번호
        }

    def get_latest_data(self, station_name="서울"):
        """
        지정한 관측소(station_name)에서 가장 최근에 측정된 데이터를 1건 조회합니다.
        
        Args:
            station_name (str): 조회할 지역 이름 (기본값: "서울")
            
        Returns:
            dict: {station_name, pm10, pm25, measured_at} 형태의 데이터 (없을 시 None)
        """
        try:
            # 1. DB 연결 (Connection) 생성
            # **self.conn_params는 딕셔너리 안의 설정값들을 풀어서 전달하라는 의미입니다.
            conn = psycopg2.connect(**self.conn_params)
            
            # 2. 커서(Cursor) 생성
            # RealDictCursor: 결과값을 (1, 2) 같은 튜플이 아닌 {'pm10': 1, 'pm25': 2} 같은 
            # 파이썬 딕셔너리 형태로 반환해주어 코드를 읽기 편하게 만듭니다.
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # 3. SQL 쿼리 실행
            # [통계적 관점] 시계열 데이터에서 가장 최신(Latest) 시점의 수치를 뽑기 위해 
            # ORDER BY measured_at DESC(내림차순 정렬)와 LIMIT 1을 조합합니다.
            # %s를 사용하는 이유는 SQL Injection 공격을 방지하기 위한 보안 규약입니다.
            query = """
                SELECT station_name, pm10, pm25, measured_at 
                FROM mart.air_quality 
                WHERE station_name = %s 
                ORDER BY measured_at DESC 
                LIMIT 1;
            """
            cur.execute(query, (station_name,))
            
            # 4. 결과 가져오기
            result = cur.fetchone()
            
            # 5. 자원 반납 (중요)
            # 사용이 끝난 통로는 닫아주어야 메모리 누수를 방지할 수 있습니다.
            cur.close()
            conn.close()
            
            return result
            
        except Exception as e:
            # DB 서버가 꺼져있거나 네트워크 문제 발생 시 에러 로그를 출력합니다.
            print(f"❌ DB 연결 에러: {e}")
            return None