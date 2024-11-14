from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.utils import platform  # 플랫폼을 확인하기 위해 사용
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton, MDFlatButton

if platform == 'android':
    from plyer import permission  # Android 플랫폼에서만 plyer.permission 사용

Builder.load_string("""
<Intro>:
    name: "intro"

    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        # md_bg_color: "#F7F7F9"

        MDBoxLayout:
            size_hint_x: None
            size_hint_y: 0.2
            width: dp(100)
            pos_hint: {"x":0, "top": 1}
            md_bg_color: "#F7F7F9"
            Image:
                source: "csv_logo.png"
                allow_stretch: True
                keep_ratio: True
                size_hint: None, None
                width: self.parent.width
                height: self.parent.height
        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        MDBoxLayout:
            size_hint: None, None
            size: dp(270), dp(270)
            pos_hint: {"center_x": 0.5}
            Image:
                source: "background.gif"
                allow_stretch: True
                keep_ratio: True

        MDLabel:
            text: "환영합니다!"
            halign: "center"
            size_hint_y: None
            height: dp(30)

        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(15)

        MDRaisedButton:
            text: "로그인"
            size_hint: (0.8, 0.1)
            height: dp(40)
            font_size: sp(18)
            pos_hint: {"center_x": 0.5}
            md_bg_color: "#00289B"
            on_press:root.move_to_login()
            elevation: 0

        MDRaisedButton:
            text: "회원가입"
            size_hint: (0.8, 0.1)
            height: dp(45)
            font_size: sp(18)
            pos_hint: {"center_x": 0.5}
            md_bg_color: "#FFFFFF"
            text_color: "#000000"
            line_color: "#00289B"
            on_press:root.move_to_signup()
            elevation: 0
            
        MDLabel:
            text: " "
            size_hint_y: None
            height: self.texture_size[1] + dp(30)
""")

class Intro(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 플랫폼에 따라 권한 요청 로직 결정
        if platform == 'android':
            Clock.schedule_once(self.show_permission_dialog, 1)

    def show_permission_dialog(self, *args):
        if platform == 'android':
            dialog = MDDialog(
                title="카메라 접근 권한 요청",
                text="이 앱에서 카메라에 접근하려고 합니다. 허용하시겠습니까?",
                buttons=[
                    MDRaisedButton(
                        text="허용",
                        md_bg_color="#00289B",  # 버튼 배경색 설정
                        text_color="#FFFFFF",  # 텍스트 색상 설정
                        elevation=0,  # 그림자 제거
                        on_press=lambda x: self.request_camera_permission()
                    ),
                    MDRaisedButton(
                        text="거부",
                        md_bg_color="#b2b2b3",  # 버튼 배경색 설정
                        text_color="#FFFFFF",  # 텍스트 색상 설정
                        elevation=0,  # 그림자 제거
                        on_press=lambda x: self.dismiss_dialog()
                    ),
                ],
            )
            dialog.open()

    def request_camera_permission(self):
        if platform == 'android':
            permission.request_permissions([permission.CAMERA])

    def dismiss_dialog(self):
        self.manager.current = 'intro'

    def move_to_signup(self):
        self.manager.current = "signup"


    def move_to_login(self):
        self.manager.current = "login"
