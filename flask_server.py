from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import pymysql
import getAir
import getBus
import getCorona
import getWeather
import getCorona_Graph
 
app = Flask(__name__)

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

# server init start
home_station = getBus.getStation("YOUR_HOME_X_CORDINATE", "YOUR_HOME_Y_CORDINATE")
home_code = getBus.getCityCode(getBus.getGeo("YOUR_HOME_X_CORDINATE", "YOUR_HOME_Y_CORDINATE"))
# server init end

# Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html')

# 메인 페이지 출력
@app.route("/")
def main_page():
    return render_template('/index.html')
@app.route("/index")
def index_page():
    return render_template('/index.html')

# 코로나 차트 페이지 출력
@app.route("/corona")
def corona_page():
    return render_template('/corona.html')

# 로그인 페이지 출력
@app.route("/login")
def login_page():
    return render_template('/login.html')
 
# 그래프 json 가져오기
@app.route("/<TARGET>.json")
def data(TARGET):
    sensor_data = []

    if(TARGET == 'sound'):
        connection = pymysql.connect("YOUR_DB_CONNECTION_INFO")
    elif(TARGET == 'humi'):
        connection = pymysql.connect("YOUR_DB_CONNECTION_INFO")
    elif(TARGET == 'temp'):
        connection = pymysql.connect("YOUR_DB_CONNECTION_INFO")
    elif(TARGET == 'corona'):
        return getCorona_Graph.getjson()
    else:
        return 'Not Available Parameter.'

    cursor = connection.cursor()

    if(TARGET == 'sound'):
        cursor.execute("SELECT 1000*time, value from VALUE")

    elif(TARGET == 'humi'):
        cursor.execute("SELECT 1000*time, humi from VALUE")

    elif(TARGET == 'temp'):
        cursor.execute("SELECT 1000*time, temp from VALUE")

    results = cursor.fetchall()
    for row in results:
        time = datetime.fromtimestamp(row[0] / 1000.0).strftime('%Y-%m-%d-%H-%M-%S')
        sensor_data.append({'x': time, 'y': row[1]})

    connection.close()

    return json.dumps(sensor_data)

# 카카오톡 챗봇 날씨 API 응답
@app.route("/weather", methods=['POST'])
def weather():

    # 기상청 RSS 데이터 파싱 함수 호출
    weather_data = getWeather.getWEATHER_RSS()

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
        return response_data_text(getAir.getAir(geometry))
    else:
        return response_data_text("입력하신 지역이 공공API에서 제공하는 범위 내에 없습니다.")

# 카카오톡 챗봇 코로나 API 응답
@app.route("/corona_read", methods=['POST'])
def corona_read():
    return response_data_text(getCorona.getCorona())

# 카카오톡 챗봇 버스 API 응답 
@app.route("/get_bus", methods=['POST'])
def get_bus():
    return response_data_text(getBus.getBus(home_station, home_code))

# 카카오톡 챗봇 센서값 응답
@app.route("/home_state", methods=['POST'])
def home_state():
    return response_data_text("구현중입니다.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded = True)
