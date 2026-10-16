import sys
from src.collector import get_current_weather
from src.storage import save_weather_data, clean_old_data, get_records_count
from src.processor import analyze_weather_trend
from src.display import render_dashboard


def run_pipeline():
    """Запускает полный цикл: сбор -> сохранение -> анализ -> чистка -> вывод."""
    print("\n[MAIN] Запуск метеорологического конвейера...")

    # 1. Сбор данных из сети
    weather_data = get_current_weather()
    if not weather_data:
        print("[MAIN] Ошибка: Не удалось получить свежие данные. Завершение.")
        sys.exit(1)

    # 2. Сохранение новой точки в БД SQLite
    save_weather_data(weather_data)

    # 3. Анализ трендов на основе истории из БД
    trend_analysis = analyze_weather_trend()

    # 4. Автоматическая чистка старых данных (старше 30 дней)
    clean_old_data(days_to_keep=30)
    
    # NEW: 4.5. Запрашиваем актуальное количество строк в базе данных
    total_records = get_records_count()

    # 5. Отрисовка красивого итогового дашборда (передаем счетчик)
    render_dashboard(weather_data, trend_analysis, total_records)
    
    
if __name__ == "__main__":
    run_pipeline()
