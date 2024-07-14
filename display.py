import tkinter as tk
from tkinter import messagebox
import locale
from datetime import datetime

# 日本語のロケールを設定
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

def on_yes(alarm_time):
    messagebox.showinfo("選択", f"{alarm_time}にアラームを設定しました")
    root.destroy()

def on_no():
    messagebox.showinfo("選択", "アラームを設定しませんでした")
    root.destroy()

def show_alarm_time(alarm_time, event, user, travel_time, weather_forecast):
    global root
    root = tk.Tk()
    root.title("アラーム時間")

    # 背景色を設定
    root.configure(bg="#f0f0f0")

    start_time = datetime.fromisoformat(event.start_time).strftime("%H:%M")
    destination = event.destination.split(' ')[-1]
    mode = {"walking": "徒歩", "driving": "車", "cycling": "自転車"}
    transportation_mode = mode[user.transportation_mode]
    weather = {"Clear": "晴れ", "Clouds": "くもり", "Rain": "雨", "Thunderstorm": "嵐", "Snow": "雪",}
    
    try:
        weather_forecast = weather[weather_forecast]
    except KeyError:
        weather_forecast = "取得できませんでした"
    
    # ラベルの設定 
    label_text = f"<明日の最も早い予定>\nイベント名: {event.name}\n開始時間: {start_time}\n場所: {destination} ({transportation_mode} で {travel_time} 分)\n天気: {weather_forecast}\n\nアラーム時間: {alarm_time}\nこの時間にアラームを設定しますか？"
    label = tk.Label(root, text=label_text, font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#333", anchor="w", justify="left")
    label.pack(padx=20, pady=20)

    # ボタンフレームの作成
    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(padx=20, pady=20)

    # 「はい」ボタンの設定
    yes_button = tk.Button(button_frame, text="はい", command=lambda: on_yes(alarm_time),
                        font=("Helvetica", 18), bg="#4CAF50", fg="white", height=2, width=10)
    yes_button.pack(side=tk.LEFT, padx=10)

    # 「いいえ」ボタンの設定
    no_button = tk.Button(button_frame, text="いいえ", command=on_no,
                        font=("Helvetica", 18), bg="#f44336", fg="white", height=2, width=10)
    no_button.pack(side=tk.RIGHT, padx=10)

    # ウィンドウのサイズを設定
    root.geometry("800x400")
    root.resizable(False, False)

    root.mainloop()