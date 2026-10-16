import requests
from requests.exceptions import RequestException


def get_current_weather(lat: float = 51.17, lon: float = 71.43) -> dict | None:
    """Делает запрос к Open-Meteo API и возвращает словарь с текущей погодой."""
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m",
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }

    try:
        # Запрашиваем данные
        response = requests.get(url, params=params, timeout=10)

        # Если статус ответа не 200, это вызовет исключение и уйдет в блок сетевых ошибок
        response.raise_for_status()

    except RequestException as net_error:
        print(f"[Коллектор] Сетевая ошибка (проверьте подключение/URL): {net_error}")
        return None

    # Если дошли сюда, сеть отработала успешно. Проверяем содержимое ответа.
    if not response.text.strip():
        print("[Коллектор] Ошибка: Сервер вернул абсолютно пустой ответ.")
        return None

    try:
        data = response.json()

        current_data = data.get("current")
        if not current_data:
            print("[Коллектор] Ошибка: В JSON-ответе сервера отсутствует блок 'current'.")
            return None

        cleaned_data = {
            "timestamp": current_data.get("time"),
            "temperature": current_data.get("temperature_2m"),
            "humidity": current_data.get("relative_humidity_2m"),
            "pressure": current_data.get("surface_pressure"),
            "wind_speed": current_data.get("wind_speed_10m"),
        }

        print(f"[Коллектор] Данные успешно получены за {cleaned_data['timestamp']}")
        return cleaned_data

    except ValueError as json_error:
        print(f"[Коллектор] Ошибка парсинга JSON: {json_error}")
        print(f"[Коллектор] Первые 150 символов сырого ответа: {response.text[:150]}")
        return None