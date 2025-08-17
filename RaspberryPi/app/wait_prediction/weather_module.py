import requests
from datetime import datetime

KMA_KEY = "j-cKV8pCQUinClfKQpFIxQ"
NX, NY = 60, 126  # 청파동 grid

def get_weather_kma():
    try:
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        base_time = now.strftime("%H%M")
        minute = (now.minute // 10) * 10
        base_time = now.strftime("%H") + f"{minute:02d}"

        url = (
            f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/"
            f"getUltraSrtNcst"
            f"?serviceKey={KMA_KEY}"
            f"&numOfRows=100&pageNo=1&dataType=JSON"
            f"&base_date={base_date}&base_time={base_time}"
            f"&nx={NX}&ny={NY}"
        )

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        items = response.json()["response"]["body"]["items"]["item"]

        temp = next(float(i["obsrValue"]) for i in items if i["category"] == "T1H")
        humidity = next(float(i["obsrValue"]) for i in items if i["category"] == "REH")
        rain = next(float(i["obsrValue"]) for i in items if i["category"] == "RN1")

        return {"temp": temp, "humidity": humidity, "rain": rain}

    except Exception as e:
        print(f"[✘] KMA fetch failed: {e}")
        return {"temp": 0, "humidity": 0, "rain": 0}
