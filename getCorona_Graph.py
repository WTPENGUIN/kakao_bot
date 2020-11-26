
from urllib.parse import urlencode, quote_plus
import requests, json
import xml.etree.ElementTree as elemTree
import datetime

# 공공 데이터포털 API 서비스키
service_key = "YOUR_API_KEY"

# 공공API 코로나 관련 데이터 파싱 함수
def getjson():

    global service_key

    # API 엔드포인트
    api_URL = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"

    # 변수 선언 & 초기화
    response_DATA = []

    # 현재 시간
    now = datetime.datetime.today().strftime('%Y%m%d')
    weekago = (datetime.datetime.now()-datetime.timedelta(weeks=1)).strftime('%Y%m%d')

    # 서비스키가 utf-8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 파라미터 세팅
    params = {'serviceKey': serviceKey_decode, 'startCreateDt': weekago, 'endCreateDt': now}
    params_encode = urlencode(params, quote_via=quote_plus)

    # 요청 보내기
    corona_api_Result = requests.get(api_URL, params=params_encode)

    # xml 파일 파싱을 위해 파서 호출
    corona_DATA = elemTree.fromstring(corona_api_Result.text)

    # xml 파일 파싱
    for item in corona_DATA.iter('item'):
        if(item.find('gubun').text == '합계'):
            allCnt = int(item.find('localOccCnt').text) + int(item.find('overFlowCnt').text)
            response_DATA.append({'x': item.find('createDt').text[:-12], 'y': allCnt})
    
    response_DATA.reverse()

    return json.dumps(response_DATA)
