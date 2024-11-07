### 설치해야함
# pip install easyocr

# import easyocr
# import cv2
# import logging

# # Suppress EasyOCR logging
# logging.getLogger('easyocr').setLevel(logging.WARNING)

# # EasyOCR Reader 초기화 (한국어와 영어 지원 예시)
# reader = easyocr.Reader(['ko', 'en'], gpu=False)

# def extract_text_and_resident_number(image_path):
#     # 이미지 읽기
#     img = cv2.imread(image_path)

#     # OCR 수행
#     result = reader.readtext(img)

#     # OCR 결과에서 텍스트만 추출
#     texts = [res[1] for res in result]
    
#     # 주민번호를 포함한 텍스트 추출
#     resident_numbers = []
#     for text in texts:
#         # 주민번호 형식이 있는 경우 추가
#         if len(text) == 14 and text[6] == '-':
#             resident_numbers.append(text)

#     return resident_numbers

# # 사용 예시
# image_path = "abc.jpg"
# extracted_resident_numbers = extract_text_and_resident_number(image_path)
# print("추출된 주민번호:", extracted_resident_numbers)


### ================================ PaddleOCR 간단 버전

###### 이거 설치해야함 pip install paddlepaddle
# from paddleocr import PaddleOCR

# # PaddleOCR 객체 생성 (언어 설정)
# ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 'en'은 영어

# # 이미지에서 텍스트 추출
# result = ocr.ocr('download.jpg')

# # 결과 출력
# for line in result:
#     for word_info in line:
#         print(word_info[1][0])  # 텍스트 추출



### ================================ PaddleOCR 간단 버전

######이거 설치해야함  pip install paddlepaddle
import re
import logging
from paddleocr import PaddleOCR

# 로깅 비활성화
logging.disable(logging.CRITICAL)  # 모든 로깅 비활성화

# PaddleOCR 객체 생성 (언어 설정)
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 'en'은 영어

# 이미지에서 텍스트 추출
result = ocr.ocr('download.jpg')

# 주민등록번호 패턴 정의
jumin_pattern = r'(\d{6})-(\d{7})'  # 6자리와 7자리를 그룹으로 분리

# 주민등록번호 추출 리스트 (regno1, regno2 쌍을 저장)
jumin_numbers = []

# 결과에서 주민등록번호 추출 및 분리
for line in result:
    for word_info in line:
        text = word_info[1][0]  # 인식된 텍스트
        # 정규 표현식으로 주민등록번호 찾기
        matches = re.findall(jumin_pattern, text)
        if matches:
            for match in matches:
                regno1, regno2 = match  # 각각 6자리와 7자리로 분리
                jumin_numbers.append((regno1, regno2))  # (regno1, regno2) 형태로 저장

# 추출된 주민등록번호 출력
print("추출된 주민등록번호:")
for regno1, regno2 in jumin_numbers:
    print(f"regno1: {regno1}, regno2: {regno2}")





