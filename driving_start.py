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

BASE_URL = "http://127.0.0.1:8000/drive"

Builder.load_file('driving_start.kv')


class DrivingStart(MDScreen):
    def __init__(self, **kwargs):
        # 부모 클래스인 MDScreen의 __init__ 메서드를 호출해 초기화 (MDScreen의 모든 속성과 기능을 사용 가능하게 함)
        super().__init__(**kwargs)
        # self.is_checking_helmet = False
        # self.is_verifying_identity = False
        self.is_retrying = False  # 재시도 플래그 추가
        self.retry_count = 0  # 재시도 횟수를 추적하는 변수 추가
        self.cam_app = None
        self.helmet_result = None
        self.helmet_result_override = False
        self.verification_result = None
        self.verification_result_override = False
        self.perfect_count = 0
        self.count = 0

#########################################################################################

    # 헬멧 인증 모델 콜백 함수 정의
    def helmet_result_callback(self, result):
        self.helmet_result = result
        print("[모델 결과] Helmet Model Result:", self.helmet_result)
        
        if self.helmet_result_override or self.helmet_result == 1:
            print("[모델 결과] 헬멧 착용 확인")
            model_result = [1, 0]
            self.make_df(self.mem_id, model_result)
            self.result_list.append(2)
            self.retry_count = 0 # 성공 시 재시도 횟수 초기화
            self.is_retrying = False # 헬멧 착용 확인 시 재시도 플래그 초기화
            Clock.schedule_once(lambda dt: self.popup_manager.show_helmet_verification_success_popup(), 2.0)
            
        elif self.helmet_result == 0:
            if not self.is_retrying and self.retry_count < 2:  # 재시도가 진행 중이 아니면(self.is_retrying == False)
                self.is_retrying = True  # 재시도 시작 표시
                self.retry_count += 1
                print(f"[모델 결과] 헬멧 미착용 확인 : 재시도 횟수 {self.retry_count}")
                Clock.schedule_once(self.retry_helmet_detection, 3.0)
            elif self.retry_count >= 2:
                print(f"[모델 결과] 헬멧 미착용 확인 : 재시도 횟수 {self.retry_count+1} : 팝업 표시")
                model_result = [0, 0]
                print(f"[모델 결과] self.mem_id : {self.mem_id}")
                self.make_df(self.mem_id, model_result, "0")
                self.result_list.append(3)
                Clock.schedule_once(lambda dt: self.popup_manager.show_helmet_warning_popup(), 2.0)
                self.retry_count = 0  # 재시도 횟수 초기화
                self.is_retrying = False  # 최종 실패 후 재시도 중단
        else: # NO FACE self.helmet_result == 2
            print("[모델 결과] 헬멧 검출 실패")
            self.is_retrying = False
        
    # 사용자 인증 모델 콜백 함수 정의
    def iv_result_callback(self, result):
        self.verification_result = result
        print("[모델 결과] Identity Verification Model Result:", self.verification_result)
        
        if self.verification_result_override or self.verification_result == 1:
            print("[모델 결과] 사용자 인증 확인")
            self.ids.btn_verify.disabled = False  # 인증 버튼을 활성화
            model_result = [1, 1]
            self.make_df(self.mem_id, model_result)
            self.result_list.append(0)
            self.retry_count = 0 # 성공 시 재시도 횟수 초기화
            self.is_retrying = False # 헬멧 착용 확인 시 재시도 플래그 초기화
            if self.perfect_count == 0:
                current_location = get_current_location()
                print(f"check_same_person : current_location : {current_location}=========================================")
                self.insert_rental_log(self.mem_id, self.result_list, current_location)
                self.rent_no = self.get_rent_no(self.mem_id)
                print(f"check_same_person : ################## self.rent_no : {self.rent_no}=========================================")
        
        elif self.verification_result == 0:
            if not self.is_retrying and self.retry_count < 1:  # 재시도가 진행 중이 아니면(self.is_retrying == False)
                self.is_retrying = True  # 재시도 시작 표시
                self.retry_count += 1
                print(f"[모델 결과] 사용자 인증 실패 : 재시도 횟수 {self.retry_count}")
                
                # 이전에 예약된 이벤트 모두 취소
                Clock.unschedule(self.retry_identity_verification)
                
                Clock.schedule_once(self.retry_identity_verification, 3.0)
            elif self.retry_count >= 1:
                print(f"[모델 결과] 사용자 인증 실패 : 재시도 횟수 {self.retry_count+1} : 팝업 표시")
                model_result = [1, 0]
                print(f"[모델 결과] self.mem_id : {self.mem_id}")
                self.make_df(self.mem_id, model_result, "0")
                self.result_list.append(1)
                Clock.schedule_once(lambda dt: self.popup_manager.show_face_verification_failed_popup(), 2.0)
                self.retry_count = 0  # 재시도 횟수 초기화
                self.is_retrying = False  # 최종 실패 후 재시도 중단
                
        elif self.verification_result == 3:
            # ID 도용 확인 시 팝업 표시
            print(f"[모델 결과] ID 도용 확인 : {self.verification_result == 3}")
            Clock.unschedule(self.retry_identity_verification)
            Clock.schedule_once(lambda dt: self.popup_manager.show_id_theft_popup(), 2.0)
        
        else: # NO FACE self.helmet_result == 2
            print("[모델 결과] 사용자 인증 실패")
            self.is_retrying = True
            self.retry_count = 0
            Clock.unschedule(self.retry_identity_verification)  # 이벤트 해제
            Clock.schedule_once(lambda dt: self.popup_manager.show_no_face_popup(), 2.0)

#########################################################################################

    # 화면이 사용자에게 보여질 때 실행되는 메서드 (화면이 활성화될 때 호출됨)
    def on_enter(self, *args):
        # self.initialize_state()
        # self.perfect_count = 0

        self.cookies = SimpleCookie()
        self.popup_manager = PopupManager(self)
        # self.cam_app = None

        # self.cam_app2 = None
        # self.helmet_detected = False
        # self.helmet_result = 0
        # self.helmet_result_count = 0
        # self.dialog = None
        # self.count = 0
        self.result_list = []
        # self.face_verification_attempts = 0
        # self.helmet_result_override = False
        # self.verification_result_override = False
        # self.verification_result = 0
        # self.capture = None # OpenCV로 카메라 초기화
        # self.initialize_camera()
        
        # driving_start 진입 후 헬멧 인증 모델 실행
        if not self.cam_app:
            self.start_helmet_detection(self.helmet_result_callback)
        

    # 헬멧 인증 모델 실행 메서드
    def start_helmet_detection(self, result_callback):
        # 기존 cam_app 종료
        if self.cam_app:
            self.cam_app.stop()
            self.cam_app = None
            Clock.schedule_once(lambda dt: self.helmet_check_stop_and_restart(result_callback), 0.1)
        # 새로운 HelmetDetectionApp 인스턴스 생성
        else:
            self.create_helmet_detection(result_callback)

    # 헬멧 인증 모델 중지 확인 및 재시작 메서드
    def helmet_check_stop_and_restart(self, result_callback):
        # cam_app의 stop 완료 확인
        if self.cam_app and not self.cam_app.is_stopped:
            Clock.schedule_once(lambda dt: self.helmet_check_stop_and_restart(result_callback), 0.1)
        else:
            self.create_helmet_detection(result_callback)
            
    # 헬멧 인증 모델 생성 메서드
    def create_helmet_detection(self, result_callback):
        app = MDApp.get_running_app()
        self.mem_id = app.store.get('session')['mem_id']
        self.cam_app = HelmetDetectionApp(web_cam=self.ids.web_cam3, 
                                          mem_id=self.mem_id, 
                                          helmet_result_override=self.helmet_result_override
                                          )
        self.cam_app.set_result_callback(result_callback)
        print("헬멧 인증 모델이 새로 시작되었습니다.")       

    # 헬멧 인증 모델 재시작 메서드
    def retry_helmet_detection(self, *args):
        print("[재시도] 헬멧 인식 모델을 처음부터 다시 실행합니다.")
        self.start_helmet_detection(self.helmet_result_callback)  # 헬멧 인증 모델을 처음부터 다시 실행
        self.is_retrying = False  # 재시도 후 플래그 초기화
        
#########################################################################################

    # 사용자 인증 모델 실행 메서드
    def start_identity_verification(self, result_callback):
        # 기존 cam_app 종료
        if self.cam_app:
            self.cam_app.stop()
            self.cam_app = None
            Clock.schedule_once(lambda dt: self.iv_check_stop_and_restart(result_callback), 0.1)
        # 새로운 IdentityVerificationApp 인스턴스 생성
        else:
            self.create_identity_verification(result_callback)
            
    # 사용자 인증 모델 중지 확인 및 재시작 메서드
    def iv_check_stop_and_restart(self, result_callback):
        # cam_app의 stop 완료 확인
        if self.cam_app and not self.cam_app.is_stopped:
            Clock.schedule_once(lambda dt: self.iv_check_stop_and_restart(result_callback), 0.1)
        else:
            self.create_identity_verification(result_callback)

    # 사용자 인증 모델 생성 메서드retry_helmet_detection
    def create_identity_verification(self, result_callback):
        app = MDApp.get_running_app()
        self.mem_id = app.store.get('session')['mem_id']
        self.cam_app = Compare_with_last_cropped_image(web_cam=self.ids.web_cam3, 
                                                       mem_id=self.mem_id, 
                                                       verification_result_override=self.verification_result_override)
        self.cam_app.set_result_callback(result_callback)
        print("사용자 인증 모델이 새로 시작되었습니다.")       

    # 사용자 인증 모델 재시작 메서드
    def retry_identity_verification(self, *args):
        print(f"[사용자 인증 재인증] retry_identity_verification : self.is_retrying : {self.is_retrying}")
        if not self.is_retrying:  # is_retrying이 False면 재시도 중단
            return
        # 이전에 예약된 이벤트 모두 취소
        Clock.unschedule(self.retry_identity_verification)
        
        print("[재시도] 사용자 인증 모델을 처음부터 다시 실행합니다.")
        self.start_identity_verification(self.iv_result_callback)  # 사용자 인증 모델을 처음부터 다시 실행
        self.is_retrying = False  # 재시도 후 플래그 초기화

#########################################################################################

    # 특정 UI 요소를 숨기는 메서드
    def verify_and_change_buttons(self):
        print("[UI 변경] 인증 완료")
        
        if self.ids.btn_verify.text == "인증 완료":
            # 모든 실행 상태를 중지
            self.cam_app.stop()
            
            # 푸시 알림 보내기
            show_system_notification("인증 서비스 실행중", "1분마다 인증을 재시작합니다.")
            show_kivy_popup("인증 서비스 실행중", "1분마다 인증을 재시작합니다.", delay=1)
            
            self.ids.title_box.text = "운행중 인증확인"
            self.ids.text_box.text = "헬멧 착용한 상태를 유지해주세요"
            self.ids.hide_box.height = 0  # hide_box의 높이를 0으로 설정하여 숨김
            self.ids.hide_box.text = ""  # hide_box의 텍스트를 빈 문자열로 변경
            self.ids.hide_box.opacity = 0  # hide_box의 투명도를 0으로 설정해 완전히 숨김
            self.ids.btn_verify.text = "운행 재개"  # '운행 일시정지'로 변경
            self.ids.btn_verify.on_release = self.toggle_camera
            self.ids.btn_customer_service.opacity = 1
            self.ids.btn_customer_service.disabled = False

            print("120초마다 self.on_enter() 실행")
            # self.scheduled_event = Clock.schedule_interval(self.on_enter2, 60)
            self.scheduled_event= Clock.schedule_once(self.retry_helmet_detection, 120)
            print(f"self.scheduled_event : {self.scheduled_event}")

    def toggle_camera(self):
        if self.cam_app:
            if self.ids.btn_verify.text == "운행 일시정지":
                self.cam_app.stop()
                self.ids.btn_verify.text = "운행 재개"
                # 스케줄링된 이벤트를 일시정지
                if hasattr(self, 'scheduled_event') and self.scheduled_event is not None:
                    Clock.unschedule(self.scheduled_event)
                    self.scheduled_event = None
                    print("스케줄링된 이벤트가 일시정지되었습니다.")
            elif self.ids.btn_verify.text == "운행 재개":
                # self.retry_helmet_detection()
                self.ids.btn_verify.text = "운행 일시정지"
                # 스케줄링된 이벤트를 재개
                if self.scheduled_event is None:
                    print(f"")
                    self.perfect_count = 1
                    self.scheduled_event = Clock.schedule_interval(self.retry_helmet_detection, 60)
                    print(f"스케줄링된 이벤트가 재개되었습니다.")


    # 운행 종료
    def end_driving(self):
        if self.cam_app:
            self.cam_app.stop()
            self.cam_app = None
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
        
    # 화면을 떠날 때 (다른 화면으로 이동할 때) 실행되는 메서드
    def on_leave(self):
        if self.cam_app:
            self.cam_app.stop()
            self.cam_app = None

#########################################################################################
    ### 데이터프레임 만들기 함수
    def make_df(self, mem_id, model_result, service=None):
        self.count += 1
        response = self.send_make_df(self.count, mem_id, model_result, service)
        if response.get('status') == 'success':
            print("Insert cert log df success")
        else:
            print("Insert cert log df failed")
    
    def send_make_df(self, count, mem_id, model_result, service):
        url = f'{BASE_URL}/make_df/'
        data = {
            'count': count,
            'mem_id': mem_id,
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