from kivy.lang import Builder  # Kivy의 Builder 모듈을 사용해 문자열로 정의된 KV 언어를 파싱
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen  # KivyMD에서 제공하는 MDScreen 클래스를 사용해 화면을 정의
import requests
from http.cookies import SimpleCookie
from kivymd.app import MDApp

# KV 언어를 사용해 UI 레이아웃을 문자열로 정의
Builder.load_string("""
# 로그인 화면 레이아웃 정의
<Login>:
    name: "login"

    MDBoxLayout:
        orientation: 'vertical'
        # spacing: dp(15)

        # 상단 타이틀 및 뒤로가기 버튼 박스
        MDBoxLayout:  # 상단에 위치할 타이틀과 나가기 버튼 박스
            size_hint_y: None  # 레이아웃 높이를 고정하기 위해 None으로 설정
            height: dp(50)  # 레이아웃 높이를 50dp로 설정
            # padding: [dp(10), dp(0), dp(10), dp(0)]  # 내부 패딩 설정 (왼쪽, 위, 오른쪽, 아래)
            # md_bg_color: 1, 0, 0, 1  # 상단 배경 색상을 빨간색으로 설정 (예시)
            pos_hint: {"center_x": 0.5, "top": 1}  # 화면 상단에 고정
            
            # 뒤로가기 버튼
            MDIconButton:
                icon: "arrow-left"
                padding: [dp(10), dp(0), dp(10), dp(0)]
                on_release: root.switch_screen('intro')
                pos_hint: {"center_y": 0.5}

        # 타이틀 레이블
        MDLabel:
            text: "로그인"
            padding: [dp(0), dp(0), dp(10), dp(0)]  # 내부 패딩 설정 (왼쪽, 위, 오른쪽, 아래)
            # bold: True
            halign: "left"
            valign: "middle"  # 세로 가운데 정렬
            size_hint: None, None  # 크기 고정
            width: dp(318)  # 레이블의 고정 너비
            height: dp(60)  # 고정 높이
            font_size: '20sp'
            theme_text_color: "Custom"
            text_color: "#000000"
            pos_hint: {"top": 1.88, "center_x": 0.5}  # 타이틀 바로 아래에 위치하도록 설정
            # md_bg_color: 1, 0, 0, 1  # 상단 배경 색상을 빨간색으로 설정 (예시)


        # 나머지 콘텐츠를 감싸는 BoxLayout
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(10)

            MDLabel:
                text: "CSV에 오신 것을 환영합니다!"
                size_hint_y: None
                text_color: "#656565"
                height: self.texture_size[1] + dp(5)

            # 배경 이미지 삽입
            MDBoxLayout:
                size_hint: None, None
                size: dp(170), dp(170)
                pos_hint: {"center_x": 0.5}
                Image:
                    source: "background.png"
                    allow_stretch: True
                    keep_ratio: True

        #MDLabel:
            #text: " "
            #font_size: sp(2)
            #size_hint_y: None
            #height: self.texture_size[1] + dp(1)  # 여백 추가

        # ID 입력칸
        MDTextField:
            id: mem_id
            hint_text: "아이디"
            helper_text_mode: "persistent"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}
            on_text_validate: root.ids.password.ids.textfield.focus = True  # Enter 키를 눌렀을 때 포커스 이동
            line_color_normal: "#00289B"
            # hint_text_color_normal: "#00289B"
            line_color_focus: "#00289B"
            hint_text_color_focus: "#00289B"
            text_color_normal: "#00289B"
            text_color_focus: "#00289B"
            
        # PW 입력칸
        CustomTextField:
            id: password
            _hint: "비밀번호"
            #helper_text_mode: "persistent"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}
            password: True  # 비밀번호를 숨기기 위해 True 설정
        
        

        # 회원가입, 아이디 찾기, 비밀번호 찾기 라벨들을 수평으로 배치
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            spacing: dp(20)
            padding: [dp(20), 0]
            pos_hint: {"center_x": 0.5}
            
            MDLabel:
                text: "회원가입"
                font_size: sp(15)
                halign: "center"
                theme_text_color: "Hint"
                on_touch_down: 
                    if self.collide_point(*args[1].pos): root.switch_screen('signup')

            MDLabel:
                text: "아이디 찾기"
                font_size: sp(15)
                halign: "center"
                theme_text_color: "Hint"
                on_touch_down: 
                    if self.collide_point(*args[1].pos): root.switch_screen('find_id')

            MDLabel:
                text: "비밀번호 찾기"
                font_size: sp(15)
                halign: "center"
                theme_text_color: "Hint"
                on_touch_down: 
                    if self.collide_point(*args[1].pos): root.switch_screen('find_password')
        
        ### 로그인 정보 자동저장      
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            width: dp(300)
            height: dp(40)
            spacing: dp(10)  # 체크박스와 라벨 사이의 간격을 줄임
            pos_hint: {"center_x": 0.6}
            # md_bg_color: 1, 0, 0, 1  # 상단 배경 색상을 빨간색으로 설정 (예시)


            MDCheckbox:
                id: auto_login_check
                # 체크박스 상태에 따라 자동 저장을 설정할 수 있습니다.
                size_hint: None, None
                size: dp(24), dp(24)
                pos_hint: {"center_y": 0.5}
                # padding: [dp(10), dp(0), dp(0), dp(0)]  # 내부 패딩 설정 (왼쪽, 위, 오른쪽, 아래)
                color_active: "#00289B"
                color_inactive: "FFD500"

            MDTextButton:
                text: "로그인 정보 자동 저장"
                on_press: auto_login_check.active = not auto_login_check.active
                size_hint: None, None
                font_size: sp(13)
                width: dp(260)
                height: dp(100)
                text_color: "#656565"
                pos_hint: {"center_y": 0.5}
        

        MDBoxLayout:
            orientation: 'vertical'
            size_hint: (None, None)
            height: dp(45)
            width: dp(300)
            # spacing: dp(10)
            pos_hint: {"center_x": 0.5,"bottom": 0.5}
            # md_bg_color: 1, 0, 1, 1  # 상단 배경 색상을 빨간색으로 설정 (예시)
            
            # 로그인 버튼
            MDRaisedButton:
                text: "로그인"
                size_hint: (1, None)
                height: dp(50)
                font_size: sp(15)
                md_bg_color: "#00289B"
                # pos_hint: {"center_x": 0.5, "bottom": 0.5}  # 화면 하단 쪽에 위치
                on_press: root.login()
                elevation: 0
                
        # 간격 추가
        MDBoxLayout:
            size_hint_y: None
            height: dp(40)  # 이 값을 조절하여 간격을 조정할 수 있습니다

""")

# 'Login' 화면 클래스 정의, MDScreen을 상속받음
class Login(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = SimpleCookie()
        
        # 변수 저장용 (자동 저장 여부와 사용자 정보)
        self.auto_save = False
        self.saved_username = ""
        self.saved_password = ""

    def login(self):
        # ID와 비밀번호 필드 가져오기
        mem_id = self.ids.mem_id.text
        password = self.ids.password.ids.textfield.text
        auto_login_check = self.ids.auto_login_check.active

        # Django 서버로 로그인 요청 보내기
        response = self.send_login_request(mem_id, password)

        if response.get('status') == 'success':
            app = MDApp.get_running_app()
            app.store.put('session', mem_id=mem_id)
            
            # 자동 저장 여부 확인
            if auto_login_check:
                self.auto_save = True
                self.saved_username = mem_id
                self.saved_password = password
            else:
                # 체크가 해제되어 있으면 자동 저장 해제
                self.auto_save = False

            self.manager.current = "index"
            self.manager.get_screen("index").update_member_name()
        else:
            self.show_login_failed_popup()

    ### 디장고 서버로 로그인 요청 보내기
    def send_login_request(self, mem_id, password):
        url = 'http://127.0.0.1:8000/login/'  # Django 서버의 로그인 API 엔드포인트
        data = {'mem_id': mem_id, 'password': password}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}


################# [~위에까지 처리하면 db에 접근해서 True, False 반환]#################


    def show_login_failed_popup(self):
        dialog = MDDialog(
            title="로그인 실패",
            text="아이디 또는 비밀번호를 다시 확인해주세요.",
            buttons=[
                MDRaisedButton(
                    text="확인",
                    text_color="#FFFFFF",  # 버튼 텍스트 색상
                    md_bg_color="#00289B",  # 버튼 배경 색상
                    on_release=lambda *args: dialog.dismiss()
                )
            ],
        )
        dialog.open()

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

