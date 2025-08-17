import torch
from datetime import datetime
import weather_module

class WaitTimePredictor:
    def __init__(self, model_path="path/to/waittime_lstm.pt", device="cpu"):
        self.device = device
        self.model = torch.load(model_path, map_location=device)
        self.model.eval()

    def fetch_dynamic_features(self, standing_people):
        timestamp = datetime.now()
        weather = weather_module.get_weather_kma()
        day = timestamp.weekday()
        time_hour = timestamp.hour + timestamp.minute / 60
        return weather["temp"], weather["humidity"], weather["rain"], day, time_hour, timestamp

    def preprocess_input(self, standing_people, temp, humidity, rain, day, time_hour):
        features = [standing_people, temp, humidity, rain, day, time_hour]
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        return x

    def predict(self, standing_people):
        temp, humidity, rain, day, time_hour, timestamp = self.fetch_dynamic_features(standing_people)
        x = self.preprocess_input(standing_people, temp, humidity, rain, day, time_hour).to(self.device)
        with torch.no_grad():
            wait_time = self.model(x).item()
        return wait_time, timestamp
