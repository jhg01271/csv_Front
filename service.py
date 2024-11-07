# from jnius import autoclass
# from time import sleep
# from rental_log import show_push_notification

# ##########################  [서비스 스크립트 작성]  ##########################################
# # 안드로이드 환경에서 앱이 백그라운드에서도 계속 실행되도록 하려면, 
# # Android의 서비스(Service) 기능을 활용하는 것이 일반적입니다. 
# # Kivy와 KivyMD를 사용하여 Android 앱을 개발할 때, Python for Android(p4a)와 함께 
# # Android 서비스로 백그라운드 작업을 수행할 수 있습니다.
# def main():
#     # Android 서비스로 실행될 작업
#     while True:
#         print("백그라운드 서비스 실행 중...")
#         show_push_notification("알림", "30분마다 기능이 재실행되었습니다.", delay=0)
#         sleep(1800)  # 30분 대기

# if __name__ == '__main__':
#     main()

# ### buildozer.spec 파일 수정
# # (list) Android service to declare
# # android.services = background_service:service.py