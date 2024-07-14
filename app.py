from flask import Flask, jsonify, request
from flask_cors import CORS
import schedule
from datetime import datetime
from display import show_alarm_time
from cal import get_travel_time, calculate_wakeup_time
from load_data import load_data
from predict_weather_add_time import predict_weather_add_time

app = Flask(__name__)
CORS(app)

class User:
    def __init__(self, current_location, transportation_mode, preparation_time, latest_wakeup_time, earliest_event_time):
        self.current_location = current_location # 現在地 (住所)
        self.transportation_mode = transportation_mode # 移動手段
        self.preparation_time = preparation_time # 支度時間
        self.latest_wakeup_time = latest_wakeup_time # 最遅起床時刻
        self.earliest_event_time = earliest_event_time # 最早イベント時刻

class Event:
    def __init__(self, user, event):
        self.name = event['summary']
        self.start_time = event['start_time']
        if event['location']:
            self.destination = event['location']
        else:
            self.destination = user.current_location # イベントの場所が設定されていない場合は、現在地を目的地に設定

response = {}

@app.route('/api/random-number', methods=['GET', 'POST'])
def main():
    global response

    if request.method == 'POST':
        api_key = "AIzaSyB0nf7_vnnBkOrBPSXHhK_--SSkbi1Iwx4"
        weekdays = ["(月)", "(火)", "(水)", "(木)", "(金)", "(土)", "(日)"]
        
        # user = User(current_location="大阪府堺市北区中百舌鳥町２丁", transportation_mode="driving", preparation_time=30, 
        #             latest_wakeup_time="12:00", earliest_event_time="05:00")
        data = request.json
        user = User(
            current_location=data['current_location'],
            transportation_mode=data['transportation_mode'],
            preparation_time=data['preparation_time'],
            latest_wakeup_time=data['latest_wakeup_time'],
            earliest_event_time=data['earliest_event_time']
        )
        print(f"{user.current_location}")
        print(f"{user.transportation_mode}")
        print(f"{user.preparation_time}")
        print(f"{user.latest_wakeup_time}")
        print(f"{user.earliest_event_time}")
        formatted_events = load_data()
        
        if not formatted_events: # 次の日にイベントがない場合は、次の日の最遅起床時間にアラームをセットする
            now = datetime.utcnow()
            tomorrow = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
            weekday = weekdays[tomorrow.weekday()]
            alarm_time = tomorrow.strftime("%m/%d ")+ weekday + user.latest_wakeup_time
            # show_alarm_time(alarm_time, event=None, user=user, travel_time=None, weather_forecast=None)
        else:
            event = Event(user, formatted_events)

            buffer_time = 10  # 猶予時間（分） イベントの重要度によって変える (ex. テストなら余裕を持って 15 分前など)

            travel_time = get_travel_time(api_key, user, event)
            weather_add_time, weather_forecast = predict_weather_add_time(event)
            wakeup_time = calculate_wakeup_time(event, user, travel_time, buffer_time, weather_add_time)
            
            print(f"予定開始時間: {event.start_time}")
            print(f"移動時間: {travel_time} 分")
            print(f"支度時間: {user.preparation_time} 分")
            print(f"猶予時間: {buffer_time} 分")
            print(f"目的地の天気: {weather_forecast}, その影響: {weather_add_time} 分")
            print(f"起床時間: {wakeup_time}")
            if wakeup_time:
                alarm_time = wakeup_time.strftime("%m/%d")
                weekday = weekdays[wakeup_time.weekday()]
                alarm_time += f" {weekday} {wakeup_time.strftime('%H:%M:%S')}"   
            else: # 最も早いイベントが最早イベント時刻よりも早い場合、寝ないで頑張りましょう
                alarm_time = "寝ないで頑張りましょう！"
            print(f"アラーム時間: {alarm_time}")

            start_time = datetime.fromisoformat(event.start_time).strftime("%H:%M")
            destination = event.destination.split(' ')[-1]
            mode = {"walking": "徒歩", "driving": "車", "cycling": "自転車"}
            transportation_mode = mode[user.transportation_mode]
            weather = {"Clear": "晴れ", "Clouds": "くもり", "Rain": "雨", "Thunderstorm": "嵐", "Snow": "雪",}

            try:
                weather_forecast = weather[weather_forecast]
            except KeyError:
                weather_forecast = "取得できませんでした"

            response = {
                'event_name': event.name,
                'start_time': start_time,
                'destination': destination,
                'transportation_mode': transportation_mode,
                'travel_time': travel_time,
                'weather_forecast': weather_forecast,
                'alarm_time': alarm_time
            }
    # show_alarm_time(alarm_time, event, user, travel_time, weather_forecast)
        return jsonify(response)
    elif request.method == 'GET':
        return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)