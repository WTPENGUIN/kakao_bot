"""
getAir : AIRKOREA OPEN API에서 대기 미세먼지 농도를 조회해 반환하는 모듈

"""
from urllib.parse import urlencode, quote_plus
import requests, json
import xml.etree.ElementTree as elemTree

# 공공 데이터포털 API 서비스키
service_key = "YOUR_API_KEY"

# 지수 치환함수
def read_grade(grade):

    if(grade == "-" or grade is None):
        return "측정값 없음"

    int_grade = int(grade)

    if(int_grade == 1):
        return "좋음"
    elif(int_grade == 2):
        return "보통"
    elif(int_grade == 3):
        return "나쁨"
    elif(int_grade == 4):
        return "매우 나쁨"
    else:
        return "잘못된 값"

# 공공API 대기지수 파싱 함수
def getAir(geo):

    global service_key

    # 변수 선언 & 초기화
    air_result_DATA = ""
    
    # API 엔드포인트
    api_air_URL = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnMesureSidoLIst"

    # 서비스키가 utf8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 파라미터 세팅
    params = {'serviceKey': serviceKey_decode, 'numOfRows': 50, 'sidoName': geo, 'searchCondition': 'DAILY'}
    params_encode = urlencode(params, quote_via=quote_plus)

    # 에러 처리 시작

    # 요청 보내기
    air_api_Result = requests.get(api_air_URL, params=params_encode)

    # xml 파일 파싱을 위해 파서 호출
    air_DATA = elemTree.fromstring(air_api_Result.text)
    time_pre = ""

    # 데이터 파싱
    for item in air_DATA.iter('item'):
        time_cur = item.find('dataTime').text

        if(time_pre == ""):
            time_pre = time_cur
        else:
            if(time_cur != time_pre):
                break
            
        air_result_DATA = air_result_DATA + ('지역 : ' + item.find('cityName').text + '\n') + \
            ('미세먼지 : ' + item.find('pm10Value').text + '\n') + ('초미세먼지 : ' + item.find('pm25Value').text + '\n\n')
    
    return air_result_DATA

# 테스트 코드
# print(getAir('울산'))
