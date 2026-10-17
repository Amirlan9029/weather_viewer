def render_dashboard(
    city_name: str,
    current_weather: dict,
    trend_analysis: dict,
    records_count: int,
) -> None:
    """Форматирует данные и выводит красивый погодный дашборд в терминал."""
    if not current_weather:
        print("[Экран] Нет данных для отображения.")
        return

    status_icons = {
        "stable": "🌤️ ",
        "success": "☀️ ",
        "info": "☁️ ",
        "danger": "⛈️ ",
        "warning": "⚠️ ",
    }
    icon = status_icons.get(trend_analysis.get("status", "stable"), "🔹 ")

    # Шапка дашборда теперь динамически выводит имя выбранного города
    print("\n" + "=" * 54)
    print(f" 📊 МЕТЕОРОЛОГИЧЕСКИЙ ДАШБОРД: {city_name.upper()} ")
    print(f" (Записей в локальной базе данных: {records_count})")
    print("=" * 54)

    # Блок 1: Текущие замеры (добавили ощущаемую температуру)
    print(f"🕒 Время замера: {current_weather['timestamp'].replace('T', ' ')}")
    print(f"🌡️  Температура: {current_weather['temperature']} °C")

    # Выводим ощущаемую температуру, если она прилетела из API
    if "apparent_temp" in current_weather:
        print(f"🧥 Ощущается как: {current_weather['apparent_temp']} °C")

    print(f"💧 Влажность: {current_weather['humidity']}%")
    print(f"🧭 Давление: {current_weather['pressure']} гПа")
    print(f"💨 Скорость ветра: {current_weather['wind_speed']} м/с")
    print("-" * 54)

    # Блок 2: Анализ изменений и тренды
    print(f"📈 Анализ тренда:")
    print(f" {trend_analysis.get('trend_message', 'Нет данных')}")
    print("-" * 54)

    # Блок 3: Итоговый прогноз системы
    print(f"🔮 НАШ ПРОГНОЗ:")
    print(f" {icon}{trend_analysis.get('prediction', 'Недоступен')}")
    print("=" * 54 + "\n")
