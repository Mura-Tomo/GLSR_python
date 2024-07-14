# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import schedule
from datetime import datetime
from display import show_alarm_time
from cal import get_travel_time, calculate_wakeup_time
from load_data import load_data
from predict_weather_add_time import predict_weather_add_time

app = Flask(__name__)

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

@app.route('/api/random-number', methods=['POST'])
def main():
    api_key = "AIzaSyB0nf7_vnnBkOrBPSXHhK_--SSkbi1Iwx4"
    
    alarm_time = None
    
    user = User(current_location="大阪府堺市北区中百舌鳥町２丁", transportation_mode="driving", preparation_time=30, 
                latest_wakeup_time="12:00", earliest_event_time="05:00")
    formatted_events = load_data()
    
    if not formatted_events: # 次の日にイベントがない場合は、次の日の最遅起床時間にアラームをセットする
        now = datetime.utcnow()
        tomorrow = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
        alarm_time = tomorrow.strftime("%m月%d日 %A") + user.latest_wakeup_time
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
            alarm_time = wakeup_time.strftime("%m月%d日 %A %H:%M:%S")
        else: # 最も早いイベントが最早イベント時刻よりも早い場合、寝ないで頑張りましょう
            alarm_time = "寝ないで頑張りましょう！"
    # show_alarm_time(alarm_time, event, user, travel_time, weather_forecast)
    print(user)
    return jsonify({'alarm_time': travel_time})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# notification_time = "18:45" # 通知時間
# schedule.every().day.at(notification_time).do(main)

# while True:
#     schedule.run_pending()
#     time.sleep(1)