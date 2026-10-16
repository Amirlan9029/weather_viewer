import sqlite3
from src.storage import DB_PATH


def fetch_recent_history(hours: int = 6) -> list[dict]:
    """Вытягивает из базы данных записи за последние N часов для анализа."""
    conn = sqlite3.connect(DB_PATH)
    # Позволяет получать строки из БД в виде удобных словарей, а не кортежей
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Сортируем по времени, чтобы самые свежие записи были в конце списка
        cursor.execute(
            """
            SELECT timestamp, temperature, humidity, pressure, wind_speed 
            FROM weather_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (hours,),
        )

        rows = cursor.fetchall()
        # Разворачиваем список, чтобы хронология шла от старых к новым
        return [dict(row) for row in reversed(rows)]
    except sqlite3.Error as error:
        print(f"[Процессор] Ошибка при чтении истории из БД: {error}")
        return []
    finally:
        conn.close()


def analyze_weather_trend() -> dict:
    """Анализирует динамику параметров за последние часы и строит прогноз."""
    history = fetch_recent_history(hours=6)

    # Дефолтный ответ на случай, если данных в базе слишком мало для анализа тренда
    result = {
        "status": "warning",
        "trend_message": "Недостаточно данных для анализа тренда (нужно хотя бы 2 замера).",
        "prediction": "Прогноз недоступен.",
    }

    if len(history) < 2:
        return result

    # Берем самый старый замер из доступных за 6 часов и самый свежий
    oldest = history[0]
    latest = history[-1]

    # Считаем разницу (дельту) ключевых показателей
    pressure_delta = latest["pressure"] - oldest["pressure"]
    humidity_delta = latest["humidity"] - oldest["humidity"]

    # Логика метеорологического прогноза по трендам
    if pressure_delta <= -1.5:
        prediction = "Ожидается ухудшение погоды, возможны осадки или усиление ветра."
        status = "danger"
    elif pressure_delta >= 1.5:
        prediction = "Погода улучшается, ожидается прояснение и сухая погода."
        status = "success"
    else:
        # Если давление стабильно, смотрим на влажность
        if humidity_delta > 10:
            prediction = "Влажность растет, возможна переменная облачность."
            status = "info"
        else:
            prediction = "Погода останется стабильной в ближайшие часы."
            status = "stable"

    return {
        "status": status,
        "delta_pressure": round(pressure_delta, 2),
        "delta_humidity": round(humidity_delta, 2),
        "prediction": prediction,
        "trend_message": f"Давление: {round(pressure_delta, 2)} гПа, Влажность: {round(humidity_delta, 2)}%",
    }
