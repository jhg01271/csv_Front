from kivy.lang import Builder  # Kivy의 Builder 모듈을 사용해 문자열로 정의된 KV 언어를 파싱
from kivymd.uix.screen import MDScreen  # KivyMD에서 제공하는 MDScreen 클래스를 사용해 화면을 정의
from reg_models2 import CamApp, crop_latest_image

# .kv 파일에서 레이아웃을 정의한 것을 로드함 (화면 레이아웃)
Builder.load_file('reg_cam2.kv')

# RegCam 클래스 정의 (MDScreen을 상속받음)
class RegCam2(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mem_id = None
        self.cam_app3 = None
        self.cropped_img_filename = None
        self.regno1 = None
        self.regno2 = None

    def on_enter(self):
        if not self.cam_app3:
            self.cam_app3 = CamApp(manager=self.manager, web_cam=self.ids.web_cam, mem_id=self.mem_id)  # RegCam 인스턴스 전달
            # camera_layout = self.cam_app3.build()
            # self.ids.camera_box.add_widget(camera_layout)

    def on_leave(self):
        if self.cam_app3:
            self.cam_app3.stop_camera()
            self.ids.web_cam.clear_widgets()
            if self.cam_app3.cropped_img_filename:
                self.manager.get_screen('mypage').set_regimage(self.cam_app3.cropped_img_filename)
                self.manager.get_screen('mypage').set_regno(self.cam_app3.regno1, self.cam_app3.regno2)
                print(f"***reg_cam2.py*** self.cam_app3.cropped_img_filename: {self.cam_app3.cropped_img_filename} self.cam_app3.regno1: {self.cam_app3.regno1} self.cam_app3.regno2: {self.cam_app3.regno2}")
            
            # 카메라 장치 해제
            if self.cam_app3.capture and self.cam_app3.capture.isOpened():
                self.cam_app3.capture.release()
                print("***reg_cam2.py*** release camera")
            
            self.cam_app3 = None

        self.manager.current = 'mypage'

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def put_mem_id(self, mem_id):
        self.mem_id = mem_id
        print(f"RegCam2: mem_id set to {self.mem_id}")