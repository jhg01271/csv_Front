from kivy.lang import Builder  # Kivy의 Builder 모듈을 사용해 문자열로 정의된 KV 언어를 파싱
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen  # KivyMD에서 제공하는 MDScreen 클래스를 사용해 화면을 정의
# from csvtest_real1 import database
import database
import requests

# KV 언어를 사용해 UI 레이아웃을 문자열로 정의
Builder.load_string("""          
# 비밀번호 찾기 화면 레이아웃 정의
<FindPW>:
    name: "find_password"

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
                on_release: root.switch_screen('login')
                pos_hint: {"center_y": 0.5}

        # 타이틀 레이블
        MDLabel:
            text: "비밀번호 찾기"
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




        BoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            padding: [dp(20), dp(40), dp(0), dp(10)]

            # # 상단에 고정된 MDTopAppBar
            # MDTopAppBar:
            #     title: "비밀번호 찾기"
            #     md_bg_color: "#FFFFFF"
            #     specific_text_color: "#656565"  # 텍스트와 아이콘 색상 지정
            #     left_action_items: [["arrow-left", lambda x: root.switch_screen('login')]] 
            #     elevation: 0

            MDLabel:
                text: "비밀번호를 찾기 위해 정보를 입력해주세요"
                size_hint_y: None
                text_color: "#656565"
                # pos_hint: {"center_x": 0.6}
                height: self.texture_size[1] + dp(18)  # 여백 추가


            # 아이디 입력칸
            MDTextField:
                id: mem_id
                hint_text: "아이디"
                size_hint_x: None
                width: dp(300)
                pos_hint: {"center_x": 0.5}
                helper_text_mode: "persistent"
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

            # 주민번호 입력칸
            MDLabel:
                text: "주민등록번호"
                font_size: sp(13)
                size_hint_y: None
                height: dp(16)
                pos_hint: {"center_x": 0.58}
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint: None, None
                height: dp(48)
                width: dp(300)
                spacing: dp(10)
                pos_hint: {"center_x": 0.5}

                # 주민번호 앞자리
                MDTextField:
                    id: mem_regno1
                    hint_text: "앞자리"
                    helper_text_mode: "persistent"
                    size_hint_x: None
                    width: dp(130)
                    max_text_length: 6
                    line_color_normal: "#00289B"
                    # hint_text_color_normal: "#00289B"
                    line_color_focus: "#00289B"
                    hint_text_color_focus: "#00289B"
                    text_color: "#00289B"
                    text_color_normal: "#00289B"
                    text_color_focus: "#00289B"
                    
                # "-" 기호
                MDLabel:
                    text: "-"
                    size_hint_x: None
                    pos_hint: {"center_y": 0.5}
                    width: dp(10)  # "-" 기호의 너비를 지정
                # 주민번호 뒷자리
                CustomTextField:
                    id: mem_regno2
                    _hint: "뒷자리"
                    size_hint_x: None
                    width: dp(135)
                    max_text_length: 7



            MDLabel:
                text: " "
                size_hint_y: None
                height: self.texture_size[1] + dp(20)  # 여백 추가

            # 찾기 버튼
            MDRaisedButton:
                text: "비밀번호 찾기"
                size_hint: (0.7, 0.1)
                height: dp(40)
                font_size: sp(18)
                pos_hint: {"center_x": 0.5}
                md_bg_color: "#00289B"
                elevation: 0
                on_release: root.find_pw()   # 비밀번호 찾기 성공 시 로그인 페이지로 이동

            MDLabel:
                text: " "
                size_hint_y: None
                height: self.texture_size[1] + dp(50)  # 여백 추가
""")


# 'FindPW' 화면 클래스 정의, MDScreen을 상속받음
class FindPW(MDScreen):

    # def isExist(self, mem_id, password):
    #
    #     from csvtest_real1 import database
    #     login_view = database.isExsist
    #     print(f"*********************{mem_id}, {password}*********************")
    #     query = f"SELECT * FROM csv.MEMBER WHERE MEM_ID = '{mem_id}' and MEM_PASS = '{password}'"
    #     try:
    #         result = fetch_data(query=query)
    #         print(f"---------------------{result}-------------------")
    #         if result:  # 결과가 있으면 True
    #             return True
    #         else:
    #             return False
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #         return False

    def switch_screen(self, screen_name):
        self.manager.current = screen_name  # screen_name에 맞는 페이지로 이동

    def on_leave(self):
        """화면을 떠날 때 입력 필드를 초기화합니다."""
        self.ids.mem_id.text = ""
        self.ids.mem_tel.text = ""
        self.ids.mem_regno1.text = ""
        self.ids.mem_regno2.text = ""

    # # PW 찾기 화면
    # class FindPWScreen(Screen):
    #     def getPW(self, mem_id, mem_tel, mem_regno1, mem_regno2):
    #         print(f"*********************{mem_id}, {mem_tel}, {mem_regno1}, {mem_regno2}*********************")
    #         query = f"""
    #             SELECT MEM_PASS FROM csv.MEMBER
    #             WHERE MEM_ID = '{mem_id}'
    #               and MEM_TEL = '{mem_tel}'
    #               and MEM_REGNO1 = '{mem_regno1}'
    #               and MEM_REGNO2 = '{mem_regno2}'"""
    #         try:
    #             result = fetch_data(query=query)
    #             print(f"---------------------{result}-------------------")
    #             if result:  # 결과가 있으면 True
    #                 return result[0][0]
    #             else:
    #                 return False
    #         except Exception as e:
    #             print(f"Error occurred: {e}")
    #             return False

    def find_pw_failed_popup(self):
        dialog = MDDialog(
            title="비밀번호 찾기 실패",
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

    def find_pw_success_popup(self, mem_pass):
        def close_dialog_and_switch():
            dialog.dismiss()
            self.manager.current = 'login'

        dialog = MDDialog(
            title="비밀번호 찾기 성공",
            text=f"고객님의 비밀번호는 [{mem_pass}] 입니다.",
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

    def find_pw(self):
        mem_id = self.ids.mem_id.text
        mem_tel = self.ids.mem_tel.text
        mem_regno1 = self.ids.mem_regno1.text
        mem_regno2 = self.ids.mem_regno2.ids.textfield.text
        
        # print(f"======================={mem_id}, {mem_tel}, {mem_regno1}, {mem_regno2}===================")
        # if database.getPW(mem_id, mem_tel, mem_regno1, mem_regno2):
        #     mem_pass = database.getPW(mem_id, mem_tel, mem_regno1, mem_regno2)[0]
        #     print("ID Found Successfully")
        #     self.find_pw_success_popup(mem_pass["mem_pass"])
        #     print("Find ID Failed")
        #     self.find_pw_failed_popup()  # 팝업 띄우기
        
        response = self.send_find_pw_request(mem_id, mem_tel, mem_regno1, mem_regno2)

        if response.get('status') == 'success':
            mem_pass = response.get('mem_pass')
            self.find_pw_success_popup(mem_pass)
        else:
            self.find_pw_failed_popup()

    def send_find_pw_request(self, mem_id, mem_tel, mem_regno1, mem_regno2):
        url = 'http://127.0.0.1:8000/find_password/'  # Django 서버의 비밀번호 찾기 API 엔드포인트
        data = {'mem_id': mem_id, 'mem_tel': mem_tel, 'mem_regno1': mem_regno1, 'mem_regno2': mem_regno2}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}
