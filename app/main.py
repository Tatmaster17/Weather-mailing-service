from pathlib import Path
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.get_city_name import get_city_name

app = FastAPI()

USERS_DATA: dict[str, "User"] = {}

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class User(BaseModel):
    id: str | None = None
    name: str = Field(..., max_length=32)
    city: str = Field(..., max_length=64)
    country: str = Field(..., max_length=64)
    channel: str | None = None
    email: str | None = None


@app.post("/api/users")
def add_user_name(user: User):
    if user.name in USERS_DATA:
        raise HTTPException(
            status_code=400,
            detail=f"User {user.name} is already created",
        )

    user.id = str(uuid.uuid4())
    USERS_DATA[user.name] = user

    return {"ok": True, "user": user}


@app.get("/weather")
def get_weather(city_name: str, country: str):
    location_params = get_city_name(city_name, country)

    if location_params == "Not Found":
        raise HTTPException(
            status_code=400,
            detail=f"This city in this country is not found"
        )

    city = location_params["city"]
    country = location_params["country"]
    lat = location_params["latitude"]
    lon = location_params["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "daily": ["sunrise", "sunset"],
        "timezone": "auto",
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        "city": city,
        "country": country,
        "Date": data["daily"]["sunrise"][0].split("T")[0],
        "Temperature": data["current"]["temperature_2m"],
        "Time_sunrise": data["daily"]["sunrise"][0].split("T")[1],
        "Time_sunset": data["daily"]["sunset"][0].split("T")[1],
    }


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
