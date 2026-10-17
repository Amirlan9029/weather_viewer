import sys
from src.geocoder import search_city
from src.collector import get_current_weather, fetch_historical_archive
from src.storage import (
    save_weather_data,
    clean_old_data,
    get_records_count,
    get_monitored_cities,
)
from src.processor import analyze_weather_trend
from src.display import render_dashboard


def choose_city() -> tuple[str, float, float]:
    """Реализует динамический выбор города на основе истории из базы данных."""
    # Получаем список городов, которые уже сохранялись в БД
    saved_cities = get_monitored_cities()

    # Если база данных чистая и истории еще нет
    if not saved_cities:
        print("\n=== Первичный запуск проекта ===")
        city_input = input(
            "Введите название вашего первого города для мониторинга (например, Astana или Almaty): "
        ).strip()
        return fetch_coordinates_via_geocoder(city_input)

    # Если в базе уже есть сохраненные города, строим динамическое меню
    print("\n=== Выбор города для мониторинга ===")
    print("Доступные города из истории:")

    for idx, city in enumerate(saved_cities, start=1):
        print(f"{idx}. {city}")

    print(f"{len(saved_cities) + 1}. [Добавить новый город...]")

    choice = input(f"Выберите вариант (1-{len(saved_cities) + 1}): ").strip()

    # Проверяем, выбрал ли пользователь город из истории
    if choice.isdigit():
        choice_idx = int(choice) - 1

        if 0 <= choice_idx < len(saved_cities):
            # Пользователь выбрал существующий город.
            # Отлично, но нам все равно нужны его Lat/Lon для текущего запроса погоды!
            # Передаем имя в геокодер, чтобы получить свежие координаты.
            selected_city_name = saved_cities[choice_idx]

            # Отрезаем название страны, если оно пристыковано в скобках, для чистого поиска
            clean_name = selected_city_name.split(" (")[0]
            return fetch_coordinates_via_geocoder(clean_name)

        elif choice_idx == len(saved_cities):
            # Пользователь выбрал пункт "Добавить новый город"
            city_input = input(
                "Введите название нового города (например, Karaganda): "
            ).strip()
            return fetch_coordinates_via_geocoder(city_input)

    print("[MAIN] Некорректный выбор, закрытие программы.")
    sys.exit(1)


def fetch_coordinates_via_geocoder(city_name: str) -> tuple[str, float, float]:
    """Вспомогательная функция для поиска координат через геокодер."""
    if not city_name:
        print("[MAIN] Ошибка: Введено пустое имя.")
        sys.exit(1)

    print(f"[MAIN] Ищу координаты для '{city_name}'...")
    found_cities = search_city(city_name)

    if not found_cities:
        print("[MAIN] Ошибка: Не удалось найти город через API. Выход.")
        sys.exit(1)

    # ИСПРАВЛЕНО: Берем первый СЛОВАРЬ из списка результатов [0]
    target = found_cities[0]
    full_name = f"{target['name']} ({target['country']})"
    return full_name, target["lat"], target["lon"]


def run_pipeline():
    """Запускает полный динамический цикл: сбор -> сохранение -> анализ -> чистка -> вывод."""
    # Шаг 0: Получаем город и его точные координаты
    city_name, lat, lon = choose_city()

    print(
        f"\n[MAIN] Запуск метеорологического конвейера для: {city_name} [{lat}, {lon}]..."
    )

    # Шаг 1: Проверяем наличие исторической базы данных по этому городу (Бутстрап)
    records_in_db = get_records_count(city_name)

    if records_in_db == 0:
        print(
            f"[MAIN] [Внимание] База данных для [{city_name}] пуста. Запуск первичного скачивания архива..."
        )
        archive_data = fetch_historical_archive(lat, lon, past_days=3)

        if archive_data:
            print(f"[MAIN] Запись архива в базу данных...")
            for point in archive_data:
                save_weather_data(point, city_name)
            print(f"[MAIN] Первичный бутстрап базы данных успешно завершен!")
        else:
            print(
                f"[MAIN] Предупреждение: Не удалось загрузить архив. График тренда может быть временно недоступен."
            )

    # Шаг 2: Сбор свежих данных за текущий час из сети
    weather_data = get_current_weather(lat, lon)
    if not weather_data:
        print("[MAIN] Ошибка: Не удалось получить свежие данные. Завершение.")
        sys.exit(1)

    # Шаг 3: Сохранение новой точки в БД SQLite под именем конкретного города
    save_weather_data(weather_data, city_name)

    # Шаг 4: Анализ трендов на основе изолированной истории этого города
    trend_analysis = analyze_weather_trend(city_name)

    # Шаг 5: Автоматическая чистка старых данных (старше 30 дней)
    clean_old_data(days_to_keep=30)

    # Шаг 6: Запрашиваем актуальное количество строк по этому городу для дашборда
    total_records = get_records_count(city_name)

    # Шаг 7: Отрисовка дашборда
    render_dashboard(city_name, weather_data, trend_analysis, total_records)



if __name__ == "__main__":
    run_pipeline()
