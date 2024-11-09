import os
import time
import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivy.logger import Logger
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
import requests
import numpy as np


class CamApp(MDApp):
    def __init__(self, manager, web_cam, mem_id):
        super().__init__()
        self.manager = manager
        self.web_cam = web_cam
        self.mem_id = mem_id
        self.capture = None
        self.update_event = None  # 업데이트 이벤트를 저장할 변수
        self.cropped_img_filename = None  # 추가된 부분
        self.regno1 = None
        self.regno2 = None
        self.store = JsonStore('session.json')  # 추가된 부분

        # OpenCV로 카메라 연결
        self.capture = cv2.VideoCapture(0)

        self.face_found = False
        # 카메라 화면을 즉시 출력
        self.update_event = Clock.schedule_interval(self.display_camera, 1.0 / 33.0)

        # 15초 후에 얼굴 검출 시작
        Clock.schedule_once(lambda dt: self.start_face_detection(), 10)

    def display_camera(self, *args):
        ret, frame = self.capture.read()
        if not ret or frame is None:
            print("카메라에서 프레임을 가져올 수 없습니다.")
            self.stop_camera()
            return

        # Kivy의 Image 위젯에 카메라 프레임을 표시하기 위해 텍스처로 변환
        buf = cv2.flip(frame, 0).tobytes()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    def start_face_detection(self):
        # 얼굴 검출을 위한 업데이트
        Clock.unschedule(self.update_event)  # 기존 카메라 화면 업데이트 중지
        self.update_event = Clock.schedule_interval(self.detect_faces, 1.0 / 33.0)

    def detect_faces(self, *args):
        ret, frame = self.capture.read()
        if not ret or frame is None:
            print("카메라에서 프레임을 가져올 수 없습니다.")
            self.stop_camera()
            return

        # 얼굴 검출
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_file = "haarcascade_frontalface_default.xml"  # 절대경로 대신 상대경로 사용
        cascade = cv2.CascadeClassifier(cascade_file)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        # 화면에 표시할 프레임 복사
        display_frame = frame.copy()

        # 얼굴에 사각형 그리기 (화면 표시용)
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if not self.face_found and len(faces) > 0:
            img_filename = detect_and_save_face(frame, self.mem_id)  # mem_id 전달
            if img_filename:
                print("얼굴 이미지 저장됨")
                self.face_found = True

                ### 여기 위까지가 얼굴이 있는 원본 이미지 저장 및 서버 전송 완료

                self.cropped_img_filename, self.regno1, self.regno2 = fetch_and_crop_latest_image(self.mem_id)
                print(f'{self.cropped_img_filename, self.regno1, self.regno2}')
                if self.cropped_img_filename:
                    print(
                        f"크롭된 얼굴 이미지 파일명: {self.cropped_img_filename} self.regno1: {self.regno1} self.regno2: {self.regno2}")
                    Clock.schedule_once(self.stop_camera, 2)
                    return
        else:
            print("얼굴을 찾을 수 없음")
            Clock.schedule_once(self.stop_camera, 1)

        # Kivy의 Image 위젯에 카메라 프레임을 표시하기 위해 텍스처로 변환
        buf = cv2.flip(display_frame, 0).tobytes()
        img_texture = Texture.create(size=(display_frame.shape[1], display_frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    # 15초 후 또는 얼굴이 인식된 후 카메라 인식을 종료하는 함수
    def stop_camera(self, *args):
        # 업데이트 중지
        if self.update_event:
            Clock.unschedule(self.update_event)  # 업데이트 중지

        # 카메라 연결 해제
        if self.capture and self.capture.isOpened():
            self.capture.release()

        # 카메라 종료 및 페이지 전환 처리
        if not self.face_found:
            print("얼굴을 찾지 못했습니다.")

        print("카메라 인식 종료")
        self.switch_to_mypage()  # mypage 페이지로 전환

    # 얼굴을 인식하고 이미지 저장이 완료되면 mypage 페이지로 전환하는 함수
    def switch_to_mypage(self):
        print("mypage 페이지로 전환")
        self.manager.current = "mypage"  # mypage 화면으로 전환

    def on_leave(self):
        if self.cam_app3:
            self.cam_app3.stop_camera()
            self.ids.web_cam.clear_widgets()
            if self.cam_app3.cropped_img_filename:
                self.manager.get_screen('signup').set_regimage(self.cam_app3.cropped_img_filename)
                self.manager.get_screen('signup').set_regno(self.cam_app3.regno1, self.cam_app3.regno2)
                print(
                    f"***reg_models.py*** self.cam_app3.cropped_img_filename: {self.cam_app3.cropped_img_filename} self.cam_app3.regno1: {self.cam_app3.regno1} self.cam_app3.regno2: {self.cam_app3.regno2}")

            self.cam_app3.capture.release()  # 카메라 장치 해제
            self.cam_app3 = None


# 얼굴 검출 후 원본을 저장하는 함수
def detect_and_save_face(frame, mem_id):
    cascade_file = "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(cascade_file)

    # 이미지 처리 (그레이스케일로 변환 후 얼굴 검출)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_list = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    if len(face_list) > 0:
        # 이미지 파일 이름 생성
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        img_filename = f'captured_{timestamp}_{mem_id}.png'

        # 이미지 인코딩 (메모리에서 바로 전송 준비)
        _, img_encoded = cv2.imencode('.png', frame)

        # 서버로 전송
        send_image_to_server(img_encoded.tobytes(), img_filename)
        return img_filename
    else:
        print("얼굴이 검출되지 않았습니다.")
        return None


def fetch_and_crop_latest_image(mem_id):
    # Django 서버의 최신 이미지를 가져오는 API URL
    url = 'http://127.0.0.1:8000/get_latest_image/'

    # 서버에 요청을 보내 최신 이미지를 가져옴
    response = requests.get(url)
    if response.status_code == 200:
        # 응답 헤더에서 regno1과 regno2를 가져옴
        regno1 = response.headers.get('X-Regno1', None)
        regno2 = response.headers.get('X-Regno2', None)
        print(f"regno1: {regno1}, regno2: {regno2}")

        # 바이트 데이터를 NumPy 배열로 변환
        image_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if img is None:
            print("이미지 데이터를 불러올 수 없습니다.")
            return None

        # 이미지 크롭 처리
        cropped_img_filename = crop_latest_image(img, mem_id)
        return cropped_img_filename, regno1, regno2
    else:
        print("서버에서 이미지를 가져오는 데 실패했습니다.")
        return None, None, None


# 가장 최근의 이미지를 크롭하여 저장하는 함수
def crop_latest_image(img, mem_id):
    # Haarcascade XML 파일 경로 (상대경로 사용)
    cascade_file = "haarcascade_frontalface_default.xml"  # 상대경로
    cascade = cv2.CascadeClassifier(cascade_file)  # 얼굴 검출기 초기화

    # 이미지를 그레이스케일로 변환하여 얼굴 검출
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    if len(face_list) > 0:
        # 가장 큰 얼굴 선택
        (x, y, w, h) = face_list[0]

        # 얼굴 크롭 (사각형 표시 없이)
        padding_w = int(w * 0.2)
        padding_h = int(h * 0.3)
        x1 = max(0, x - padding_w)
        y1 = max(0, y - padding_h)
        x2 = min(img.shape[1], x + w + padding_w)
        y2 = min(img.shape[0], y + h + padding_h)
        cropped_face = img[y1:y2, x1:x2]

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        cropped_img_filename = f'cropped_{timestamp}_{mem_id}.png'

        # 이미지를 메모리 내에서 인코딩하여 서버로 전송
        _, img_encoded = cv2.imencode('.png', cropped_face)
        send_image_to_server(img_encoded.tobytes(), cropped_img_filename)
        print(f"크롭된 얼굴 이미지를 서버로 전송: {cropped_img_filename}")
        return cropped_img_filename
    else:
        print("얼굴을 찾지 못했습니다.")
        return None


####### [디장고 서버에 이미지 보내기] ######## Django 서버로 이미지를 전송하는 함수
def send_image_to_server(img_data, img_filename):
    # 이미지 파일을 전송할 서버의 URL 주소
    url = 'http://127.0.0.1:8000/upload_image/'

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



