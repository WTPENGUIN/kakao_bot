"""
getBus : WGS 84 경위도 좌표를 매개로 근접 버스 정류소를 조회해 버스 도착정보를 반환하는 모듈

"""

from urllib.parse import urlencode, quote_plus
import requests
import xml.etree.ElementTree as elemTree
from math import pi,sqrt,sin,cos,atan2
import time

# 공공 데이터포털 API 서비스키
service_key = "YOUR_API_KEY"

# 네이버 지도 API키
naver_service_id = "YOUR_NAVER_MAP_SERVICE_ID"
naver_service_key = "YOUR_NAVER_MAP_SERVICE_KEY"

# 거리 구하는 함수
def haversine(pos1lat, pos1long, pos2lat, pos2long):
    lat1 = float(pos1lat)
    long1 = float(pos1long)
    lat2 = float(pos2lat)
    long2 = float(pos2long)

    degree_to_rad = float(pi / 180.0)


    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c

    return km

# 네이버 지도 좌표변환 API 파싱
def getGeo(gpsLati, gpsLong):
    
    global naver_service_id, naver_service_key

    # 반환지역
    location = "NULL"

    # API 엔드포인트
    api_URL_NAVER = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"

    # 지역 파라미터, 헤더 세팅
    coords = str(gpsLong) + "," + str(gpsLati)
    params_geo = {'coords': coords, 'sourcecrs': "epsg:4326", 'orders': "legalcode", "output": "xml"}
    headers_geo = {'X-NCP-APIGW-API-KEY-ID': naver_service_id, 'X-NCP-APIGW-API-KEY': naver_service_key}

    # 에러처리 시작
    try:
        geo_api_Result = requests.get(api_URL_NAVER, headers = headers_geo, params = params_geo)
        
        # xml 파일 파싱을 위해 파서 호출
        geo_DATA = elemTree.fromstring(geo_api_Result.text)
        
        # xml 개체로 파싱 된 데이터 중 원하는 부분 추출
        for region in geo_DATA.iter('region'):
            # '세종특별시', '대전광역시', '울산광역시' 등 광역시, 
            if('시' in region.find('area1').find('name').text):
                location = region.find('area1').find('name').text
            else:
                location = region.find('area2').find('name').text
        
        return location
    except:
        print("getGeo : 에러가 발생")
        return location

# OPEN API 지역코드 파싱
def getCityCode(loc):

    global service_key

    # 반환코드
    city_code = 0

    # API 엔드포인트
    api_URL_City = "http://openapi.tago.go.kr/openapi/service/BusRouteInfoInqireService/getCtyCodeList"

    # 서비스키가 utf-8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 정류소 파라미터 세팅
    params_location = {'serviceKey': serviceKey_decode}
    params_location_encode = urlencode(params_location, quote_via=quote_plus)

    # 에러 처리 시작
    try:
        # 요청 보내기
        location_api_Result = requests.get(api_URL_City, params=params_location_encode)
        
        # xml 파일 파싱을 위해 파서 호출
        location_DATA = elemTree.fromstring(location_api_Result.text)
        
        # 파싱 후 결과 리턴
        for location in location_DATA.iter('item'):
            if(location.find('cityname').text in loc):
                city_code = int(location.find('citycode').text)
                break
            
        return city_code
    
    except:
        print("getCityCode : 에러 발생")
        return city_code

# OPEN API 근접정류소 조회
def getStation(gpsLati, gpsLong):
    
    global service_key

    # API 엔드포인트
    api_URL_Station = "http://openapi.tago.go.kr/openapi/service/BusSttnInfoInqireService/getCrdntPrxmtSttnList"

    # 변수 선언 & 초기화
    station_List = []
    station_Dict = {}
    return_DATA = ""

    # 서비스키가 utf-8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 정류소 파라미터 세팅
    params_station = {'serviceKey': serviceKey_decode, 'gpsLati': gpsLati, 'gpsLong': gpsLong, 'numOfRows': 50}
    params_station_encode = urlencode(params_station, quote_via=quote_plus)

    # 에러 처리 시작
    try:
        # 요청 보내기
        station_api_Result = requests.get(api_URL_Station, params=params_station_encode)
        
        # xml 파일 파싱을 위해 파서 호출
        station_DATA = elemTree.fromstring(station_api_Result.text)
        count_station_DATA = 0
        
        # API 호출을 통해 온 근처 정류장 데이터
        for items in station_DATA.iter('item'):

            # 검색 범위 반경 100m
            if(haversine(gpsLati, gpsLong, float(items.find('gpslati').text), float(items.find('gpslong').text)) > 0.15):
                continue
            
            # 버스 정보 호출을 위해 필요한 데이터 딕셔너리로 포장 후 리스트에 삽입
            station_Dict = {'citycode': items.find('citycode').text, 'nodeId': items.find('nodeid').text, 'nodenm': items.find('nodenm').text}
            station_List.append(station_Dict.copy())
            station_Dict.clear()
            count_station_DATA = count_station_DATA + 1
            
            # 데이터가 없으면 정류장이 없다고 출력
            if(count_station_DATA == 0):
                print("반경 500m 이내에 정류장이 검색되지 않습니다.")
                return
    except:
        print("getBus -> 근접정류장 검색 : 오류가 발생 했습니다.")
        return "오류 발생"
    
    return station_List

# OPEN API 버스 조회
def getBus(station_List, location_code):

    global service_key

    # API 엔드포인트
    api_URL_Bus = "http://openapi.tago.go.kr/openapi/service/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList"

    # 변수 선언 & 초기화
    return_DATA = []

    # 서비스키가 utf-8로 인코딩되어 있어서 unquote로 디코딩에서 get요청을 보내야 응답이 정상적으로 옵니다.
    serviceKey_decode=requests.utils.unquote(service_key, 'utf-8')

    # 주변 정류장 데이터 리스트
    for dic in station_List:
            
        # 버스 도착 정보를 얻기 위한 API 호출 파라미터 세팅
        params_bus = {'serviceKey': serviceKey_decode, 'cityCode': dic.get('citycode'), 'nodeId': dic.get('nodeId'), 'numOfRows': 50}
        params_bus_encode = urlencode(params_bus, quote_via=quote_plus)

        # 에러 처리 시작
        try:
            # 요청 보내기
            bus_api_Result = requests.get(api_URL_Bus, params=params_bus_encode)
           
            # xml 파일 파싱을 위해 파서 호출
            bus_DATA = elemTree.fromstring(bus_api_Result.text)
            
            # 최종 데이터 반환을 위한 준비
            final_DATA_Header = ['\nO ', dic.get('nodenm'), '\n']
            count_bus_DATA = 0

            # 데이터가 있으면 반복문 돌면서 정보 파싱
            for items in bus_DATA.iter('item'):

                final_DATA = []
                minute, second = divmod(int(items.find('arrtime').text), 60)

                final_DATA.append(items.find('routeno').text)
                final_DATA.append("번 버스 - ")
                final_DATA.append(str(minute))
                final_DATA.append('분 ')
                final_DATA.append(str(second))
                final_DATA.append('초 안에 도착 \n')

                count_bus_DATA = count_bus_DATA + 1
            
            # 데이터가 없으면        
            if(count_bus_DATA == 0):

                # 만약 정류장 지역 위치와 정류장 지역 코드가 다르면 출력하지 않음 
                if(int(dic.get('citycode')) != location_code):
                    continue

                return_DATA.append(''.join(final_DATA_Header))
                return_DATA.append("데이터가 없습니다.(운행이 종료 되었거나 아직 버스가 운행 전일 수 있습니다.)\n")

            else:
                return_DATA.append(''.join(final_DATA_Header))
                return_DATA.append(''.join(final_DATA))

        except:
            print("getBus -> 버스도착정보조회 : 오류가 발생 했습니다.")
            return "오류 발생"

    return ''.join(return_DATA)
