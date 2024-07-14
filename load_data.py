import googleapiclient.discovery
import google.auth
from datetime import datetime

def load_data():
    # ①Google APIの準備をする
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    calendar_id = 'tomoya49m@gmail.com'
    # Googleの認証情報をファイルから読み込む
    gapi_creds = google.auth.load_credentials_from_file('still-chassis-428405-d4-3fc25d1901a3.json', SCOPES)[0]
    # APIと対話するためのResourceオブジェクトを構築する
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)

    # ②次の日の日付を計算する
    now = datetime.utcnow()
    tomorrow = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
    
    # 次の日の開始時刻を設定する（午前0時）
    start_of_tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0).isoformat() + 'Z'
    end_of_tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59).isoformat() + 'Z'

    # ③Googleカレンダーから次の日のイベントを取得する
    event_list = service.events().list(
        calendarId=calendar_id, 
        timeMin=start_of_tomorrow,
        timeMax=end_of_tomorrow,
        maxResults=10, singleEvents=True,
        orderBy='startTime').execute()

    # ④最も早いイベントを選択する
    events = event_list.get('items', [])

    if not events:  # イベントが空の場合
        return None

    earliest_event = None
    earliest_start_time = None

    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        # 'Z' を取り除いて ISO フォーマットに変換する
        event_start = datetime.fromisoformat(start_time.replace('Z', ''))

        if earliest_start_time is None or event_start < earliest_start_time:
            earliest_event = event
            earliest_start_time = event_start

    if earliest_event:
        formatted_event = {
            'start_time': earliest_event['start'].get('dateTime', earliest_event['start'].get('date')),
            'end_time': earliest_event['end'].get('dateTime', earliest_event['end'].get('date')),
            'summary': earliest_event['summary'],
            'location': earliest_event.get('location'),
            'description': earliest_event.get('description'),
            'colorId': earliest_event.get('colorId')
        }
        return formatted_event
    else:
        return None
