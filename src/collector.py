import datetime
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def create_retry_session() -> requests.Session:
    """Создает сессию requests с автоматическим повтором запросов при ошибках сервера (например, 503)."""
    session = requests.Session()

    # Настраиваем правила повторов:
    # total=3 (максимум 3 попытки)
    # backoff_factor=1 (паузы между попытками: 1с, 2с, 4с)
    # status_forcelist=[502, 503, 504] (перезапрашивать только при этих ошибках сервера)
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        raise_on_status=False,  # Чтобы мы могли красиво обработать raise_for_status()
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def get_current_weather(lat: float, lon: float) -> dict | None:
    """Делает запрос к Open-Meteo API и возвращает словарь с текущей погодой."""
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,apparent_temperature",
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }

    try:
        session = create_retry_session()
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as net_error:
        print(
            f"[Коллектор] Не удалось получить текущую погоды после повторных попыток: {net_error}"
        )
        return None

    if not response.text.strip():
        print("[Коллектор] Ошибка: Сервер вернул абсолютно пустой ответ.")
        return None

    try:
        data = response.json()
        current_data = data.get("current")
        if not current_data:
            print("[Коллектор] Ошибка: В JSON-ответе отсутствует блок 'current'.")
            return None

        return {
            "timestamp": current_data.get("time"),
            "temperature": current_data.get("temperature_2m"),
            "apparent_temp": current_data.get("apparent_temperature"),
            "humidity": current_data.get("relative_humidity_2m"),
            "pressure": current_data.get("surface_pressure"),
            "wind_speed": current_data.get("wind_speed_10m"),
        }
    except ValueError as json_error:
        print(f"[Коллектор] Ошибка парсинга JSON текущей погоды: {json_error}")
        return None


def fetch_historical_archive(lat: float, lon: float, past_days: int = 3) -> list[dict]:
    """Скачивает архив погоды за динамически рассчитанный промежуток дат (start_date/end_date)."""
    today = datetime.date.today()
    start_dt = today - datetime.timedelta(days=past_days)

    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,apparent_temperature",
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }

    print(
        f"[Коллектор] Запрос архивных данных за промежуток: {start_date_str} -> {end_date_str}..."
    )

    try:
        session = create_retry_session()
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        hourly = data.get("hourly")
        if not hourly:
            print("[Коллектор] Архивные данные пустые или отсутствуют.")
            return []

        timestamps = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        apparent_temps = hourly.get("apparent_temperature", [])
        humidities = hourly.get("relative_humidity_2m", [])
        pressures = hourly.get("surface_pressure", [])
        winds = hourly.get("wind_speed_10m", [])

        history_list = []
        for t, temp, app_t, hum, press, w in zip(
            timestamps,
            temps,
            apparent_temps,
            humidities,
            pressures,
            winds,
        ):
            history_list.append(
                {
                    "timestamp": t,
                    "temperature": temp,
                    "apparent_temp": app_t,
                    "humidity": hum,
                    "pressure": press,
                    "wind_speed": w,
                }
            )

        print(f"[Коллектор] Успешно скачано {len(history_list)} архивных записей.")

        # Делаем микро-паузу перед возвратом данных, чтобы разгрузить сервер Open-Meteo
        # перед следующим немедленным запросом текущей погоды в main.py
        time.sleep(0.5)

        return history_list

    except (requests.RequestException, ValueError) as error:
        print(f"[Коллектор] Не удалось загрузить исторический архив: {error}")
        return []
