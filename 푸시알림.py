from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.utils import platform  # 플랫폼을 확인하기 위해 사용
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
import database
import requests
from http.cookies import SimpleCookie
from kivymd.app import MDApp
from plyer import notification  # 시스템 푸시 알림을 위해 사용
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock

if platform == 'android':
    from plyer import permission  # Android 플랫폼에서만 plyer.permission 사용


# 대여기록 화면
class Rental_Log(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = SimpleCookie()

    def on_enter(self):
        self.update_rental_log()
        # 3초 후에 푸시 알림을 띄우는 예시
        Clock.schedule_once(lambda dt: self.show_push_notification("테스트 알림", "이것은 테스트입니다.", delay=5), 3)

    def update_rental_log(self):
        app = MDApp.get_running_app()
        if app.store.exists('session'):
            mem_id = app.store.get('session')['mem_id']
            rental_logs = database.update_rental_log(mem_id)
            
            table = MDDataTable(
                size_hint_y=None,
                height=dp(400),
                use_pagination=True,
                column_data=[
                    ("대여번호", dp(20), "center"),
                    ("시작일시", dp(40), "center"),
                    ("종료일시", dp(40), "center")
                ],
                row_data=[(str(log['rent_no']), str(log['rent_stime']), str(log['rent_etime'])) for log in rental_logs]
            )
            
            self.ids.table_box.clear_widgets()
            self.ids.table_box.add_widget(table)
        else:
            print("로그인이 필요합니다.")
     
     
     ##======================== 밖에 팝업창 띄우는 그거
    def show_popup(self, title, message):
        # 푸시 알림을 위한 팝업 생성
        popup = Popup(title=title,
                    content=Label(text=message),
                    size_hint=(None, None), size=(400, 200))
        popup.open()
    
    
    def show_push_notification(self, title, message, delay=5):
        # 시스템 푸시 알림
        notification.notify(
            title=title,
            message=message,
            timeout=60)

        # Popup을 UI 스레드에서 실행
        Clock.schedule_once(lambda dt: self.show_popup(title, message), delay)

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

def show_system_notification(title, message):
    """
    시스템 푸시 알림을 보내는 함수.
    
    :param title: 알림의 제목
    :param message: 알림의 내용
    """
    # plyer 라이브러리를 사용하여 시스템 푸시 알림을 보냅니다.
    notification.notify(
        title=title,
        message=message,
        app_name='MyApp',  # 알림을 보낸 앱의 이름
        timeout=10  # 알림이 표시되는 시간 (초)
    )

def show_kivy_popup(title, message, delay=0):
    """
    Kivy 팝업을 띄우는 함수.
    
    :param title: 팝업의 제목
    :param message: 팝업의 내용
    :param delay: 팝업을 띄우기 전 대기 시간
    """
    def open_popup(dt):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="확인",
                    text_color="#FFFFFF",  # 버튼 텍스트 색상
                    md_bg_color="#00289B",  # 버튼 배경 색상
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    Clock.schedule_once(open_popup, delay)

# 메인 함수: 이 파일이 직접 실행될 때만 실행됩니다.
if __name__ == '__main__':
    # 테스트용 푸시 알림과 팝업을 보냅니다.
    show_system_notification("테스트 알림", "이것은 시스템 푸시 알림입니다.")
    show_kivy_popup("테스트 팝업", "이것은 Kivy 팝업입니다.", delay=3)
