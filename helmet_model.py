import cv2
import numpy as np
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
import requests
import time

# 앱을 정의하는 HelmetDetectionApp 클래스입니다. Kivy의 App 클래스를 상속받습니다.
class HelmetDetectionApp(MDApp):
    def __init__(self, web_cam, mem_id, helmet_result_override=False, **kwargs):
        super().__init__(**kwargs)
        self.web_cam = web_cam  # OpenCV VideoCapture 객체
        self.capture = None
        self.update_event = None  # 업데이트 이벤트를 저장할 변수
        self.store = JsonStore('session.json')  # 세션 데이터를 JSON 파일로 저장하기 위해 JsonStore를 사용합니다
        self.helmet_detected = None
        self.result_callback = None
        # self.is_running = False  # 카메라가 실행 중인지 여부를 저장하는 변수
        # self.model = None  # YOLO 모델을 저장하는 변수
        # self.camera = camera  # 외부에서 주입받은 카메라 객체
        self.helmet_result_override = helmet_result_override  # 추가된 속성
        self.mem_id = mem_id
        self.is_stopping = False  # stop 호출 중복 방지를 위한 플래그 추가

        # OpenCV로 카메라 연결
        self.capture = cv2.VideoCapture(0)

        # 카메라 화면을 즉시 출력
        self.update_event = Clock.schedule_interval(self.display_camera, 1.0 / 33.0)

        # 카메라를 먼저 켭니다
        # self.camera.play = True  # 카메라를 켭니다
        # Clock.schedule_once(self.start_model, 1.0)  # 1초 후에 모델을 실행
        Clock.schedule_once(self.process_frame, 5.0)

    def display_camera(self, *args):
        ret, frame = self.capture.read()
        if not ret or frame is None:
            print("헬멧 카메라에서 프레임을 가져올 수 없습니다.")
            self.stop()
            return
        # Kivy의 Image 위젯에 카메라 프레임을 표시하기 위해 텍스처로 변환
        buf = cv2.flip(frame, 0).tobytes()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    # 결과 콜백 함수를 설정
    def set_result_callback(self, callback):
        self.result_callback = callback

    # def start_model(self, dt):
    #     print(f"[START] start_model : =======================================")
    #     # 얼굴 검출을 위한 업데이트
    #     # Clock.unschedule(self.update_event)  # 기존 카메라 화면 업데이트 중지
    #     Clock.schedule_once(self.process_frame, 1.0)

    #     # # self.is_running = True
    #     # self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #     # Clock.schedule_once(self.process_frame, 1.0)


    # 카메라에서 프레임을 처리하는 메서드입니다 (헬멧 감지 수행)
    def process_frame(self, dt):
        print(f"[START] 헬멧인식 process_frame : =======================================")
        ret, frame = self.capture.read()
        if not ret or frame is None:
            print("helmet_model...카메라에서 프레임을 가져올 수 없습니다.")
            self.stop()
            return

        # 얼굴 검출
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cascade_file = "haarcascade_frontalface_default.xml"  # 절대경로 대신 상대경로 사용
        # cascade = cv2.CascadeClassifier(cascade_file)
        # faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        # 화면에 표시할 프레임 복사
        display_frame = frame.copy()

        # 얼굴에 사각형 그리기 (화면 표시용)
        # for (x, y, w, h) in faces:
        #     cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # if self.camera.texture:
        #     texture = self.camera.texture  # 카메라의 텍스처를 가져옵니다
        #     image_data = np.frombuffer(texture.pixels, np.uint8)  # 텍스처의 픽셀 데이터를 가져옵니다
        #     image_data = image_data.reshape(texture.height, texture.width, 4)  # 이미지 데이터를 4채널(RGBA)로 변환합니다
        #     image = cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)  # RGBA 이미지를 BGR로 변환합니다 (OpenCV에서 사용)
        #
        #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 이미지를 그레이스케일로 변환합니다
        #     faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)  # 얼굴을 검출합니다

        # if len(faces) > 0:
        print(f"[START] 헬멧인식 process_frame : 얼굴 검출 성공")
        # (x, y, w, h) = faces[0]  # 첫 번째 얼굴의 좌표를 가져옵니다
        # 이미지 파일 이름 생성
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        img_filename = f'helmet_{timestamp}_{self.mem_id}.png'

        # 이미지 인코딩 (메모리에서 바로 전송 준비)
        _, img_encoded = cv2.imencode('.png', frame)

        # 서버로 전송
        send_image_to_server(img_encoded.tobytes(), img_filename)

        # 헬멧 인증 결과 요청
        self.helmet_detected = self.request_helmet_detection_result(self.mem_id)

        # 고객센터를 통한 헬멧 결과를 1로 만드는 경우라면
        if self.helmet_result_override:
            print(f"************************ self.helmet_result_override : {self.helmet_result_override}")
            self.helmet_detected = 1
        #     # self.helmet_detected = helmet_detected
        #     print(f"[END] process_frame : helmet_detected : {self.helmet_detected}=======================================")
        print(f"************************ Helmet detected: {self.helmet_detected}")
        print(f"************************ self.result_callback: {self.result_callback}")

        # 콜백을 통해 결과 전달
        if self.result_callback:
            self.result_callback(self.helmet_detected)

        # stop 호출 중복 방지
        if not self.is_stopping:
            Clock.schedule_once(self.stop, 2.0)
                
            
        # else:
        #     print(f"[END] process_frame : NO FACE======================================")
        #     # Clock.schedule_once(self.process_frame, 0)
        #     self.helmet_detected = 2
        #     if self.result_callback:
        #         self.result_callback(self.helmet_detected)
        #     self.stop()


    def get_helmet_detected(self):
        print(f"헬멧 인증 get_helmet_detected : {self.helmet_detected}")
        # return self.helmet_detected
    
        # helmet_result_override가 True인 경우, 결과를 강제로 1로 설정
        if self.helmet_result_override:
            print("[고객센터 인증] helmet_result_override가 True이므로 helmet_detected를 1로 설정합니다.")
            self.helmet_detected = 1    
        return self.helmet_detected

    def pause(self, *args):
        # stop 중복 실행 방지
        if self.is_stopping:
            return
        print(f"[START] helmet_model pause : =======================================")
        self.is_stopping = True  # stop 실행 중 표시

        Clock.unschedule(self.process_frame)
        if self.update_event:
            Clock.unschedule(self.update_event)

        # if self.capture and self.capture.isOpened():
        #     self.capture.release()
        print("헬멧 process_frame만 일시정지되었습니다.") 

    def stop(self, *args):
        # stop 중복 실행 방지
        if self.is_stopping:
            return
        print(f"[START] helmet_model stop : =======================================")
        self.is_stopping = True  # stop 실행 중 표시

        Clock.unschedule(self.process_frame)
        if self.update_event:
            Clock.unschedule(self.update_event)

        if self.capture and self.capture.isOpened():
            self.capture.release()
        print("카메라가 정지되었습니다.")


    def request_helmet_detection_result(self, mem_id):
        url = 'http://127.0.0.1:8000/drive/run_helmet_detection/'
        data = {'mem_id': mem_id}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            return result.get('helmet_detected', 'null')
        except requests.exceptions.RequestException as e:
            print(f"헬멧 인증 결과 요청 실패: {e}")
            return 0


####### [디장고 서버에 이미지 보내기] ######## Django 서버로 이미지를 전송하는 함수
def send_image_to_server(img_data, img_filename):
    # 이미지 파일을 전송할 서버의 URL 주소
    url = 'http://127.0.0.1:8000/drive/upload_image/'
    
    # 서버에 전송할 파일 정보: 'image'라는 키에 img_filename 경로의 파일을 바이너리 읽기 모드('rb')로 엽니다.
    files = {'image': (img_filename, img_data, 'image/png')}
    
    # 서버에 함께 전송할 데이터 정보: 'img_filename'이라는 키에 이미지 파일의 이름을 저장
    data = {'img_filename': img_filename}
    
    # 예외 처리를 위해 try-except 구문을 사용하여 전송 작업을 실행
    try:
        # HTTP POST 요청을 사용해 서버에 파일과 데이터를 전송하고 응답을 받음
        response = requests.post(url, files=files, data=data)
        
        # 요청이 성공적으로 완료되지 않으면 오류 발생 (상태 코드가 200번대가 아닐 때 예외가 발생함)
        response.raise_for_status()
        
        # 요청이 성공적으로 완료된 경우 출력 메시지
        print("이미지 서버 전송 성공")
    
    # 만약 전송 과정에서 오류가 발생하면 예외를 잡아 오류 내용을 출력
    except requests.exceptions.RequestException as e:
        # 요청이 실패했을 때 실패 원인과 함께 에러 메시지를 출력
        print(f"이미지 서버 전송 실패: {e}")
