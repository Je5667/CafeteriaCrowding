# app/wait_prediction/predict.py

import json

class WaitTimePredictor:
    def __init__(self, model_path):
        # Load your LSTM model here
        pass

    def predict(self, sensor_data_json: str):
        sensor_data = json.loads(sensor_data_json)
        # Process sensor data and run LSTM prediction
        # Return estimated wait time (e.g., in minutes)
        wait_time = 5  # Dummy example
        return wait_time
