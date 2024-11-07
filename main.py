from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.storage.jsonstore import JsonStore
import requests
import subprocess
# import boto3
from kivy.config import Config
import atexit
import signal
import psutil

# Windows Pen 및 Touch 입력 비활성화
Config.set('input', 'wm_touch', 'None')
Config.set('input', 'wm_pen', 'None')

# 앱 크기 설정 (모바일 해상도 기준으로 설정)
Window.size = (360, 640)
# 소프트 키보드가 타겟 위로 표시되지 않고 아래에 위치하도록 설정
Window.softinput_mode = "below_target"


# 여러 화면을 관리하는 인터페이스 클래스 정의
class Interface(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.quit)

    # 뒤로가기 키(ESC)가 눌리면 앱을 종료하는 메서드
    def quit(self, window, key, *args):
        if key == 27:  # 키 값 27은 ESC 키(안드로이드에서는 뒤로 가기 버튼)
            MDApp.get_running_app().stop()  # 실행 중인 앱을 종료



class CsvApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('session.json')

    def build(self):
        # 앱의 테마와 색상 설정
        self.theme_cls.primary_palette = "Blue"  # 기본 색상을 네이비로 설정
        self.theme_cls.primary_light_hue = "300"  # 밝은 색상 팔레트의 음영을 300으로 설정
        self.theme_cls.accent_palette = "Gray"  # 배경 보조 색상을 그레이로 설정
        self.theme_cls.accent_light_hue = "50"  # 보조 색상의 밝은 음영을 50으로 설정
        self.theme_cls.accent_hue = "700"  # 보조 색상 팔레트의 기본 음영을 700으로 설정
        self.theme_cls.material_style = "M3"  # Material Design 스타일을 M3 (Material Design 3)로 설정
        Builder.load_file('csv.kv')
        
        screen = MDScreen()
        screen.add_widget(Builder.load_file('csv.kv'))
        return screen

    # def send_request_to_django(self, endpoint, data):
    #     url = f'http://127.0.0.1:8000/{endpoint}/'
    #     response = requests.post(url, json=data)
    #     return response.json()

CsvApp().run()
