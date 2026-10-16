import os
import sqlite3
from datetime import datetime, timedelta

# Определяем путь к файлу базы данных относительно корня проекта
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "weather.db")


def init_db():
    """Инициализирует базу данных: создает папку data и таблицу погоды."""
    # Создаем папку data, если её нет
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    # Подключаемся к базе (если файла нет, SQLite создаст его сам)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создаем таблицу для хранения метеоданных
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT UNIQUE,
            temperature REAL,
            humidity INTEGER,
            pressure REAL,
            wind_speed REAL,
            created_at TEXT
        )
    """
    )

    conn.commit()
    conn.close()
    print("[Хранилище] База данных успешно инициализирована.")


def save_weather_data(data: dict) -> bool:
    """Принимает словарь от коллектора и сохраняет его в БД.

    Игнорирует дубликаты по полю timestamp.
    """
    if not data:
        return False

    init_db()  # На всякий случай проверяем, что таблица существует

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Используем INSERT OR IGNORE, чтобы не плодить дубли за один и тот же час
        cursor.execute(
            """
            INSERT OR IGNORE INTO weather_history 
            (timestamp, temperature, humidity, pressure, wind_speed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data["timestamp"],
                data["temperature"],
                data["humidity"],
                data["pressure"],
                data["wind_speed"],
                datetime.now().isoformat(),
            ),
        )

        conn.commit()

        if cursor.rowcount > 0:
            print(f"[Хранилище] Данные за {data['timestamp']} успешно сохранены.")
        else:
            print(
                f"[Хранилище] Запись за {data['timestamp']} уже существует. Пропущено."
            )

        return True
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при записи в БД: {error}")
        return False
    finally:
        conn.close()


def clean_old_data(days_to_keep: int = 30):
    """Блок чистки: удаляет данные старше указанного количества дней."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Вычисляем пограничную дату (все, что раньше неё — удаляем)
    cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

    try:
        # Open-Meteo возвращает время в формате ISO (YYYY-MM-DDTHH:MM),
        # поэтому мы можем безопасно сравнивать их как строки
        cursor.execute(
            "DELETE FROM weather_history WHERE timestamp < ?", (cutoff_date,)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(
                f"[Хранилище] Очистка: удалено {cursor.rowcount} устаревших записей."
            )
        else:
            print("[Хранилище] Очистка: устаревших данных не обнаружено.")
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при очистке БД: {error}")
    finally:
        conn.close()

def get_records_count() -> int:
    """Возвращает общее количество записей в таблице погоды."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # COUNT(*) заставляет SQLite мгновенно вернуть число строк в таблице
        cursor.execute("SELECT COUNT(*) FROM weather_history")
        # fetchone() забирает первую строчку результата, а [0] — само число
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при подсчете записей: {error}")
        return 0
    finally:
        conn.close()
