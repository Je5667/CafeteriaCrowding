# app/wait_prediction/predict.py

import json
import numpy as np
import datetime

class WaitTimePredictor:
    def __init__(self, model_path):
        # TODO: Load your LSTM model from file
        # Example (PyTorch):
        # self.model = torch.load(model_path)
        # self.model.eval()
        self.model = None  # placeholder

        self.recent_entries = []  # list of (timestamp, count)

    def _extract_features(self, sensor_data):
        """
        Compute hybrid features for LSTM:
        - people_entered
        - people_sitting
        - people_in_room
        - entry_rate
        - line_estimate
        """
        timestamp = sensor_data.get("timestamp") or datetime.datetime.now().isoformat()
        people_entered = sensor_data.get("people_entered", 0)
        people_sitting = sensor_data.get("people_sitting", 0)
        people_in_room = sensor_data.get("people_in_room", 0)

        # --- Line estimate ---
        line_estimate = max(people_in_room - people_sitting, 0)

        # --- Entry rate (last 1 min) ---
        now = datetime.datetime.fromisoformat(timestamp)
        self.recent_entries.append((now, people_entered))

        # Prune old entries beyond 1 minute
        one_minute_ago = now - datetime.timedelta(minutes=1)
        self.recent_entries = [entry for entry in self.recent_entries if entry[0] >= one_minute_ago]
        total_recent = sum(count for t, count in self.recent_entries)
        entry_rate = total_recent / 1.0  # per minute

        # --- Final feature vector ---
        return np.array([
            people_entered,
            people_sitting,
            people_in_room,
            line_estimate,
            entry_rate
        ]).reshape(1, 1, -1)  # shape: (batch, seq_len, features)

    def predict(self, sensor_data_json: str):
        try:
            sensor_data = json.loads(sensor_data_json)
            features = self._extract_features(sensor_data)

            # Dummy prediction (replace with model inference)
            # Example for PyTorch:
            # with torch.no_grad():
            #     output = self.model(torch.from_numpy(features).float())
            #     wait_time = output.item()

            wait_time = 5 + features[0, 0, 3] * 2  # mock: base + 2min per person in line
            return round(wait_time, 2)

        except Exception as e:
            print(f"[ERROR] wait prediction failed: {e}")
            return 0.0  # fallback
