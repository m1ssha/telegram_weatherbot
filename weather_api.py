from dotenv import load_dotenv

import os
import requests

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API")

def get_weather(city):
    """ Получает погоду в указанном городе с OpenWeatherMap """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        weather = {
            "city": data["name"],
            "city_id": data["id"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "windspeed": f"{data['wind']['speed']} м/с"
        }
        return weather
    else:
        return False
    

def get_weather_forecast(city, hours=6, days=0):
    from datetime import datetime
    """Получает прогноз погоды на указанное число часов или дней"""
    
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Температура в градусах Цельсия
        "lang": "ru"        # Описание погоды на русском
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        forecasts = data["list"]
        city_id = data['city']['id']
        
        steps = (days * 24 + hours) // 3

        weather_forecast = []


        for i in range(min(steps, len(forecasts))):
            forecast = forecasts[i]
            dt = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d %H:%M")
            weather_info = {
                "дата и время": dt,
                "температура": forecast["main"]["temp"],
                "ощущается как": forecast["main"]["feels_like"],
                "влажность": forecast["main"]["humidity"],
                "давление": forecast["main"]["pressure"],
                "ветер": f"{forecast['wind']['speed']} м/с",
                "погода": forecast["weather"][0]["description"]
            }
            weather_forecast.append(weather_info)

        return weather_forecast, city_id
    else:
        return False
    

def get_city_info(city):
    from datetime import datetime, UTC
    from pytz import timezone
    """Получает информацию о городе: население, код региона, время восхода/заката и т.д."""
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()

        timezone_offset = data["city"]["timezone"]

        local_sunrise = datetime.fromtimestamp(data["city"]["sunrise"], UTC) \
            .replace(tzinfo=timezone("UTC")) \
            .astimezone(timezone(f"Etc/GMT{int(-timezone_offset / 3600)}")) \
            .strftime('%H:%M:%S')

        local_sunset = datetime.fromtimestamp(data["city"]["sunset"], UTC) \
            .replace(tzinfo=timezone("UTC")) \
            .astimezone(timezone(f"Etc/GMT{int(-timezone_offset / 3600)}")) \
            .strftime('%H:%M:%S')

        city_info = {
            "city": data['city']["name"],
            "country": data["city"]["country"],
            "population": data["city"]["population"],
            "sunrise": local_sunrise,
            "sunset": local_sunset,
            "id": data["city"]["id"]
}

        return city_info
    else:
        return False