# from csvtest_real1 import dblib
import dblib
## 위의 폴더명은 나중에 바꿔줄것!!

### DBUtil 클래스 최초 한번 생성해 놓기
# - views.py에서(여기서는 main.
# # main 페이지 이름 표시py) import하는 시점에 생성됩니다.
dbutil = dblib.DBUtil()
from datetime import datetime

###########################[index.py 메인페이지]#########################################
# 메인페이지
def update_index_member_name(mem_id):
    print(f"[Start] update_index_member_name({mem_id}) ..................................")
    dbutil.sql_in = f"""
        SELECT MEM_NAME as mem_name
        FROM MEMBER 
        WHERE MEM_ID = '{mem_id}'
    """
    rows = dbutil.getListDict()
    print(f"[End] update_index_member_name() 결과값 = {rows}..................................")
    return rows

##############################[signup.py 회원가입 페이지]#################################
# 회원가입
# @staticmethod
def insert_into_user(mem_id, password, name, nickname, phone, address, regno1, regno2, regimage):
    print(f"[Start] insert_into_user({mem_id}, {password}, {name}, {nickname}, {phone}, {address}, {regno1}, {regno2}, {regimage}) ..................................")
    dbutil.sql_in = f"""
        INSERT INTO MEMBER 
        (mem_id, mem_pass, mem_name, mem_nick, mem_tel, mem_add, mem_regno1, mem_regno2, mem_regimage)
        VALUES ('{mem_id}', '{password}', '{name}', '{nickname}', '{phone}', '{address}', '{regno1}', '{regno2}', '{regimage}')
    """
    row = dbutil.setCUD()
    print(f"[End] insert_into_user() 결과값 = {row}..................................")
    return row

# 주어진 아이디가 유효한지 확인하는 메서드 (사용자가 존재하는지 확인)
# @staticmethod
def is_Valid(mem_id):
    print(f"[Start] is_Valid({mem_id}) ..................................")
    dbutil.sql_in = f"""
        SELECT * FROM csv.MEMBER 
        WHERE MEM_ID = '{mem_id}'
    """
    rows = dbutil.getListDict()
    print(f"[End] is_Valid() 결과값 = {rows}..................................")
    return len(rows) > 0



##############################[login.py 로그인 페이지]#################################
# 주어진 이메일과 비밀번호로 사용자가 존재하는지 확인
# @staticmethod
def isExist(mem_id, password):
    print(f"[Start] is_Exsist({mem_id}, {password}) ..................................")
    dbutil.sql_in = f"""
        SELECT * FROM csv.MEMBER 
        WHERE MEM_ID = '{mem_id}' and MEM_PASS = '{password}'
    """
    rows = dbutil.getListDict()
    print(f"[End] is_Exsist() 결과값 = {rows}..................................")
    if rows:
        return True  # 사용자가 존재함
    else:
        return False  # 사용자가 존재하지 않음

# ID 찾기 화면
# @staticmethod
def getID(mem_name, mem_tel, mem_birth):
    print(f"[Start] getID({mem_name}, {mem_tel}, {mem_birth}) ..................................")
    dbutil.sql_in = f"""
        SELECT MEM_ID FROM csv.MEMBER 
        WHERE MEM_NAME = '{mem_name}' 
          and MEM_TEL = '{mem_tel}' 
          and MEM_REGNO1 = '{mem_birth}'
    """
    rows = dbutil.getListDict()
    print(f"[End] getID() 결과값 = {rows}..................................")
    return rows


# PW 찾기 화면
# @staticmethod
def getPW(mem_id, mem_tel, mem_regno1, mem_regno2):
    print(f"[Start] getPW({mem_id}, {mem_tel}, {mem_regno1}, {mem_regno2}) ..................................")
    dbutil.sql_in = f"""
        SELECT MEM_PASS FROM csv.MEMBER 
        WHERE MEM_ID = '{mem_id}' 
          and MEM_TEL = '{mem_tel}' 
          and MEM_REGNO1 = '{mem_regno1}'
          and MEM_REGNO2 = '{mem_regno2}'
    """
    rows = dbutil.getListDict()
    print(f"[End] getPW() 결과값 = {rows}..................................")
    return rows




##############################[rental_log.py 대여기록 페이지]#################################
# # 새로운 데이터를 'data_table'에 삽입하는 메서드
# @staticmethod
# def insert_into_data_table(entry_id, email, disease, percentage):
#     sql = "INSERT INTO data_table (entry_id, email, disease, percentage) VALUES (%s, %s, %s, %s)"
#     val = (entry_id, email, disease, percentage)  # 삽입할 값들
#     Database.cursor.execute(sql, val)  # 쿼리 실행
#     Database.connection.commit()  # 변경사항 커밋
def get_rental_log(mem_id):
    print(f"[Start] get_rental_log({mem_id}) ..................................")
    dbutil.sql_in = f"""
        SELECT RENT_NO, RENT_STIME, RENT_ETIME 
        FROM RENTAL_LOG 
        WHERE RENT_MEM = '{mem_id}' AND RENT_ETIME IS NOT NULL
        ORDER BY RENT_STIME DESC
    """
    rows = dbutil.getListDict()
    print(f"[End] get_rental_log() 결과값 = {rows}..................................")
    return rows







############################  인증기록 확인 #########################################

# def setCertLog(cert_helmet, cert_ident, cert_image):
#     print(f"[Start] setCertLog({cert_helmet}, {cert_ident}, '{cert_image}') ..................................")
#     dbutil.sql_in = f"""
#         INSERT INTO cert_log
#         (cert_helmet, cert_ident, cert_image, cert_time)
#         VALUES ({cert_helmet}, {cert_ident}, '{cert_image}', SYSDATE())
#     """
#     insert_cnt = dbutil.setCUD()
#     print(f"[End] setCertLog() 결과값 = {insert_cnt}..................................")
#     return insert_cnt

##############################[mypage.py 마이페이지]#################################
def get_user_info(mem_id):
    print(f"[Start] get_user_info({mem_id}) ..................................")
    dbutil.sql_in = f"""
        SELECT * FROM MEMBER 
        WHERE MEM_ID = '{mem_id}'
    """
    rows = dbutil.getListDict()
    print(f"[End] get_user_info() 결과값 = {rows}..................................")
    return rows[0] if rows else None

def update_user_info(mem_id, nickname, phone, address, password):
    print(f"[Start] update_user_info({mem_id}, {nickname}, {phone}, {address}, {password}) ..................................")
    dbutil.sql_in = f"""
        UPDATE MEMBER 
        SET MEM_NICK = '{nickname}', MEM_TEL = '{phone}', MEM_ADD = '{address}', MEM_PASS = '{password}'
        WHERE MEM_ID = '{mem_id}'
    """
    row = dbutil.setCUD()
    print(f"[End] update_user_info() 결과값 = {row}..................................")
    return row

###############################[driving_start.py 대여 페이지]#################################
def insert_rental_log(mem_id, rent_result, current_location):
    print(f"[Start] insert_rental_log({mem_id}, {rent_result}, {current_location}) ..................................")
    
    # 현재 시간을 '%Y-%m-%d %H:%M:%S' 형식의 문자열로 변환
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    dbutil.sql_in = f"""
        INSERT INTO RENTAL_LOG
        (RENT_MEM, RENT_STIME, RENT_VEHICLE, RENT_SPLACE1, RENT_SPLACE2, RENT_RESULT)
        VALUES ('{mem_id}', '{current_time}', 'k07-20241003', '{current_location[0]}', '{current_location[1]}', '{rent_result}')
    """
    row = dbutil.setCUD()
    print(f"[End] insert_rental_log({row}) ..................................")
    return row

def update_rental_log(rent_no, rent_result, end_location):
    # rent_result의 모든 요소를 문자열로 변환
    rent_result_str = [str(item) for item in rent_result]
    result_str = ','.join(rent_result_str)
    
    # 현재 시간을 '%Y-%m-%d %H:%M:%S' 형식의 문자열로 변환
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[Start] update_rental_log({rent_no}, '{str}') ..................................")
    dbutil.sql_in = f"""
        UPDATE RENTAL_LOG 
        SET RENT_RESULT = '{result_str}' , RENT_ETIME = '{current_time}', RENT_EPLACE1 = '{end_location[0]}', RENT_EPLACE2 = '{end_location[1]}'
        WHERE RENT_NO = {rent_no}
        """
    row = dbutil.setCUD()
    print(f"[End] update_rental_log({row}) ..................................")
    return row

def get_rent_no(mem_id):
    print(f"[Start] select_rental_log({mem_id}) ..................................")
    dbutil.sql_in = f"""
        SELECT RENT_NO FROM RENTAL_LOG
        WHERE RENT_NO = (SELECT MAX(RENT_NO) FROM RENTAL_LOG WHERE RENT_MEM = '{mem_id}')
    """
    rows = dbutil.getListDict()
    print(f"[End] select_rental_log() 결과값 = {rows}..................................")
    return rows

def insert_cert_log(dt):
    # SQL에 넣기 위해 쿼리에서 여러 행 넣을때 적는 작은 ''를 자동적으로 넣는 형식
    dt[["CERT_SERVICE","CERT_MEM"]] = dt[["CERT_SERVICE","CERT_MEM"]].applymap(lambda x : f"'{x}'" )
    dt["CERT_TIME"] = dt["CERT_TIME"].apply(lambda x: f"'{x.strftime('%Y-%m-%d %H:%M:%S')}'")

    # 데이터프레임에 쿼리 형태로 쌓는 중
    final_result = ""
    row_values = ""
    rn=0
    for index, row in dt.iterrows():
        rn = rn+1
        if rn < len(dt) :
            row_values = '(' + ',' .join(map(str,row.values)) + '),' + '\n'
            final_result += row_values
        else :
            row_values = '(' + ',' .join(map(str,row.values)) + ')' + '\n'
            final_result += row_values
    print(final_result)
    
    
    # final_result(데이터프레임에 쿼리 형태로 쌓음)은 것을 DB에 넣는 과정
    dbutil.sql_in = f"""
        INSERT INTO CERT_LOG
        (CERT_NO, CERT_HELMET, CERT_IDENT, CERT_SERVICE, CERT_TIME, CERT_MEM)
        VALUES 
        {final_result}
    """
    insert_cnt = dbutil.setCUD()
    print(f"[End] insert_cert_log() 결과값 = {insert_cnt}..................................")
    return insert_cnt