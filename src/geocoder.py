import requests
from requests.exceptions import RequestException


def search_city(city_name: str) -> list[dict] | None:
    """Ищет город по названию через Open-Meteo Geocoding API.

    Возвращает список найденных вариантов с координатами.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"

    # Очищаем строку от лишних пробелов
    city_name = city_name.strip()

    if not city_name:
        print("[Геокодер] Ошибка: Передано пустое имя города.")
        return None

    params = {
        "name": city_name,
        "count": 5,  # Берем топ-5 совпадений
        "language": "ru",  # Просим вернуть названия на русском, если возможно
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results")

        # Если сервер ничего не нашел по этому слову
        if not results:
            print(f"[Геокодер] Город '{city_name}' не найден.")
            return None

        cleaned_results = []
        for item in results:
            cleaned_results.append(
                {
                    "name": item.get("name"),
                    "country": item.get("country", "Неизвестно"),
                    "lat": round(item.get("latitude"), 4),
                    "lon": round(item.get("longitude"), 4),
                }
            )

        return cleaned_results

    except RequestException as net_error:
        print(f"[Геокодер] Сетевая ошибка при поиске города: {net_error}")
        return None
    except ValueError as json_error:
        print(f"[Геокодер] Ошибка обработки данных поиска: {json_error}")
        return None