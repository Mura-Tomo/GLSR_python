import re
import datetime
import requests
from datetime import datetime, timedelta

def get_travel_time(api_key, user, event):
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        'origin': user.current_location,
        'destination': event.destination,
        'key': api_key,
        'mode': user.transportation_mode
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        route = data['routes'][0]
        leg = route['legs'][0]
        duration_seconds = leg['duration']['value']
        duration_minutes = int(duration_seconds // 60)
        return duration_minutes
    else:
        return f"Error fetching data: {data['status']}"

def calculate_wakeup_time(event, user, travel_time, buffer_time, weather_add_time):
    event_start_datetime = datetime.fromisoformat(event.start_time)
    earliest_event_time = datetime.fromisoformat(re.sub(r"T\d{2}:\d{2}", f"T{user.earliest_event_time}", event.start_time))

    if event_start_datetime < earliest_event_time:
        return None
    
    latest_wakeup_time = datetime.fromisoformat(re.sub(r"T\d{2}:\d{2}", f"T{user.latest_wakeup_time}", event.start_time))    
    total_time = user.preparation_time + travel_time + buffer_time + weather_add_time
    wakeup_time = event_start_datetime - timedelta(minutes=total_time)
    
    if wakeup_time > latest_wakeup_time:
        wakeup_time = latest_wakeup_time

    return wakeup_time