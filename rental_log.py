from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.utils import platform  # 플랫폼을 확인하기 위해 사용
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
import requests
from http.cookies import SimpleCookie
from kivymd.app import MDApp
from datetime import datetime
import pandas as pd
from kivymd.uix.label import MDLabel  # MDLabel을 가져옵니다.

if platform == 'android':
    from plyer import permission  # Android 플랫폼에서만 plyer.permission 사용

Builder.load_string("""
<Rental_Log>:
    name: "rental_log"
    
    MDBoxLayout:
        orientation: 'vertical'

        # 노란색 배경 영역 (로고 이미지와 검정색 영역 포함)
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(53)
            md_bg_color: "#FFFFFF"  # 노란색 배경
            padding: [dp(5), dp(15), 0, 0]
            spacing: dp(0)
            pos_hint: {"center_x": 0.5}

            # 뒤로가기 버튼
            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: "#656565"
                pos_hint: {"center_y": 0.6}
                on_press: root.switch_screen('index')

            # 로고 이미지 중앙 정렬
            Image:
                source: 'csv_logo.png'
                size_hint_y: None
                md_bg_color: "#FFFFFF"
                size: dp(40), dp(40)
                padding: [dp(20), dp(15), 0, 0]
                allow_stretch: True
                pos_hint: {"center_x": 0.6,"center_y": 0.6}

            # 오른쪽 빈 MDLabel
            MDLabel:
                size_hint_x: None
                width: dp(73)

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            padding: [dp(20), dp(5), 0, 0]
            md_bg_color: "#F7F7F9"

            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(60)
                padding: [0, dp(0), 0, dp(5)]
                MDLabel:
                    text: "대여 기록"
                    halign: "left"
                    font_size: sp(20)
                    size_hint_y: None
                    height: self.texture_size[1]
            
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                
                MDBoxLayout:
                    id: table_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
""")

# 대여기록 화면
class Rental_Log(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = SimpleCookie()

    def on_enter(self):
        self.get_rental_log()
     
    def get_rental_log(self):
        app = MDApp.get_running_app()
        if app.store.exists('session'):
            mem_id = app.store.get('session')['mem_id']
            response = self.send_rental_log_request(mem_id)
            
            self.ids.table_box.clear_widgets()  # 기존 위젯 제거
            
            if response.get('status') == 'success':
                rental_logs = response.get('rental_logs', 0)
                print(f"rental_logs: {rental_logs}")

                if rental_logs != 0:
                    table = MDDataTable(
                        size_hint_y=None,
                        height=dp(500),
                        use_pagination=True,
                        elevation=0,
                        column_data=[
                            ("시작일시", dp(20)),
                            ("종료일시", dp(20)),
                            ("운행시간", dp(15)),
                        ],
                        row_data=[
                            (   
                                log['rent_stime'],  # 문자열 그대로 사용
                                log['rent_etime'] if log['rent_etime'] else '',
                                str(round(float(log.get('duration_minutes', 0)))) + "분" if log['rent_etime'] else ''
                                # log['rent_stime'].to_pydatetime().strftime('%Y-%m-%d %H:%M'),
                                # log['rent_etime'].to_pydatetime().strftime('%Y-%m-%d %H:%M') if pd.notna(log['rent_etime']) else '',
                                # str(round((log['rent_etime'] - log['rent_stime']).total_seconds() / 60)) + "분" if pd.notna(log['rent_etime']) else ''
                            )
                            for log in rental_logs
                        ]
                    )
                    self.ids.table_box.add_widget(table)
            else:
                print("대여기록을 불러오는 데 실패했습니다.")
                no_data_label = MDLabel(
                    text="대여기록이 없습니다",
                    halign="center",
                    size_hint_y=None,  # 크기 힌트를 None으로 설정
                    height=dp(40),  # 높이를 설정하여 위치 조정
                    theme_text_color="Hint"
                )
                self.ids.table_box.add_widget(no_data_label)
        
        else:
                print("로그인이 필요합니다.")
                
    def send_rental_log_request(self, mem_id):
        url = 'http://127.0.0.1:8000/index/rental_log/'  # Django 서버의 index_rental_log API 엔드포인트
        data = {'mem_id': mem_id}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}
               
    def switch_screen(self, screen_name):
        self.manager.current = screen_name
