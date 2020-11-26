"""
getWeather : 기상청 육상 중기예보 RSS 데이터를 조회해 가공한 후 반환하는 모듈
"""

from urllib.parse import urlencode, quote_plus
import requests, json
import xml.etree.ElementTree as elemTree

# 기상청 RSS 함수
def getWEATHER_RSS():
    
    # 기상청 온도 예보
    weather_string = "기상청 육상 중기예보 RSS 데이터입니다."
    
    # 기상청 RS
    weather_URL = "http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108"
    
    # 요청 보내기
    weather_rss_Result = requests.get(weather_URL)
    
    # xml 파일 파싱을 위해 파서 호출
    weather_DATA = elemTree.fromstring(weather_rss_Result.text)

    # 데이터 파싱
    for wf in weather_DATA.iter('wf'):
        wf_text = wf.text
        if("br" in wf_text) :
            # 필요없는 부분 치환해서 지우기
            wf_text = wf_text.replace('<br />', '')
            wf_text = wf_text.replace('          ', ' ')
            wf_text = wf_text.replace('○', '\n\n○')
            weather_string = weather_string + wf_text
            break

    return weather_string

# 테스트코드
# print(getWEATHER_RSS())