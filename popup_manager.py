from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.app import MDApp
from kivy.clock import Clock
from sound import Play # 음성 알람

class PopupManager:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.beep_event = None  # Clock 이벤트를 저장할 변수 추가
        self.repeat_beep_event = None  # 반복 beep 이벤트를 저장할 변수 추가
        self.sound_player = Play()  # Play 인스턴스 생성

    def is_any_popup_open(self):
        return self.dialog is not None and self.dialog.open

###########################################[헬멧, 얼굴 인식 실패 팝업]###########################################
    def show_warning_popup(self, title, text, on_retry, on_help):
        self.dialog = MDDialog(
            title=title,
            text=text,
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text="재인증" if on_retry else "고객센터 연결",
                    md_bg_color="#00289B",
                    text_color="#FFFFFF",
                    elevation=0,
                    on_release=on_retry if on_retry else self.connect_to_customer_service_face
                ),
                MDRaisedButton(
                    text="인증문제 해결" if on_help else "취소",
                    md_bg_color="#b2b2b3",
                    text_color="#FFFFFF",
                    elevation=0,
                    on_release=on_help if on_help else self.cancel_and_switch_to_index
                ),
            ],
        )
        self.dialog.bind(on_dismiss=self.stop_beeping)
        self.dialog.open()
        self.start_beeping()

    def show_helmet_warning_popup(self):
        self.show_warning_popup(
            title='헬멧 인식 실패',
            text="헬멧이 인식되지 않습니다.\n헬멧을 착용하시고 재인증 진행해주세요!",
            on_retry=self.retry_and_close_popup,
            on_help=self.show_help_popup
        )

    def show_face_verification_failed_popup(self):
        self.show_warning_popup(
            title='얼굴 인식 실패',
            text="얼굴 인식에 실패했습니다. 고객센터로 연결하시겠습니까?",
            on_retry=None,
            on_help=None
        )

###########################################[헬멧 인식 실패 팝업 재인증 버튼]###########################################
    def retry_and_close_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss(force=True)  # 현재 열려 있는 다이얼로그 닫기
            self.dialog = None
        self.retry_helmet_detection(*args)  # 다음 작업 진행
        
    def retry_helmet_detection(self, *args):
        if self.parent.cam_app:  # self.cam_app 대신 self.parent.cam_app 사용
            Clock.schedule_once(self.parent.cam_app.process_frame, 2.0)  # 1초 후에 process_frame 실행
            Clock.schedule_once(self.parent.check_helmet_detection, 2.5)  # 2초 후에 헬멧 감지 확인
        if self.dialog:
            self.dialog.dismiss()

###########################################[헬멧, 얼굴 인식 실패 음성 알림]###########################################
    def start_beeping(self):
        print(f"[Start] start_beeping : self.sound_player.beep :")
        # 처음엔 1초 후 beep 메서드를 호출
        self.beep_event = Clock.schedule_once(self.sound_player.beep, 1.0)
        self.start_repeat_beep()
        
    def start_repeat_beep(self):
        print(f"[Start] start_repeat_beep : self.sound_player.beep :")
        # 6초마다 beep 메서드를 호출
        self.repeat_beep_event = Clock.schedule_interval(self.sound_player.beep, 6.0)

    def stop_beeping(self, *args):
        # beep 이벤트 중지
        if self.beep_event:
            self.beep_event.cancel()
            self.beep_event = None
        if self.repeat_beep_event:
            self.repeat_beep_event.cancel()
            self.repeat_beep_event = None

###########################################[헬멧 인식 실패 팝업 고객센터 버튼]###########################################
    def show_help_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title='고객센터 안내',
            text="헬멧을 착용했음에도 인식되지 않을 시 고객센터 연결을 눌러주세요.",
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text="고객센터 연결",
                    md_bg_color="#00289B",  # 버튼 배경색 설정
                    text_color="#FFFFFF",  # 텍스트 색상 설정
                    elevation=0,  # 그림자 제거
                    on_release=self.connect_to_customer_service
                ),
                MDRaisedButton(
                    text="취소",
                    md_bg_color="#b2b2b3",  # 버튼 배경색 설정
                    text_color="#FFFFFF",  # 텍스트 색상 설정
                    elevation=0,  # 그림자 제거
                    on_release=self.cancel_and_show_helmet_warning
                ),
            ],
        )
        self.dialog.open()

    def connect_to_customer_service(self, *args):
        self.parent.helmet_result = 1  # helmet_result 값을 1로 설정
        self.parent.helmet_result_override = True  # 결과 덮어쓰기를 방지
        print(f"connect_to_customer_service : self.parent.helmet_result : {self.parent.helmet_result}")
        if self.parent.cam_app:
            print(f"connect_to_customer_service : self.parent.cam_app : {self.parent.cam_app}")
            Clock.schedule_once(self.parent.check_helmet_detection, 1.0)  # check_helmet_detection 실행
        if self.dialog:
            self.dialog.dismiss(force=True)
            self.dialog = None
    def cancel_popup(self, *args):
        self.dialog.dismiss(force=True)

    def cancel_and_show_helmet_warning(self, *args):
        if self.dialog:
            self.dialog.dismiss()  # 현재 열려 있는 다이얼로그 닫기
        self.show_helmet_warning_popup()  # 헬멧 경고 팝업 다시 열기




###########################################[얼굴 인식 실패 팝업 고객센터 버튼]###########################################
    def connect_to_customer_service_face(self, *args):
        self.dialog.dismiss()
        self.face_verification_success(MDApp.get_running_app().store.get('session')['mem_id'])
        
    def face_verification_success(self, *args):
        # self.parent.verification_result = 1  # helmet_result 값을 1로 설정
        self.parent.verification_result_override = 100  # 결과 덮어쓰기를 방지하는 플래그 설정
        print(f"face_verification_success : self.parent.verification_result : {self.parent.verification_result}")
        if self.parent.cam_app:
            print(f"face_verification_success : self.parent.cam_app : {self.parent.cam_app}")
            Clock.schedule_once(self.parent.check_same_person, 1.0)  # check_helmet_detection 실행
        self.dialog.dismiss()     
        


    def cancel_and_switch_to_index(self, *args):
        if self.dialog:
            self.dialog.dismiss()  # 현재 열려 있는 다이얼로그 닫기
        self.parent.switch_screen('index')  # 'index' 페이지로 이동
