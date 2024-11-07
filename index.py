from kivy.lang import Builder
import requests
from kivymd.uix.screen import MDScreen
# from csvtest_real1 import database

from datetime import datetime
from http.cookies import SimpleCookie
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

Builder.load_file('index.kv')

class Index(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = SimpleCookie()
        self.dialog = None  # 팝업을 저장할 변수 추가

    def on_enter(self):
        # 화면에 들어올 때 데이터베이스에서 이름을 가져와 반영
        self.update_member_name()
        self.update_date()


    ### 인덱스에 이름 들어가는 부분 request로 수정
    def update_member_name(self):
        app = MDApp.get_running_app()
        if app.store.exists('session'):
            mem_id = app.store.get('session')['mem_id']
            response = self.send_update_name_request(mem_id)
            if response.get('status') == 'success':
                text = f"안녕하세요 {response['mem_name']}님,\n오늘도 안전운전하세요!"
                self.ids.mem_text.text = text
            else:
                self.ids.mem_text.text = "사용자 이름을 불러올 수 없습니다."
        else:
            self.ids.mem_text.text = "로그인이 필요합니다."

    def send_update_name_request(self, mem_id):
        url = 'http://127.0.0.1:8000/index/'  # Django 서버의 index/
        data = {'mem_id': mem_id}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}

     ### 오늘 날짜 + 요일 구해서 메인페이지에 표시
    def update_date(self):
        # 오늘 날짜 가져오기
        today = datetime.now().strftime("%Y.%m.%d")
        #     # 만약 데이터가 없을 경우의 처리
        # 영어 요일을 한글 요일로 변환
        weekday_eng = datetime.now().strftime("%A")  # 영어 요일
        weekday_kor = self.get_korean_weekday(weekday_eng)  # 한글로 변환
        #     print("세션 ID가 없습니다. 로그인을 다시 시도하세요.")
        # 메인 화면의 날짜와 요일을 업데이트
        self.ids.today.text = f"{today} ({weekday_kor})"


    ### 영어 요일을 한글 요일로 변환
    def get_korean_weekday(self, weekday_eng):
        # 영어 요일을 한글 요일로 매핑
        weekdays = {
            "Monday": "월",
            "Tuesday": "화",
            "Wednesday": "수",
            "Thursday": "목",
            "Friday": "금",
            "Saturday": "토",
            "Sunday": "일",
        }
        return weekdays.get(weekday_eng, "알 수 없음")

    def show_start_confirmation_popup(self):
        self.dialog = MDDialog(
            title='서비스 시작 확인',
            text="헬멧인식과 명의도용 인식 서비스를 시작하겠습니다. 계속하시겠습니까?",
            buttons=[
                MDRaisedButton(
                    text="예",
                    md_bg_color="#00289B",
                    text_color="#FFFFFF",
                    elevation=0,
                    on_release=self.start_driving_service
                ),
                MDRaisedButton(
                    text="아니요",
                    md_bg_color="#b2b2b3",
                    text_color="#FFFFFF",
                    elevation=0,
                    on_release=self.dismiss_popup
                ),
            ],
        )
        self.dialog.open()

    def start_driving_service(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        self.switch_screen('driving_start')  # driving_start 화면으로 전환

    def dismiss_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def logout(self):
        app = MDApp.get_running_app()
        app.store.delete('session')
        self.manager.current = 'intro'
        
        # ID와 비밀번호 필드 가져오기
        username_field = self.manager.get_screen('login').ids.mem_id
        password_field = self.manager.get_screen('login').ids.password

        # 자동 저장 체크 여부 확인
        login_screen = self.manager.get_screen('login')
        if login_screen.auto_save:
            # 자동 저장이 되어 있으면 저장된 정보 유지
            username_field.text = login_screen.saved_username
            password_field.text = login_screen.saved_password
        else:
            # 자동 저장이 해제되어 있으면 필드를 비움
            username_field.text = ''
            password_field.text = ''
