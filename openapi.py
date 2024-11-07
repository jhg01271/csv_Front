import json
import requests
import random




### 주소를 활용해서 위경도값 알아내기
def addr_location(address):
    # 주소 값을 format에 제대로 전달되도록 수정
    url = "https://dapi.kakao.com/v2/local/search/address.json?query={}".format(address)
    headers = {"Authorization" : "KakaoAK dda5e1ed8153c481b29e1bb026d90c06"}
    api_json = json.loads(requests.get(url, headers=headers).text)
    
    # documents 배열이 비어있을 경우에 대한 예외 처리 추가
    if api_json.get("documents"):
        match_first = api_json["documents"][0]["address"]
        return float(match_first["x"]), float(match_first["y"])
    else:
        return None, None  # 만약 주소를 찾지 못했을 경우 None 반환


print(addr_location("부산 수영구 광일로20번가길 11"))



### 현재 위치 위경도값 알아내기
def get_current_location():
    # ipinfo API를 이용해 IP 기반의 위치 정보 가져오기
    response = requests.get("https://ipinfo.io/")
    location_data = response.json()

    # 위도와 경도를 문자열로 추출
    loc = location_data['loc']  # 'loc' 값은 "위도,경도" 형식
    latitude, longitude = loc.split(',')

    return  float(latitude), float(longitude)

# 현재 위치의 위도와 경도 출력
print(get_current_location())



# 한국 내에서 임의의 위치 생성 (위도: 33.0 ~ 38.0, 경도: 125.0 ~ 130.0)
def get_random_location():
    random_lat = random.uniform(33.0, 38.0)   # 위도 범위
    random_lon = random.uniform(125.0, 130.0)  # 경도 범위
    return float(random_lat), float(random_lon)

print(get_random_location())

