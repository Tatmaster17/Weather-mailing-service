from operator import ge
from fastapi import HTTPException
import requests

# Переписать функцию, так как в params указывается только город, при этом зачем-то потом в if'е сравнивается 
# с городом и страной значения, хотя просто берется первое попавшееся

def get_city_name(city_name: str, country: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name, 
    }

    response = requests.get(url, params=params)
    data = response.json()
    city_match = None

    # Отсеивание результатов
    for item in data.get("results") or []:
        if item.get("name") == city_name and item.get("country") == country:
            city_match = item
            break

    # Проверка, найдено ли совпадение 
    if city_match is None:
        return "Not Found"

    return {
        "city": city_name,
        "country": country,
        "latitude": city_match["latitude"],
        "longitude": city_match["longitude"],
    }
