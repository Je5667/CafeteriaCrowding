import requests
from datetime import datetime
import urllib.parse

KMA_KEY = "j-cKV8pCQUinClfKQpFIxQ"
NX, NY = 60, 126  # 청파동 grid

def get_weather_kma():
    try:
        # Dynamic base_date and base_time
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        minute = (now.minute // 10) * 10  # round down to nearest 10 minutes
        base_time = now.strftime("%H") + f"{minute:02d}"

        # Encode the key
        encoded_key = urllib.parse.quote_plus(KMA_KEY)

        # Base URL
        url = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"

        # All query parameters including the key
        params = {
            "authKey": encoded_key,  # API Hub expects authKey
            "numOfRows": 100,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": NX,
            "ny": NY
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        items = data["response"]["body"]["items"]["item"]

        # Extract relevant values
        temp = next(float(i["obsrValue"]) for i in items if i["category"] == "T1H")
        humidity = next(float(i["obsrValue"]) for i in items if i["category"] == "REH")
        rain = next(float(i["obsrValue"]) for i in items if i["category"] == "RN1")

        # Print extracted values
        print(f"[Weather] Temp: {temp}°C, Humidity: {humidity}%, Rain: {rain}mm")

        return {"temp": temp, "humidity": humidity, "rain": rain}

    except Exception as e:
        print(f"[✘] KMA fetch failed: {e}")
        return {"temp": 0, "humidity": 0, "rain": 0}

# Test
if __name__ == "__main__":
    weather = get_weather_kma()
