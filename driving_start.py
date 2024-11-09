from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from helmet_model import HelmetDetectionApp
from compare_model import Compare_with_last_cropped_image
import database
from http.cookies import SimpleCookie
from kivymd.app import MDApp
import pandas as pd
from datetime import datetime
from popup_manager import PopupManager
from kivy.metrics import dp, sp
from kivy.uix.camera import Camera
import requests

from openapi import get_current_location, get_random_location
import subprocess  # subprocess 모듈을 가져옴
from 푸시알림 import show_system_notification, show_kivy_popup

# Django API 서버 URL 설정
BASE_URL = "http://127.0.0.1:8000/drive"


# .kv 파일에서 레이아웃을 정의한 것을 로드함 (화면 레이아웃)
Builder.load_file('driving_start.kv')

# DrivingStart 클래스는 화면을 관리하는 MDScreen을 상속받음
class DrivingStart(MDScreen):    
    def __init__(self, **kwargs):
        # 부모 클래스인 MDScreen의 __init__ 메서드를 호출해 초기화 (MDScreen의 모든 속성과 기능을 사용 가능하게 함)
        super().__init__(**kwargs)
        self.is_checking_helmet = False
        self.is_verifying_identity = False

        # self.cookies = SimpleCookie()
        # self.popup_manager = PopupManager(self)  # PopupManager 인스턴스 생성 시 self를 parent로 전달


    def initialize_state(self):
        self.cookies = SimpleCookie()
        self.popup_manager = PopupManager(self)
        self.cam_app = None
        self.cam_app2 = None
        self.helmet_detected = False
        self.helmet_result = 0
        self.helmet_result_count = 0
        self.dialog = None
        self.count = 0
        self.result_list = []
        self.face_verification_attempts = 0
        self.helmet_result_override = False
        self.verification_result_override = False
        self.verification_result = 0
        self.capture = None # OpenCV로 카메라 초기화
        self.initialize_camera()

    def initialize_camera(self):
        """
        카메라를 초기화하는 메서드.
        """
        # 기존 카메라 해제
        if self.capture and self.capture.isOpened():
            print('Capturing !!!!!!!!! 캡쳐가 켜져 있어서 기존 캡쳐를 해제합니다.')
            self.capture.release()

          # 카메라 장치 해제
        # self.capture = cv2.VideoCapture(0)  # OpenCV로 카메라 초기화
        # # 기존 카메라 리소스 해제
        # if hasattr(self, 'camera') and self.camera.play:
        #     self.camera.play = False  # 카메라 중지
        #     print("reset initialize_camera1 : 기존 카메라 리소스 해제 완료.")
        #
        # # 새로운 카메라 초기화
        # self.camera = self.ids.camera  # .kv 파일에서 정의한 카메라 위젯을 가져옴
        # self.camera.play = True  # 카메라가 자동으로 켜지도록 설정
        # print("reset initialize_camera2 : 카메라 초기화 완료.")

    # 화면이 사용자에게 보여질 때 실행되는 메서드 (화면이 활성화될 때 호출됨)
    def on_enter(self, *args):
        self.initialize_state()
        # self.df = pd.DataFrame()
        self.perfect_count = 0
        # 헬멧 감지 앱 초기화
        if not self.cam_app:
            app = MDApp.get_running_app()
            mem_id = app.store.get('session')['mem_id']
            self.cam_app = HelmetDetectionApp(web_cam=self.ids.web_cam3, mem_id=mem_id) # OpenCV 캡처 객체 전달
            print("헬멧 감지 앱 초기화 완료.")

        Clock.schedule_once(self.check_helmet_detection, 2.0)


    def on_enter2(self, *args):   
        self.initialize_state()
        self.perfect_count = 1
        # 헬멧 감지 앱 초기화
        if not self.cam_app:
            app = MDApp.get_running_app()
            mem_id = app.store.get('session')['mem_id']
            self.cam_app = HelmetDetectionApp(web_cam=self.ids.web_cam3, mem_id=mem_id)
            print("헬멧 감지 앱 초기화 완료.")

        Clock.schedule_once(self.check_helmet_detection, 2.0)


    # 주기적으로 헬멧 감지 여부를 확인하는 메서드
    def check_helmet_detection(self, dt):
        if self.is_checking_helmet:
            return
        self.is_checking_helmet = True
        try:
            print(f"[START] check_helmet_detection :=======================================")
            app = MDApp.get_running_app()
            if app.store.exists('session'):
                mem_id = app.store.get('session')['mem_id']  # 멤버 ID를 가져옴
                print(f'mem_id : {mem_id}')

            # 카메라 앱이 실행 중이고, 헬멧이 감지되었다면
            if self.cam_app and self.cam_app.process_frame(0) != 'null':
                print(f"check_helmet_detection : self.cam_app.process_frame(0) : =========================================")
                self.helmet_detected = True  # 헬멧 감지 여부를 True로 설정
                helmet_result = self.cam_app.process_frame(0)  # 헬멧 감지 결과를 가져옴
                print(f"check_helmet_detection : helmet_result : {helmet_result}")

                # helmet_result_override가 True이면 헬멧이 감지된 것으로 처리
                if self.helmet_result_override:
                    helmet_result = 1

                # 헬멧 안씀 결과값 : 0
                if helmet_result == 0: 
                    self.helmet_result_count += 1
                    print(f"check_helmet_detection : 헬멧 안씀 횟수 {self.helmet_result_count} : 000000000000000")
                    
                    # # 최초로 모델 가동 시 추가 작업
                    # if self.perfect_count == 0:
                    #     database.insert_rental_log(mem_id, helmet_result, current_location)
                    #     self.perfect_count += 1
                    
                    # 모델 가동 완료. 결과값 : 0 (헬멧 안씀)
                    if self.cam_app:
                        Clock.schedule_once(self.cam_app.process_frame, 1.0)  # 1초 후에 process_frame 실행
                        Clock.schedule_once(self.check_helmet_detection, 2.0)  # 2초 후에 헬멧 감지 확인
                        
                    # 모델 3회째 가동되었을 때
                    if self.helmet_result_count & 3 == 0: ## 3의 배수일 때
                        print(f"check_helmet_detection : 헬멧 안씀 횟수 {self.helmet_result_count} : 3의 배수일 때")
                        # 예약된 작업을 해제하는 방법
                        Clock.unschedule(self.cam_app.process_frame)
                        Clock.unschedule(self.check_helmet_detection)
                        model_result = [0, 0]
                        self.make_df(mem_id, model_result, "0")
                        self.result_list.append(3)
                        Clock.schedule_once(lambda dt: self.popup_manager.show_helmet_warning_popup(), 2.0)  # 2초 후에 팝업 실행
                
                # 헬멧 씀 결과값 : 1
                else:
                    print("check_helmet_detection : 헬멧 씀 11111111111111")
                    model_result = [1, 0]
                    self.make_df(mem_id, model_result)
                    self.result_list.append(2)
                    # self.cam_app.stop()
                    # if self.perfect_count == 0:
                    #     database.insert_rental_log(mem_id, helmet_result, current_location)
                    #     self.perfect_count += 1
                    if self.perfect_count == 0:
                        # 최초로 헬멧 탐지 시에만 헬멧 탐지 성공 팝업 실행
                        Clock.schedule_once(lambda dt: self.popup_manager.show_helmet_verification_success_popup(), 1.0)  # 2초 후에 팝업 실행
                    else:   
                        self.start_identity_verification()
            else:
                print("헬멧 감지 앱이 초기화되지 않았거나 헬멧이 감지되지 않았습니다.")
        finally:
            self.is_checking_helmet = False


    # 얼굴 인식 시작
    def start_identity_verification(self, *args):
        if self.is_verifying_identity:
            return
        self.is_verifying_identity = True
        try:
            app = MDApp.get_running_app()
            if app.store.exists('session'):
                mem_id = app.store.get('session')['mem_id']
                print(f'[start] start_identity_verification== mem_id : {mem_id}=========================================')
                
                # 카메라를 켜고 화면에 표시
                self.initialize_camera()
                # 앞의 cam_app을 초기화하고 다음으로 넘아갑니다.
                self.stop_camera()
                self.cam_app = None

                # 얼굴 인식 앱 시작
                self.cam_app2 = Compare_with_last_cropped_image(web_cam=self.ids.web_cam3, mem_id=mem_id)
                # print(f"start_identity_verification : self.cam_app2 : ========================================")
                
                Clock.schedule_once(self.check_same_person, 0)
                # print(f"start_identity_verification : Clock.schedule_once : =========================================")

        finally:
            self.is_verifying_identity = False

    # 동일 인물인지 확인
    def check_same_person(self, dt):
        print(f"[START] check_same_person=========================================")
        if self.cam_app2:
            # 현재 로그인된 회원의 mem_id 가져오기
            app = MDApp.get_running_app()
            logged_in_mem_id = None
            if app.store.exists('session'):
                logged_in_mem_id = app.store.get('session')['mem_id']
            
            # 얼굴모델 가동됨
            # Compare_with_last_cropped_image 클래스의 mem_id와 비교
            if logged_in_mem_id and logged_in_mem_id == self.cam_app2.mem_id:
                
                # 고객센터 연결을 통해 임의로 결과를 1로 설정한 경우 덮어쓰지 않음
                if self.verification_result_override == 100:
                    print("임의로 설정된 얼굴 인식 결과를 유지합니다. verification_result_override : 100")
                    verification_result = 1
                else:
                    # 최초 실행시 얼굴 인식 결과 가져오기
                    print(f"안면인식 최초시작 Start first process_frame : =========================================")
                    verification_result = self.cam_app2.process_frame(0)
                    print(f"check_same_person : verification_result33333 : {verification_result}=========================================")
                    
                # 얼굴 인식 성공 verification_result == 1
                if verification_result == 1:
                    print(f"check_same_person : verification_result11111 : {verification_result}=========================================")
                    self.ids.btn_verify.disabled = False  # 인증 버튼을 활성화
                    result = 0     
                    model_result = [1,1] 
                    self.result_list.append(0)
                    # 헬멧 씀, 도용 안됨 결과값을 데이터프레임에 추가
                    self.make_df(logged_in_mem_id, model_result)
                    
                    if self.perfect_count == 0:
                        current_location = get_current_location()
                        print(f"check_same_person : current_location : {current_location}=========================================")
                        self.insert_rental_log(logged_in_mem_id, self.result_list, current_location)
                        self.rent_no = self.get_rent_no(logged_in_mem_id)
                        print(f"check_same_person : ################## self.rent_no : {self.rent_no}=========================================")
                    # self.show_verification_success_popup()
                    # self.start_driving()
                    
                # 얼굴 인식 실패 verification_result == 0
                else:
                    # verification_result == 0
                    print(f"check_same_person : verification_result00000 : {verification_result}=========================================")
                    result = 1
                    model_result = [1,0] 
                    self.result_list.append(1)
                    self.face_verification_attempts += 1
                    print(f"=============self.face_verification_attempts 시도횟수 : {self.face_verification_attempts}=========================================")
                    Clock.schedule_once(self.check_same_person, 1.0)  # check_helmet_detection 실행
                    
                    # 얼굴 인식 시도횟수가 3의 배수일 때
                    if self.face_verification_attempts & 3 == 0:
                        print(f"안면인식 시도횟수 {self.face_verification_attempts} : 3의 배수일 때=========================================")
                        self.make_df(logged_in_mem_id, model_result)
                        Clock.unschedule(self.check_same_person)
                        self.popup_manager.show_face_verification_failed_popup()
                    
            print(f"데이터베이스 작업 완료: mem_id = {logged_in_mem_id}")
        else:
            print(f"mem_id 불일치: 로그인 = {logged_in_mem_id}, 카메라 앱 = {self.cam_app2.mem_id}")



    # 화면을 떠날 때 (다른 화면으로 이동할 때) 실행되는 메서드
    def on_leave(self):
        # 카메라 앱이 있으면 카메라를 중지하고 화면에서 제거
        if self.cam_app:
            self.cam_app.stop()  # 카메라 기능을 중지
        if self.cam_app2:
            self.cam_app2.stop()  # 카메라 기능을 중지
            Clock.unschedule(self.check_helmet_detection)  # 스케줄링을 중지
            # self.ids.camera_box.clear_widgets()  # camera_box에서 카메라 위젯을 모두 제거
            self.cam_app = None  # cam_app을 None으로 설정해 메모리를 해제 (다시 돌아오면 새로 생성할 수 있도록)
            self.cam_app2 = None  # cam_app2을 None으로 설정해 메모리를 해제 (다시 돌아오면 새로 생성할 수 있도록)

    # 다른 화면으로 전환하는 메서드 (screen_name에 해당하는 화면으로 이동)
    def switch_screen(self, screen_name):
        self.manager.current = screen_name  # 화면 전을 요청

    # # 헬멧이 감지되면 운행 화면으로 이동하는 메서드
    # def verify_and_go_to_driving(self):
    #     if self.helmet_detected:  # 헬멧이 감지되었다면
    #         self.manager.current = 'index'  # 'index'라는 이름의 화면으로 이동 (운행 시작 화면일 것으로 추정됨)

    # 특정 UI 요소를 숨기는 메서드
    def verify_and_change_buttons(self):
        print("verify_and_change_buttons 함수 실행 중...")
        
        if self.ids.btn_verify.text == "인증 완료":
            # 모든 실행 상태를 중지
            self.stop_all_running_processes()
            
            # 푸시 알림 보내기
            show_system_notification("인증 서비스 실행중", "1분마다 재인증을 시작합니다.")
            show_kivy_popup("인증 서비스 실행중", "1분마다 재인증을 시작합니다.", delay=1)
            
            self.ids.title_box.text = "운행중 인증확인"
            self.ids.text_box.text = "헬멧 착용한 상태를 유지해주세요"
            self.ids.hide_box.height = 0  # hide_box의 높이를 0으로 설정하여 숨김
            self.ids.hide_box.text = ""  # hide_box의 텍스트를 빈 문자열로 변경
            self.ids.hide_box.opacity = 0  # hide_box의 투명도를 0으로 설정해 완전히 숨김
            self.ids.btn_verify.text = "운행 재개"  # '운행 일시정지'로 변경
            self.ids.btn_verify.on_release = self.toggle_camera
            self.ids.btn_customer_service.opacity = 1
            self.ids.btn_customer_service.disabled = False
            
            # 1분(60초)마다 self.on_enter() 실행
            print("3분(180초)마다 self.on_enter2() 실행")
            # self.scheduled_event = Clock.schedule_interval(self.on_enter2, 60)
            self.scheduled_event= Clock.schedule_once(self.on_enter2, 60)
            print(f"self.scheduled_event : {self.scheduled_event}")

    def toggle_camera(self):
        if self.cam_app:
            if self.ids.btn_verify.text == "운행 일시정지":
                self.stop_camera()
                self.ids.btn_verify.text = "운행 재개"
                # 스케줄링된 이벤트를 일시정지
                if hasattr(self, 'scheduled_event') and self.scheduled_event is not None:
                    Clock.unschedule(self.scheduled_event)
                    self.scheduled_event = None
                    print("스케줄링된 이벤트가 일시정지되었습니다.")
            elif self.ids.btn_verify.text == "운행 재개":
                self.start_camera()
                self.ids.btn_verify.text = "운행 일시정지"
                # 스케줄링된 이벤트를 재개
                if self.scheduled_event is None:
                    self.scheduled_event = Clock.schedule_interval(self.on_enter2, 60)
                    print("스케줄링된 이벤트가 재개되었습니다.")

    # 운행 종료
    def end_driving(self):
        if self.cam_app:
            self.stop_camera()
            self.cam_app2 = None
        # print(f"Inserting to cert log: {self.df}")
        try:
            self.insert_to_cert_log()
        except Exception as e:
            print(f"Error inserting to cert log: {e}")
        print(f"Updating rental log: {self.rent_no}, {self.result_list}")
        ### 추후에 현재 위치 값으로 수정하기!!! ###
        end_location = get_random_location()
        # self.rent_no = get_rent_no(mem_id)
        self.update_rental_log(self.rent_no, self.result_list, end_location)

        # 반복 작업 중지 및 초기화
        if hasattr(self, 'scheduled_event'):
            Clock.unschedule(self.scheduled_event)
            del self.scheduled_event
            print("스케줄링된 이벤트가 중단되고 초기화되었습니다.")

        # 버튼 상태를 초기화
        print("버튼 상태 초기화 중...")
        self.ids.title_box.text = "운행전 인증확인"
        self.ids.text_box.text = "헬멧 착용 후 얼굴을 인식해주세요"
        self.ids.hide_box.height = dp(120)
        self.ids.hide_box.text = "운행전 인증확인\n 헬멧 착용 후 얼을 인식해주세요"
        self.ids.hide_box.opacity = 1
        self.ids.btn_verify.text = "인증 완료"
        self.ids.btn_verify.disabled = True
        self.ids.btn_verify.on_release = self.verify_and_change_buttons
        self.ids.btn_customer_service.opacity = 0
        self.ids.btn_customer_service.disabled = True
        print("버튼 상태 초기화 완료")
        self.manager.current = 'index'


    def start_camera(self):
        """
        카메라를 재시작하는 메서드.
        """
        if self.cam_app:
            # self.cam_app.camera.play = True  # 헬멧 감지 앱의 카메라 시작
            # self.cam_app.is_running = True  # 실행 상태 업데이트
            # Clock.schedule_once(self.cam_app.process_frame, 0)  # 프레임 처리 시작
            print("헬멧 감지 카메라 시작됨.")

        if self.cam_app2:
            # self.cam_app2.camera.play = True  # 얼굴 인식 앱의 카메라 시작
            # self.cam_app2.is_running = True  # 실행 상태 업데이트
            # Clock.schedule_once(self.cam_app2.process_frame, 0)  # 프레임 처리 시작
            print("얼굴 인식 카메라 시작됨.")

    def stop_camera(self):
        """
        카메라를 일시정지하는 메서드.
        """
        if self.cam_app:
            self.cam_app.stop()
            print("헬멧 감지 카메라 정지됨.")

        if self.cam_app2:
            self.cam_app2.stop()
            print("얼굴 인식 카메라 정지됨.")

    def stop_all_running_processes(self):
        # HelmetDetectionApp의 self.is_running을 False로 설정
        if self.cam_app:
            self.cam_app.is_running = False
            print("HelmetDetectionApp의 실행 상태가 중지되었습니다.")

        # Compare_with_last_cropped_image의 self.is_running을 False로 설정
        if self.cam_app2:
            self.cam_app2.is_running = False
            print("Compare_with_last_cropped_image의 실행 상태가 중지되었습니다.")


    ### 데이터프레임 만들기 함수
    def make_df(self, mem_id, model_result, service=None):
        self.count += 1
        response = self.send_make_df(self.count, mem_id, model_result, service)
        if response.get('status') == 'success':
            print("Insert rental log success")
        else:
            print("Insert rental log failed")
    
    def send_make_df(self, count, logged_in_mem_id, model_result, service):
        url = f'{BASE_URL}/make_df/'
        data = {
            'count': count,
            'mem_id': logged_in_mem_id,
            'model_result': model_result,
            'service': service
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    # 데이터베이스에 렌탈 데이터 넣기 함수
    def insert_rental_log(self, mem_id, helmet_result, current_location):
        response = self.send_insert_rental_log(mem_id, helmet_result, current_location)

        if response.get('status') == 'success':
            print("Insert rental log success")
        else:
            print("Insert rental log failed")

    def send_insert_rental_log(self, mem_id, helmet_result, current_location):
        url = f'{BASE_URL}/insert_rental_log/'
        data = {
            'mem_id': mem_id,
            'helmet_result': helmet_result,
            'current_location': current_location
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    # 데이터베이스에 인증 데이터 넣기 함수
    def insert_to_cert_log(self):
        # cert_data = df.to_dict(orient='records')
        response = self.send_insert_cert_log()

        if response.get('status') == 'success':
            print("Insert cert log success")
        else:
            print("Insert cert log failed")

    def send_insert_cert_log(self):
        url = f'{BASE_URL}/insert_cert_log/'
        # cert_data = self.df.to_dict(orient='records')
        try:
            response = requests.post(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}


    ### 데이터베이스에 렌탈 데이터 업데이트 함수
    def update_rental_log(self, rent_no, result_list, end_location):
        print(f"update_rental_log : {result_list}")
        response = self.send_update_rental_log(rent_no, result_list, end_location)
        if response.get('status') == 'success':
            print("Update rental log success")
        else:
            print(f"Update rental log failed : {response.get('message')}")

    def send_update_rental_log(self, rent_no, result_list, end_location):
        url = f'{BASE_URL}/update_rental_log/'
        data = {
            'rent_no': rent_no,
            'result_list': result_list,
            'end_location': end_location
        }
        print(f"update_rental_log : data : {result_list}")
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")



    ### 데이터베이스에 렌탈 데이터 rent_no 가져오기 함수    
    def get_rent_no(self, mem_id):
        response = self.send_get_rent_no(mem_id)
        print(f'send_get_rent_no의 mem_id : {mem_id}')

        if response.get('status') == 'success':
            rent_no = response.get('rent_no')
            print(f"Get rent_no success : {rent_no}")
            return rent_no  # rent_no return
        else:
            print("Get rent_no failed")
        
    def send_get_rent_no(self, mem_id):
        url = f'{BASE_URL}/get_rent_no/'
        data = {
            'mem_id': mem_id,
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {'status': 'fail', 'message': '서버 오류 발생'}






















