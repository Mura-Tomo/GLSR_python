from datetime import datetime, timezone
import dateutil.parser
import requests

def get_lat_lng_from_location(location, api_key):
    # Google Geocoding APIエンドポイント
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": api_key
    }
    
    # APIリクエスト
    response = requests.get(url, params=params)
    
    # レスポンスのチェック
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # 緯度と経度を取得
            lat_lng = data['results'][0]['geometry']['location']
            return lat_lng['lat'], lat_lng['lng']
        else:
            return None, None
    else:
        return None, None

def get_weather_from_lat_lng_date(lat, lng, api_key, tgt_date):
    # OpenWeatherMap APIエンドポイント
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": api_key,
        "units": "metric",
        "lang": "ja"
    }
    
    # APIリクエスト
    response = requests.get(url, params=params)
    
    # レスポンスのチェック
    if response.status_code == 200:
        data = response.json()

        #tgt_date直前の予測を調べる
        for i, forecast in enumerate(data['list']):
            forecast_time = dateutil.parser.parse(forecast['dt_txt']).astimezone(timezone.utc)
            #print("forecast_date:", forecast_time)
            if forecast_time > tgt_date:
                if i > 0:
                    # print("forecast_date:", dateutil.parser.parse(data['list'][i-1]['dt_txt']).astimezone(timezone.utc))
                    return data['list'][i-1]['weather'][0]['main']
                else:
                    return None
    
    return None

def predict_weather_add_time(event):
    # 位置、時間情報
    location = event.destination
    tgt_date = event.start_time

    # Google Maps APIキー
    google_api_key = "AIzaSyB0nf7_vnnBkOrBPSXHhK_--SSkbi1Iwx4"
    # OpenWeatherMapのAPIキー
    openweather_api_key = "73f715aae4998171b12043e2d487726a"

    # 緯度と経度を取得
    latitude, longitude = get_lat_lng_from_location(location, google_api_key)
    tgt_date = dateutil.parser.parse(tgt_date).astimezone(timezone.utc)
    # print("tgt_date:", tgt_date)

    # 天気予報を取得
    if latitude and longitude:
        forecast = get_weather_from_lat_lng_date(latitude, longitude, openweather_api_key, tgt_date)
        # print(f"Location: {location}")
        # print(f"Latitude: {latitude}, Longitude: {longitude}")
        # print(forecast)
    else:
        forecast = None
        print("位置情報の取得に失敗しました。")

    #天気の追加時間を計算
    add_time_by_weather = {"Clear":0, "Clouds":0, "Rain":10, "Thunderstorm":20, "Snow":30,}
    try:
        add_time = add_time_by_weather[forecast]
    except KeyError:
        add_time = 0
    
    return add_time, forecast