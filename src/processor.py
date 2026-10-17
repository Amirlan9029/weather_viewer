import sqlite3
from src.storage import DB_PATH


def fetch_recent_history(city_name: str, hours: int = 6) -> list[dict]:
    """Вытягивает из базы данных записи за последние N часов для конкретного города."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Добавляем фильтр WHERE city = ?
        cursor.execute(
            """
            SELECT timestamp, temperature, apparent_temp, humidity, pressure, wind_speed 
            FROM weather_history 
            WHERE city = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (city_name, hours),
        )

        rows = cursor.fetchall()
        return [dict(row) for row in reversed(rows)]
    except sqlite3.Error as error:
        print(f"[Процессор] Ошибка при чтении истории для [{city_name}] из БД: {error}")
        return []
    finally:
        conn.close()


def analyze_weather_trend(city_name: str) -> dict:
    """Анализирует динамику параметров конкретного города за последние часы и строит прогноз."""
    history = fetch_recent_history(city_name=city_name, hours=6)

    result = {
        "status": "warning",
        "trend_message": "Недостаточно данных для анализа тренда (нужно хотя бы 2 замера).",
        "prediction": "Прогноз недоступен.",
    }

    if len(history) < 2:
        return result

    oldest = history[0]
    latest = history[-1]

    # Считаем дельты
    pressure_delta = latest["pressure"] - oldest["pressure"]
    humidity_delta = latest["humidity"] - oldest["humidity"]
    temp_delta = latest["temperature"] - oldest["temperature"]

    # Логика метеорологического прогноза
    if pressure_delta <= -1.5:
        prediction = "Ожидается ухудшение погоды, возможны осадки или усиление ветра."
        status = "danger"
    elif pressure_delta >= 1.5:
        prediction = "Погода улучшается, ожидается прояснение и сухая погода."
        status = "success"
    else:
        if humidity_delta > 10:
            prediction = "Влажность растет, возможна переменная облачность."
            status = "info"
        else:
            prediction = "Погода останется стабильной в ближайшие часы."
            status = "stable"

    # Генерируем более подробное сообщение о трендах
    trend_msg = (
        f"Давление: {round(pressure_delta, 2)} гПа, "
        f"Влажность: {round(humidity_delta, 2)}%, "
        f"Темп: {round(temp_delta, 1)}°C"
    )

    return {
        "status": status,
        "delta_pressure": round(pressure_delta, 2),
        "delta_humidity": round(humidity_delta, 2),
        "delta_temperature": round(temp_delta, 1),
        "prediction": prediction,
        "trend_message": trend_msg,
    }