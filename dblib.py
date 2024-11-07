import pymysql  # MySQL과 Python 간의 연결을 가능하게 하는 모듈
from pymysql import Error  # MySQL 연결 중 발생할 수 있는 오류 처리 모듈
import pandas as pd  # SQL 쿼리 결과를 DataFrame으로 처리하기 위한 Pandas 모듈

class DBUtil:
    def __init__(self, p_sql=""):
        self.sql_in = p_sql # sql 문 가져다올 변수
        # print(f'{self.sql_in}------sql문 잘가져옴')

    ### DB접속 및 커서 생성하기
    def initDB(self):
        self.initConnection()
        self.initCursor()

    ### 원래 oracle에 따르면 dsn 드라이버 연결하는자리인데 안들어가는 이유!!!
        # MySQL에서는 DSN 함수가 필요하지 않은 이유
        # MySQL은 DNS(도메인 네임 서비스) 또는 호스트 주소로 연결됩니다.
            # ex: localhost 또는 database-1.cn2waou22oc1.ap-northeast-2.rds.amazonaws.com
            # 같은 도메인 이름을 사용하여 MySQL 서버에 연결
        ## 따라서 MySQL에 연결할 때는 Oracle처럼 dsn을 설정할 필요가 없습니다.
        # MySQL에서는 host, user, password, database와 같은 기본적인 연결 정보만 필요합니다.

    # connect 접속 함수 : MySQL 데이터베이스에 연결하는 함수
    def initConnection(self):
        try:
            self.conn = pymysql.connect(
                # MySQL 서버 호스트 주소
                # MySQL 사용자 이름
                # MySQL 비밀번호
                # 사용할 데이터베이스 이름
                host="database-1.cn2waou22oc1.ap-northeast-2.rds.amazonaws.com",
                user="admin",
                password="dbsgml1234",
                database="csv"
            )
            print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
            self.conn = None

    # cursor 생성 함수
    def initCursor(self):
        if self.conn is None:
            print("No connection available.")
            return None
        self.cursor = self.conn.cursor()
        # print(f"커서 연결 완료.")
        return self.cursor

    # execute 실행 함수
    def initExecute(self):
        print(f"Executing SQL: {self.sql_in}")  # 쿼리 디버깅 출력
        self.cursor.execute(self.sql_in)
        # print("execute 실행성공.")
        #
        # except Error as e:
        #     print(f"The error '{e}' occurred")

    # 데이터를 Pandas DataFrame으로 반환하는 함수
    def getDataFrame(self):
        ### DB접속 및 커서 생성하기
        self.initDB()

        ### SQL 요청 및 응답 받아오기
        self.initExecute()

        ### 리스트 타입으로 조회됨
        # - 각 행들은 튜플 타입으로 되어 있음
        rows = self.cursor.fetchall()
        # print(f'getDataFrame내의 rows : {rows}')

        ## 커서가 가지고 있는 변수에서 컬럼 정보 추출하기
        columns = self.cursor.description
        # print(f'columns: {columns}')
        # - lower() : 대문자 컬럼명을 소문자로 변환
        columns_nm = [data[0].lower() for data in columns]
        # print(f'columns_nm: {columns_nm}')
        df = pd.DataFrame(rows, columns=columns_nm)

        self.closeDB()  # 최종적으로 리턴하기 전에 종료시키기 : 이러면 바로 닫겨서 매번 새로 생성해줘야한다.

        return df


### 잠깐!!! 현재 데이터가  [('John Doe','Jo Hyeonji')] <<요런 형태로 나오고 있다.
    # 그래서 그런식으로 되어있는 데이터가 John Doe < 요렇게 별개로 뽑아지는게 아닌가 했지만
    # 아니었다...
    # 원래 응답받은 결과를 가지고 있는 cursor는
    # 리스트 내에 튜플타입으로 되이있다. 웹에서도 동일.
    # 자세한것은 빅데이터 3기 수업 내용 : 01_파이썬에서_오라클_연동하기 참고.
    # 단지 웹환경에서 데이터를 써먹기 용이하도록 [{},{},...] 형태로 반환하는거였다!!!
    # 딕셔너리 형태로 만들면 컬럼명까지 라벨링된채로 들고와서 알차게 써먹을 수있으니까

    # 앱에서 사용할 [{},{}] 형식으로 반환하는 함수 (웹 응용 프로그램에서 사용 가능)
    def getListDict(self):
        # return self.getDataFrame().to_dict("records")
        return self.getDataFrame().to_dict("records")

    # 입력/수정/삭제(CUD) 작업을 처리하는 함수
    def setCUD(self):
        try:
            ### DB접속 및 커서 생성하기
            self.initDB()

            ### SQL 요청 및 응답 받아오기
            self.initExecute()

            ### 처리결과 추출하기
            # - 처리결과는 정수값으로 반환됩니다.
            # - rowcount : 해당되는 행갯수를 정수값으로 반환
            # - 정수값이 1이상이면 성공, 1미만이면 실패
            rs_cnt = self.cursor.rowcount

            ### 정상적으로 입력/수정/삭제가 되었다면 DB서버 메모리에 반영시키기
            # - 반영 : commit()
            # if rs_cnt >= 1 :
            #     self.conn.commit()

            self.conn.commit()

            # self.closeDB()

            return rs_cnt

        except Error as e:
            print(f"The error '{e}' occurred")
            self.conn.rollback()  # 오류 발생 시 롤백
            return None

    # DB접속 종료 함수 만들기 : closeDB()
    def closeDB(self):
        self.cursor.close()
        self.conn.close()
        print("MySQL connection closed")
