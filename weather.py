import requests

def get_weather(city):
    try:
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city}&count=1&language=ru&format=json"
        )

        geo_resp = requests.get(geo_url, timeout=5).json()

        if not geo_resp.get("results"):
            return "❌ Город не найден"

        location_data = geo_resp["results"][0]

        lat = location_data["latitude"]
        lon = location_data["longitude"]
        location = location_data["name"]
        country = location_data.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}"
            f"&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )

        weather_resp = requests.get(weather_url, timeout=5).json()

        current = weather_resp.get("current")

        if not current:
            return "❌ Ошибка получения погоды"

        return (
            f"📍 {location}, {country}\n\n"
            f"🌡 Температура: {current['temperature_2m']}°C\n"
            f"💧 Влажность: {current['relative_humidity_2m']}%\n"
            f"💨 Ветер: {current['wind_speed_10m']} км/ч"
        )

    except Exception:
        return "❌ Ошибка подключения к API"