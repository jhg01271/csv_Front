import cv2  # OpenCV는 이미지 및 비디오 처리를 위한 라이브러리입니다.
import numpy as np  # numpy는 수학 계산 및 행렬 처리를 위한 라이브러리입니다.
from kivy.app import App  # Kivy는 파이썬 기반의 GUI 프레임워크입니다.
from kivy.uix.boxlayout import BoxLayout  # BoxLayout은 수직 또는 수평 방향으로 위젯을 배치하는 레이아웃입니다.
from kivy.uix.label import Label  # Label은 텍스트를 표시하는 위젯입니다.
from kivy.uix.camera import Camera  # Camera는 카메라 비디오 스트림을 표시하는 데 사용되는 위젯입니다.
from kivy.clock import Clock  # Clock은 주기적으로 함수를 실행하는 데 사용됩니다.
from kivy.graphics.texture import Texture  # Texture는 화면에 이미지를 그리기 위한 객체입니다.
from kivy.storage.jsonstore import JsonStore  # JsonStore는 데���터를 JSON 형식으로 저장하는 데 사용됩니다.
from deepface import DeepFace  # DeepFace는 얼굴 인식 및 비교를 위한 라이브러리입니다.
import os  # os 모듈은 파일과 디렉토리를 관리하는데 사용됩니다.
from kivymd.app import MDApp
import requests
import time

# Compare_with_last_cropped_image는 얼굴 인식을 통해 비교하는 애플리케이션입니다.
class Compare_with_last_cropped_image(MDApp):
    def __init__(self, camera, mem_id=None, **kwargs):
        super().__init__(**kwargs)
        self.camera = camera  # 외부에서 주입받은 카메라 객체
        self.mem_id = mem_id
        self.verification_result_override = False
        self.is_running = False  # 실행 상태를 저장하는 변수 초기화
        self.call_count = 0  # 호출 횟수를 저장하는 변수 추가

        # JSON 파일을 사용하여 세션 정보를 저장
        self.store = JsonStore('session.json')  # 이 줄을 추가하여 store 속성을 초기화

        # 카메라를 먼저 켜고, 일정 시간 후에 모델을 실행
        self.camera.play = True  # 카메라를 켭니다
        self.is_running = True
        Clock.schedule_once(self.process_frame, 1.0)  # 1초 후에 모델을 실행

    # def start_model(self, dt):
    #     Clock.schedule_once(self.process_frame, 0)
    
    
# 카메라에서 프레임을 받아 처리하는 함수
    def process_frame(self, dt):
        if self.camera and self.camera.texture:  # 카메라와 텍스처가 있는지 확인
            # 카메라 텍스처를 numpy 배열로 변환 (RGBA 형식)
            texture = self.camera.texture
            image_data = np.frombuffer(texture.pixels, np.uint8)
            image_data = image_data.reshape(texture.height, texture.width, 4)
            # OpenCV가 사용하는 BGR 형식으로 이미지 변환
            image = cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)
            
            # 이미지를 메모리 내에서 인코딩하여 서버로 전송
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            img_filename = f'current_image_{timestamp}.png'
            _, img_encoded = cv2.imencode('.png', image)
            send_image_to_server(img_encoded.tobytes(), img_filename)

            # 현재 카메라 이미지와 마지막 저장된 이미지 비교
            comparison_result = self.compare_with_last_cropped_image()
            
            # 텍스처가 이미 업데이트된 경우 다시 반전되지 않도록 확인
            if not hasattr(self, 'flipped_texture') or self.flipped_texture is None:
                # 상하 반전 수행
                flipped_image = cv2.flip(image, 0)
            
                # 현재 카메라 화면을 앱에 업데이트 (이미지를 반전하여 표시)
                buf = flipped_image.tobytes()
                texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera.texture = texture
                # 텍스처가 한 번만 반전되었음을 기록
                self.flipped_texture = True
                
            # self.stop()

            # 비교 결과 반환
            return comparison_result
        else:
            print(f"[END] process_frame : NO FACE======================================")
            Clock.schedule_once(self.process_frame, 0)  
              


    # 앱을 일시 정지하는 함수
    def stop(self):
        print(f"compare_model stop=========================================")
        # if self.is_running:
        self.camera.play = False  # 카메라 중지
        self.is_running = False  # 실행 상태 업데이트
        Clock.unschedule(self.process_frame)  # 프레임 처리 중지
        
    # 얼굴 인식 확인 요청
    def compare_with_last_cropped_image(self):
        url = 'http://127.0.0.1:8000/drive/verify_identity/'
        data = {'mem_id': self.mem_id}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            return result.get('verified', 'null')
        except requests.exceptions.RequestException as e:
            print(f"얼굴 인식 확인 요청 실패: {e}")
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
          
