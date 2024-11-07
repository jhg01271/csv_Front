from kivy.lang import Builder  # Kivy의 Builder 모듈을 사용해 문자열로 정의된 KV 언어를 파싱
from kivymd.uix.screen import MDScreen  # KivyMD에서 제공하는 MDScreen 클래스를 사용해 화면을 정의
import database  # 데이터베이스 관련 모듈을 불러옴

# KV 언어로 화면 레이아웃을 정의
# .kv 파일에서 레이아웃을 정의한 것을 로드함 (화면 레이아웃)
Builder.load_file('mem_regimage.kv')

# Regimage 클래스 정의 (MDScreen을 상속받음)
class Regimage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mem_id = None

    def switch_screen(self, screen_name):  # 화면 전환 메서드
        self.manager.current = screen_name  # screen_name에 해당하는 화면으로 전환
        
    # def set_mem_id(self, mem_id):
    #     self.mem_id = mem_id
    #     print(f"MemRegImage: mem_id set to {self.mem_id}")

    def set_mem_id(self, mem_id):
        self.mem_id = mem_id
        reg_cam_screen = self.manager.get_screen('reg_cam')
        reg_cam_screen.put_mem_id(self.mem_id)
        print(f"MemRegImage: mem_id put in to reg_cam")

    # def reg_cam(self):  # 신분증 촬영 메서드 (여기에 촬영 로직을 추가)
    #     pass

    # 주석 처리된 모바일 신분증 불러오기 메서드 (추가 로직을 작성할 수 있음)
    # def load_mobile_id(self):
    #     pass
