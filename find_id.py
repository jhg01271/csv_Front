from kivy.lang import Builder  # Kivy의 Builder 모듈을 사용해 문자열로 정의된 KV 언어를 파싱
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen  # KivyMD에서 제공하는 MDScreen 클래스를 사용해 화면을 정의
from kivy.utils import get_color_from_hex
import database
import requests

# KV 언어를 사용해 UI 레이아웃을 문자열로 정의
Builder.load_string("""          
# ID 찾기 화면 레이아웃 정의
<FindID>:
    name: "find_id"

    BoxLayout:
        orientation: 'vertical'
        spacing: dp(18)

        # 상단에 고정된 MDTopAppBar
        MDTopAppBar:
            title: "아이디 찾기"
            md_bg_color: "#FFFFFF"
            specific_text_color: "#656565"  # 텍스트와 아이콘 색상 지정
            left_action_items: [["arrow-left", lambda x: root.switch_screen('login')]]
            elevation: 0

        MDLabel:
            text: "아이디를 찾기 위해 정보를 입력해주세요!"
            size_hint_y: None
            text_color: "#656565"
            pos_hint: {"center_x": 0.6}
            height: self.texture_size[1] + dp(18)  # 여백 추가

        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(20)  # 여백 추가


        # 이름 입력칸
        MDTextField:
            id: mem_name
            hint_text: "이름"
            helper_text_mode: "persistent"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}
            line_color_normal: "#00289B"
            # hint_text_color_normal: "#00289B"
            line_color_focus: "#00289B"
            hint_text_color_focus: "#00289B"
            text_color: "#00289B"
            text_color_normal: "#00289B"
            text_color_focus: "#00289B"

        # 휴대폰번호 입력칸
        MDTextField:
            id: mem_tel
            hint_text: "휴대폰번호 (010-0000-0000)"
            helper_text_mode: "persistent"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}
            max_text_length: 13
            line_color_normal: "#00289B"
            # hint_text_color_normal: "#00289B"
            line_color_focus: "#00289B"
            hint_text_color_focus: "#00289B"
            text_color: "#00289B"
            text_color_normal: "#00289B"
            text_color_focus: "#00289B"

        # 생년월일 입력칸
        MDTextField:
            id: mem_birth
            hint_text: "생년월일 (YYMMDD)"
            helper_text_mode: "persistent"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}
            max_text_length: 6
            line_color_normal: "#00289B"
            # hint_text_color_normal: "#00289B"
            line_color_focus: "#00289B"
            hint_text_color_focus: "#00289B"
            text_color: "#00289B"
            text_color_normal: "#00289B"
            text_color_focus: "#00289B"

        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(20)  # 여백 추가

        # 찾기 버튼
        MDRaisedButton:
            text: "아이디 찾기"
            size_hint: (0.7, 0.1)
            height: dp(40)
            font_size: sp(18)
            pos_hint: {"center_x": 0.5}
            md_bg_color: "#00289B"
            elevation: 0
            on_release: root.find_id()   # 아이디 찾기 성공 시 로그인 페이지로 이동

        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(20)  # 여백 추가
""")


# 'FindID' 화면 클래스 정의, MDScreen을 상속받음
class FindID(MDScreen):
    def switch_screen(self, screen_name):
        self.manager.current = screen_name  # screen_name에 맞는 페이지로 이동

    def find_id_failed_popup(self):
        dialog = MDDialog(
            title="아이디 찾기 실패",
            text="입력해주신 정보를 다시 확인해주세요.",
            buttons=[
                MDRaisedButton(
                    text="확인",
                    md_bg_color="#00289B",  # 버튼 배경색 설정
                    text_color="#FFFFFF",  # 텍스트 색상 설정
                    elevation=0,  # 그림자 제거
                    on_release=lambda *args: dialog.dismiss()
                )
            ],
        )
        dialog.open()

    def find_id_success_popup(self, mem_id):
        def close_dialog_and_switch():
            dialog.dismiss()
            self.manager.current = 'login'

        dialog = MDDialog(
            title="아이디 찾기 성공",
            text=f"고객님의 아이디는 [{mem_id}] 입니다.",
            buttons=[
                MDRaisedButton(
                    text="확인",
                    md_bg_color="#00289B",  # 버튼 배경색 설정
                    text_color="#FFFFFF",  # 텍스트 색상 설정
                    elevation=0,  # 그림자 제거
                    on_release=lambda *args: close_dialog_and_switch()
                )
            ],
        )
        dialog.open()

    def find_id(self):
        mem_name = self.ids.mem_name.text
        mem_tel = self.ids.mem_tel.text
        mem_birth = self.ids.mem_birth.text
        # print(f"======================={mem_name}, {mem_tel}, {mem_birth}===================")
        # if database.getID(mem_name, mem_tel, mem_birth):
        #     mem_id = database.getID(mem_name, mem_tel, mem_birth)[0]
        #     print("ID Found Successfully")
        #     self.find_id_success_popup(mem_id["mem_id"])
        # else:
        #     print("Find ID Failed")
        #     self.find_id_failed_popup()  # 팝업 띄우기
            
        response = self.send_find_id_request(mem_name, mem_tel, mem_birth)

        if response.get('status') == 'success':
            mem_id = response.get('mem_id')
            self.find_id_success_popup(mem_id)
        else:
            self.find_id_failed_popup()

    def send_find_id_request(self, mem_name, mem_tel, mem_birth):
        url = 'http://127.0.0.1:8000/find_id/'  # Django 서버의 ID 찾기 API 엔드포인트
        data = {'mem_name': mem_name, 'mem_tel': mem_tel, 'mem_birth': mem_birth}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}


