# Различные ошибки
error_city_weather = "🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/weather Москва</code>"
error_city_forecast = "🚫 Ошибка: проверьте формат ввода данных. Пример: <code>/forecast Москва 12</code>"
error_city_info = "🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/info Москва</code>"
error_find_city = "❌ Ошибка: город не найден. Проверьте правильность написания и попробуйте снова."
error_forecast_time = "⚠️ Ошибка: Время прогноза должно быть числом (часы или дни). Пример: <code>/forecast Москва 12</code>"
error_subscribe_format = "Некорректный формат! Используйте: <b>/subscribe Город HH:MM</b>"
error_subscribe_time = "Некорректное время! Используйте формат <b>HH:MM</b> (например, 08:30)."

# Уведомления
warning_city = "⚠️ Вы не указали город. Выберите город из списка или введите свой:"
warning_choose_city = "⚠️ Выберите город из списка или введите свой:"
warning_forecast_input = "⚠️ Укажите город. Пример: <code>/forecast Москва 12</code>"
warning_subscribe_input = "Введите город и время в формате <b>город HH:MM</b>. Пример: <code>/subscribe Москва 08:30</code>"
success_subscribe = "Вы подписаны на ежедневную погоду в городе <b>{city}</b> в <b>{time}</b>!"

# Информация
info_city_weather = "🔍 Введите название города в формате: <code>/weather Москва</code>"
info_city_forecast = "🔍 Введите название города в формате: <code>/forecast Москва 12</code>"
info_mysubscriptions = "<b>Ваши подписки:</b>\n\n"

# Help Menu:
help_menu_text = (f"📌 <b>Меню помощи</b>\n\n"
                  f"<b>Доступные команды:</b>\n"
                  f"<b>/weather [город]</b> - Получает текущую погоду в указанном городе.\n"
                  f"Допустимо использование команды <b>/weather</b> без добавления города. При условии, если ваш город имеется в списке\n\n"
                  f"<b>/forecast [город] [часы]</b> - Прогноз погоды на указанное время.\n"
                  f"Время указывается в часах. \n"
                  f"\n<b>/info [город]</b> - Выводит информацию о городе\n"
                  f"\n<b>Подписка на ежедневную рассылку погоды по времени:\n</b>"
                  f"\n<b>/subscribe [город] [время]</b> - подписаться на рассылку"
                  f"\n<b>/mysubscriptions</b> - узнать о своих подписках"
                  f"\n<b>/unsubscribe</b> - отписаться от рассылки"
                  f"\n\n💡 Бот использует данные OpenWeatherMap")

# Клавиатура:
back_to_city_choice = "⬅️ Вернуться к выбору городов"

# Сообщение с погодой на данный момент
def weather_message(weather, city_url_openweather):
    return (
        f"Информация о погоде <b>на данный момент</b> в городе <b>{weather['city']}</b>:\n\n"
        f"🌡 <b>Температура:</b> {weather['temp']}°C\n"
        f"🥶 <b>Ощущается как:</b> {weather['feels_like']}°C\n"
        f"💨 <b>Ветер:</b> {weather['windspeed']}\n"
        f"🌫 <b>Давление:</b> {weather['pressure']} мм рт. ст.\n"
        f"💧 <b>Влажность:</b> {weather['humidity']}%\n"
        f"🌦 <b>Погода:</b> {weather['description'].capitalize()}\n\n"
        f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>"
    )

# Сообщение с прогнозом погоды
def forecast_message(city, hours, forecast_data, city_url_openweather):
    text = (
        f"📅 Прогноз погоды в городе <b>{city}</b>:\n"
        f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>\n\n"
    )
    for entry in forecast_data:
        text += (
            f"<b>{entry['дата и время']}</b>\n"
            f"🌡 Температура: {entry['температура']}°C\n"
            f"🥶 Ощущается как: {entry['ощущается как']}°C\n"
            f"💧 Влажность: {entry['влажность']}%\n"
            f"🌫 Давление: {entry['давление']} мм рт. ст.\n"
            f"💨 Ветер: {entry['ветер']}\n"
            f"🌦 Погода: {entry['погода'].capitalize()}\n\n"
        )
    return text
