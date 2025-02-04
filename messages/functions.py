def get_weather_emoji(description):
    weather_emojis = {
        "ясно": "☀️",
        "переменная облачность": "⛅",
        "небольшая облачность": "⛅",
        "облачно с прояснениями": "⛅",
        "облачно": "☁️",
        "пасмурно": "🌥",
        "дождь": "🌧",
        "гроза": "⛈",
        "небольшой снег": "❄️",
        "снег": "❄️",
        "туман": "🌫",
        "морось": "🌦",
        "сильный дождь": "🌩",
        "метель": "🌨",
        "шторм": "🌪",
        "сильный ветер": "💨",
    }
    return weather_emojis.get(description.lower(), "🌍")


def get_feels_like_emoji(feels_like):
    if feels_like > 30:
        return "🔥"
    elif 15 <= feels_like <= 30:
        return "🌤"
    elif 0 <= feels_like < 15:
        return "❄️"
    else:
        return "🥶"