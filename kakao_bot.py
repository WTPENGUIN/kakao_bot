from flask import Flask, render_template, request, jsonify
from urllib.parse import urlencode, quote_plus
import urllib.request, re
import xml.etree.ElementTree as elemTree
import requests, json
import pymysql
import datetime
 
app = Flask(__name__)

# 공공 데이터포털 API 서비스키
service_key = "YOUR_SERVICE_KEY"

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
    air_data_list = []
    
    # API 엔드포인트
    api_URL = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

    #서비스키가 utf8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 파라미터 세팅
    params = {'serviceKey': serviceKey_decode, 'numOfRows': 10, 'pageNo': 1, 'sidoName': geo, 'ver': 1.3, '_returnType': json}
    params_encode = urlencode(params, quote_via=quote_plus)

    # 에러 처리 시작
    try:
        # 요청 보내기
        air_DATA = requests.get(api_URL, params=params_encode).json()

        for list in air_DATA['list']:
        
            # 데이터 있는지 체크
            if(list['khaiGrade'] != '' and list['pm10Grade'] != '' and list['pm25Grade'] != ''):
                air_data_list.append("\nO 측정소 이름 : " + list['stationName'])
                air_data_list.append("\nO 측정 시간 : " + list['dataTime'])
                air_data_list.append("\nO 대기 지수 : " + read_grade(list['khaiGrade']))
                air_data_list.append("\nO 미세먼지 지수 : " + read_grade(list['pm10Grade']))
                air_data_list.append("\nO 초미세먼지 지수 : " + read_grade(list['pm25Grade']))
                air_data_list.append("\n")
            # 없으면 넘어감
            else:
                continue

        return ' '.join(air_data_list)
    except:
        return "에러가 발생 했습니다. 잠시 후 다시 요청해 보세요."

# 공공API 코로나 관련 데이터 파싱 함수
def getCorona():

    global service_key

    # API 엔드포인트
    api_URL = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"

    # 변수 선언 & 초기화
    response_DATA = ""
    data_COUNT = 0

    # 현재 시간
    now = datetime.datetime.today().strftime('%Y%m%d')

    # 서비스키가 utf-8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 파라미터 세팅
    params = {'serviceKey': serviceKey_decode, 'startCreateDt': now, 'endCreateDt': now}
    params_encode = urlencode(params, quote_via=quote_plus)

    # 에러 처리 시작
    try:
        # 요청 보내기
        corona_api_Result = requests.get(api_URL, params=params_encode)
        
        #xml 파일 파싱을 위해 파서 호출
        corona_DATA = elemTree.fromstring(corona_api_Result.text)
        
        # xml 파일 파싱
        for item in corona_DATA.iter('item'):
            if(item.find('gubun').text == '합계'):
                response_DATA = response_DATA + ('일자 : ' + now + '\n') + ('O 지역 발생 : ' + item.find('localOccCnt').text + '\n') + \
                                ('O 해외 발생 : ' + item.find('overFlowCnt').text + '\n')
            data_COUNT = data_COUNT + 1
            
        # 데이터 여부 판단 후 요청 보내기
        if(data_COUNT == 0):
            response_DATA = response_DATA + "데이터가 없습니다."
            return response_DATA 
        else:
            return response_DATA
    except:
        return "에러가 발생 했습니다. 잠시 후 다시 요청 해 보세요."

# 기상청 RSS 함수
def getWEATHER_RSS():
    
    # 기상청 온도 예보
    weather_string = ""
    
    # 기상청 RS
    weather_URL = "http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108"

    #기상청 RSS 열기
    ufile = urllib.request.urlopen(weather_URL)
    contents = ufile.read().decode('utf-8')
    wf_a = re.findall(r'<wf>(.+)</wf>', contents)

    for wf in wf_a:
        if('CDATA' in wf):
            wf = wf.replace('<br />', '')
            wf = wf.replace('          ', ' ')
            wf = wf.replace('○', '\n\n○')
            wf = wf[9:len(wf) - 3]
            weather_string = "기상청 RSS 데이터입니다." + wf
            break
    
    return weather_string

# 메세지를 카카오톡에서 처리 할 수 있게 JSON으로 변환하는 함수
def response_data_text(text):

    res = {
        "version" : "2.0",
        "template" : {
            "outputs" : [
                {
                    "simpleText" : {
                        "text" : text
                    }
                }
            ]
        }
    }

    return jsonify(res)

# 웹 페이지로 활용되는 서버가 아니므로 안내 메세지 출력
@app.route("/")
def check():
    return 'This Flask Server not used Web.'
 
# 그래프 json 가져오기
@app.route("/<TARGET>.json")
def data(TARGET):
    if(TARGET == 'sound'):
        connection = pymysql.connect(host='localhost', user='dbconnect', password='5678', db='SOUND', charset='utf8')
    elif(TARGET == 'humi'):
        connection = pymysql.connect(host='localhost', user='dbconnect', password='5678', db='HT', charset='utf8')
    elif(TARGET == 'temp'):
        connection = pymysql.connect(host='localhost', user='dbconnect', password='5678', db='HT', charset='utf8')
    else:
        return 'Give Available Parameter.'

    cursor = connection.cursor()

    if(TARGET == 'sound'):
        cursor.execute("SELECT 1000*time, value from VALUE")

    elif(TARGET == 'humi'):
        cursor.execute("SELECT 1000*time, humi from VALUE")

    elif(TARGET == 'temp'):
        cursor.execute("SELECT 1000*time, temp from VALUE")

    results = cursor.fetchall()
    connection.close()

    return json.dumps(results)

# 사운드 센서 그래프 출력
@app.route("/Sound")
def graph_sound():
    return render_template('Sound.html')

# 습도 그래프 출력
@app.route("/Humi")
def graph_humi():
    return render_template('Humi.html')

# 온도 그래프 출력
@app.route("/Temp")
def graph_temp():
    return render_template('Temp.html')

# 카카오톡 챗봇 날씨 API 응답
@app.route("/weather", methods=['POST'])
def weather():

    # 기상청 RSS 데이터 파싱 함수 호출
    weather_data = getWEATHER_RSS()

    # 응답
    return response_data_text(weather_data)

# 카카오톡 챗봇 대기지수 API 응답
@app.route("/air_read", methods=['POST'])
def air_read():

    # 지역 범위
    geometry_list = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주", "세종"]

    # 요청 받아서 JSON으로 변환
    req = request.get_json()

    # 카카오 i 오픈빌더에 정의한 location의 값 얻어옴
    geometry = req["action"]["detailParams"]["location"]["value"]

    # 지역 범위 내에 있으면 공공API를 이용하여 응답, 없으면 에러처리
    if(geometry in geometry_list):
        return response_data_text(getAir(geometry))
    else:
        return response_data_text("입력하신 지역이 공공API에서 제공하는 범위 내에 없습니다.")

# 카카오톡 챗봇 코로나 API 응답
@app.route("/corona_read", methods=['POST'])
def corona_read():
    return response_data_text(getCorona())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded = True)