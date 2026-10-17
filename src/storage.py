import os
import sqlite3
from datetime import datetime, timedelta

# Определяем путь к файлу базы данных относительно корня проекта
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "weather.db")


def init_db():
    """Инициализирует базу данных: создает папку data и таблицу погоды."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Модернизированная таблица с поддержкой колонки city и apparent_temp
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            timestamp TEXT,
            temperature REAL,
            apparent_temp REAL,
            humidity INTEGER,
            pressure REAL,
            wind_speed REAL,
            created_at TEXT,
            UNIQUE(timestamp, city) -- Защита от дубликатов в рамках одного города
        )
    """
    )

    conn.commit()
    conn.close()


def save_weather_data(data: dict, city_name: str) -> bool:
    """Принимает словарь от коллектора и сохраняет его в БД под именем конкретного города."""
    if not data:
        return False

    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Добавляем city_name в INSERT
        cursor.execute(
            """
            INSERT OR IGNORE INTO weather_history 
            (city, timestamp, temperature, apparent_temp, humidity, pressure, wind_speed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                city_name,
                data["timestamp"],
                data["temperature"],
                data.get("apparent_temp"),
                data["humidity"],
                data["pressure"],
                data["wind_speed"],
                datetime.now().isoformat(),
            ),
        )

        conn.commit()

        if cursor.rowcount > 0:
            print(
                f"[Хранилище] [{city_name}] Данные за {data['timestamp']} успешно сохранены."
            )
        else:
            print(
                f"[Хранилище] [{city_name}] Запись за {data['timestamp']} уже существует. Пропущено."
            )

        return True
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при записи в БД: {error}")
        return False
    finally:
        conn.close()


def get_records_count(city_name: str = None) -> int:
    """Возвращает количество записей в виде чистого числа (int)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        if city_name:
            cursor.execute(
                "SELECT COUNT(*) FROM weather_history WHERE city = ?",
                (city_name,),
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM weather_history")

        count = cursor.fetchone()
        # ИСПРАВЛЕНО: Достаем число из кортежа. Если данных нет, вернем 0
        return count[0] if count else 0
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при подсчете записей: {error}")
        return 0
    finally:
        conn.close()


def clean_old_data(days_to_keep: int = 30):
    """Блок чистки: удаляет данные старше указанного количества дней по всей базе."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

    try:
        cursor.execute(
            "DELETE FROM weather_history WHERE timestamp < ?", (cutoff_date,)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(
                f"[Хранилище] Очистка: удалено {cursor.rowcount} устаревших записей."
            )
    except sqlite3.Error as error:
        print(f"[Хранилище] Ошибка при очистке БД: {error}")
    finally:
        conn.close()

def get_monitored_cities() -> list[str]:
    """Возвращает список всех уникальных городов, которые уже есть в базе данных."""
    init_db()  # На случай, если файла БД еще нет
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Выбираем только уникальные имена городов
        cursor.execute("SELECT DISTINCT city FROM weather_history")
        # Извлекаем строки и превращаем список кортежей [('Астана',), ('Алматы',)] в плоский список строк
        cities = [row[0] for row in cursor.fetchall()]
        return cities
    except sqlite3.Error as error:
        print(
            f"[Хранилище] Ошибка при получении списка сохраненных городов: {error}"
        )
        return []
    finally:
        conn.close()
