from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
import requests
from http.cookies import SimpleCookie
from kivymd.app import MDApp

Builder.load_string("""
#:import CustomTextField customwidgets

<Mypage>:
    BoxLayout:
        orientation: "vertical"
        # padding: dp(10)
        # spacing: dp(10)


        # 상단 타이틀 및 뒤로가기 버튼 박스
        MDBoxLayout:  # 상단에 위치할 타이틀과 나가기 버튼 박스
            size_hint_y: None  # 레이아웃 높이를 고정하기 위해 None으로 설정
            height: dp(50)  # 레이아웃 높이를 50dp로 설정
            padding: [dp(10), dp(0), dp(10), dp(0)]  # 내부 패딩 설정 (왼쪽, 위, 오른쪽, 아래)
            # md_bg_color: 1, 0, 0, 1  # 상단 배경 색상을 빨간색으로 설정 (예시)
            pos_hint: {"center_x": 0.5, "top": 1}  # 화면 상단에 고정


            # 뒤로가기 버튼
            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: "#656565"
                pos_hint: {"center_y": 0.5}
                on_press: root.switch_screen('index')
                
        
        # 타이틀 레이블
        MDLabel:
            text: "마이페이지"
            # bold: True
            halign: "left"
            valign: "middle"  # 세로 가운데 정렬
            size_hint: None, None  # 크기 고정
            width: dp(300)  # 레이블의 고정 너비
            height: dp(60)  # 고정 높이
            font_size: '20sp'
            theme_text_color: "Custom"
            text_color: "#000000"
            pos_hint: {"top": 0.88, "center_x": 0.5}  # 타이틀 바로 아래에 위치하도록 설정

        # 안내 텍스트 레이블 (타이틀 바로 아래에 위치)
        MDLabel:
            id: mem_nick_text
            text: "(님)"
            halign: "left"
            valign: "middle"  # 세로 가운데 정렬
            size_hint: None, None  # 크기 고정
            width: dp(300)  # 레이블의 고정 너비
            height: dp(60)  # 고정 높이
            padding: [dp(0), dp(10), dp(0), dp(20)]  # 왼쪽 패딩 추가
            pos_hint: {"top": 0.76, "center_x": 0.5}  # 타이틀 바로 아래에 위치하도록 설정

        # 스크롤 가능한 회원가입 폼
        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(15)
                spacing: dp(5)
                size_hint_y: None
                height: self.minimum_height + dp(50)  # 높이 조정

                # 아이디 입력 필드
                MDTextField:
                    id: mem_id
                    hint_text: "아이디"
                    helper_text: "아이디를 입력해주세요"
                    helper_text_mode: "persistent"
                    size_hint_x: None
                    width: dp(300)
                    pos_hint: {"center_x": 0.5}
                    
                # 비밀번호 입력 필드
                CustomTextField:
                    id: password
                    _hint: "비밀번호"
                    helper_text: "영문/숫자/특수문자 포함 8자 이상"
                    size_hint_x: None
                    width: dp(300)
                    pos_hint: {"center_x": 0.5}

                # 비밀번호 확인 필드
                CustomTextField:
                    id: cpassword
                    _hint: "비밀번호 확인"
                    helper_text: "비밀번호를 다시 입력해주세요"
                    size_hint_x: None
                    width: dp(300)
                    pos_hint: {"center_x": 0.5}

                # 이름 입력 필드
                MDTextField:
                    id: name
                    hint_text: "이름"
                    helper_text: "이름을 입력해주세요"
                    helper_text_mode: "persistent"
                    size_hint_x: None
                    width: dp(300)
                    pos_hint: {"center_x": 0.5}

                # 닉네임 입력 필드
                MDTextField:
                    id: nickname
                    hint_text: "닉네임"
                    helper_text: "닉네임을 입력해주세요"
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

                # 전화번호 입력 필드
                MDTextField:
                    id: phone
                    hint_text: "전화번호"
                    helper_text: "전화번호를 입력해주세요"
                    helper_text: "010-0000-0000"
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

                # 주소 입력 필드
                MDTextField:
                    id: address
                    hint_text: "주소"
                    helper_text: "00시 00도"
                    size_hint_x: None
                    width: dp(300)
                    spacing: dp(5)
                    pos_hint: {"center_x": 0.5}
                    line_color_normal: "#00289B"
                    # hint_text_color_normal: "#00289B"
                    line_color_focus: "#00289B"
                    hint_text_color_focus: "#00289B"
                    text_color: "#00289B"
                    text_color_normal: "#00289B"
                    text_color_focus: "#00289B"

                # 주민등록번호 입력 필드
                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint: None, None
                    height: dp(60)
                    width: dp(300)
                    spacing: dp(10)
                    pos_hint: {"center_x": 0.5}

                    # 주민번호 앞자리 입력 필드
                    MDTextField:
                        id: regno1
                        hint_text: "주민번호 앞자리"
                        max_text_length: 6
                        size_hint_x: None
                        width: dp(120)

                    # "-" 기호를 레이블로 표시
                    MDLabel:
                        text: "-"
                        size_hint_x: None
                        width: dp(20)

                    # 주민번호 뒷자리 입력 필드
                    CustomTextField:
                        id: regno2
                        _hint: "주민번호 뒷자리"
                        max_text_length: 7
                        size_hint_x: None
                        width: dp(160)

                # 개인정보처리방침과 이용약관 동의 체크박스
                # MDBoxLayout:
                #     orientation: "vertical"
                #     size_hint_x: None
                #     width: dp(300)
                #     pos_hint: {"center_x": 0.5}
                #     spacing: dp(10)

                    # # 개인정보 처리방침 동의
                    # MDBoxLayout:
                    #     orientation: "horizontal"
                    #     size_hint_x: None
                    #     width: dp(300)
                    #     spacing: dp(10)

                    #     MDCheckbox:
                    #         id: privacy_check
                    #         size_hint: None, None
                    #         size: dp(24), dp(24)
                    #         pos_hint: {"center_y": 0.5}

                    #     MDTextButton:
                    #         text: "[필수] 개인정보처리방침에 동의합니다."
                    #         on_press: privacy_check.active = not privacy_check.active
                    #         size_hint: None, None
                    #         width: dp(260)
                    #         height: dp(30)

                    # # 이용약관 동의
                    # MDBoxLayout:
                    #     orientation: "horizontal"
                    #     size_hint_x: None
                    #     width: dp(300)
                    #     spacing: dp(10)

                    #     MDCheckbox:
                    #         id: terms_check
                    #         size_hint: None, None
                    #         size: dp(24), dp(24)
                    #         pos_hint: {"center_y": 0.5}

                    #     MDTextButton:
                    #         text: "[필수] 이용약관에 동의합니다."
                    #         on_press: terms_check.active = not terms_check.active
                    #         size_hint: None, None
                    #         width: dp(260)
                    #         height: dp(30)

                # 간격 추가
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(30)  # 이 값을 조절하여 간격을 조정할 수 있습니다

                # 면허증 인증 버튼
                MDRaisedButton:
                    text: "면허증 인증"
                    size_hint: (0.8, None)
                    height: dp(10)
                    md_bg_color: "#FFFFFF"
                    text_color: "#000000"
                    line_color: "#00289B"
                    font_size: sp(18)
                    pos_hint: {"center_x": 0.5}
                    on_press: root.set_mem_id2()
                    elevation: 0

                # 가입하기 버튼
                MDRaisedButton:
                    text: "수정완료"
                    size_hint: (0.8, 0.1)
                    height: dp(10)
                    font_size: sp(18)
                    md_bg_color: "#00289B"
                    pos_hint: {"center_x": 0.5}
                    on_press: root.update_info()
                    elevation: 0
                    
                # 간격 추가
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(30)  # 이 값을 조절하여 간격을 조정할 수 있습니다
                # 간격 추가
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(30)  # 이 값을 조절하여 간격을 조정할 수 있습니다
""")

class Mypage(MDScreen):
    dialog = None
    session = None
    session_id = None
    
    # 면허증 변경하지 않을때 초기값
    img_regno1 = 0
    img_regno2 = 0
    regno1 = None
    regno2 = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = SimpleCookie()

    def on_enter(self):
        self.load_user_info()

    def load_user_info(self):
        app = MDApp.get_running_app()
        if app.store.exists('session'):
             self.mem_id = app.store.get('session')['mem_id']
             if self.mem_id:
                response = self.send_user_info_request(self.mem_id)
                if response.get('status') == 'success':
                     result = response.get('result')
                     print(f'user_info: {result}')
                     if result:
                         self.ids.mem_id.text = result['mem_id']
                         self.ids.mem_id.disabled = True
                         self.ids.name.text = result['mem_name']
                         self.ids.name.disabled = True
                         self.ids.regno1.text = result['mem_regno1']
                         self.ids.regno1.disabled = True
                         self.ids.regno2.text = result['mem_regno2']
                         self.ids.regno2.disabled = True
                         self.ids.nickname.text = result['mem_nick']
                         self.ids.phone.text = result['mem_tel']
                         self.ids.address.text = result['mem_add']
                         self.regimage = result['mem_regimage']
                         print(f"origin : mypage.py regimage: {self.regimage}")
                         
                         # 닉네임 레이블에 닉네임 표시
                         text = f"({result['mem_nick']})님"
                         self.ids.mem_nick_text.text = text
                else:
                    print("사용자 정보를 불러오는 데 실패했습니다.")
             else:
               print("로그인이 필요합니다.")

    
    def send_user_info_request(self, mem_id):
        url = 'http://127.0.0.1:8000/index/get_user_info/'  # Django 서버의 index/get_user_info/
        data = {'mem_id': mem_id}
        print(f'data: {data}')
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}
    
   
    
    def update_info(self):
        nickname = self.ids.nickname.text
        phone = self.ids.phone.text
        address = self.ids.address.text
        password = self.ids.password.text
        cpassword = self.ids.cpassword.text
        regno1 = self.ids.regno1.text
        regno2 = self.ids.regno2.text
        
        if password != cpassword :
            self.show_dialog("비밀번호가 일치하지 않습니다.", is_error=True)
            
        elif password == '':
            self.show_dialog("비밀번호를 입력해주세요.", is_error=True)
            
        else:
            response = self.send_update_user_info_request(
                self.ids.mem_id.text, nickname, phone, address, password, self.regimage, regno1, regno2, self.img_regno1, self.img_regno2
            )
            if response.get('status') == 'success':
                self.show_dialog("회원정보가 수정되었습니다.", is_error=False)
            else:
                self.show_dialog(response.get('message', "회원정보 수정 중 오류가 발생했습니다."), is_error=True)

    
    
    def send_update_user_info_request(self, mem_id, nickname, phone, address, password, regimage, regno1, regno2, img_regno1, img_regno2):
        url = 'http://127.0.0.1:8000/index/update_user_info/'  # Django 서버의 index/update_user_info/
        data = {
            'mem_id': mem_id,
            'nickname': nickname,
            'phone': phone,
            'address': address,
            'password': password,
            'regimage': regimage,
            'regno1': regno1,
            'regno2': regno2,
            'img_regno1': img_regno1,
            'img_regno2': img_regno2
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}
    
    
    
    
    def set_mem_id2(self):
        mem_id = self.mem_id
        reg_cam_screen = self.manager.get_screen('mem_regimage2')
        reg_cam_screen.set_mem_id(mem_id)
        print(f'from signup2.py mem_id: {mem_id}')
        self.manager.current = 'mem_regimage2'
        return 
    
    def set_regno(self, regno1, regno2):
        self.img_regno1 = regno1
        self.img_regno2 = regno2
        print(f"mypage.py regno1, regno2 : {self.img_regno1}, {self.img_regno2}")
        
    def set_regimage(self, regimage):
        self.regimage = regimage
        print(f"mypage.py regimage: {self.regimage}")
    
    def show_dialog(self, message, is_error=True):
        if not self.dialog:
            self.dialog = MDDialog(
                title="알림" if not is_error else "오류",
                text=message,
                buttons=[
                    MDFlatButton(
                        text="확인",
                        theme_text_color="Custom",
                        text_color="#00289B",
                        on_release=self.close_dialog
                    ),
                ],
            )
        else:
            self.dialog.title = "알림" if not is_error else "오류"
            self.dialog.text = message
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()
        if self.dialog.title == "알림" and self.dialog.text == "회원정보가 수정되었습니다.":
            self.manager.current = 'index'

    def switch_screen(self, screen_name):
        self.manager.current = screen_name
