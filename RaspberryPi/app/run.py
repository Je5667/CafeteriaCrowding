# app/run.py
# stimulates everythign done on Pi

from PIL import Image
from app.detection.predictor import ChairDetector
from app.wait_prediction.predict import WaitTimePredictor
from app.core.data_formatter import format_chair_data

import time

def main():
    chair_detector = ChairDetector('models/rtdetr_model.pth')
    wait_predictor = WaitTimePredictor('models/lstm_model.pth')

    while True:
        # Simulate input data
        chair_image = Image.open('tests/test_image.jpg').convert('RGB')
        doorway_sensor_json = open('tests/fake_sensor.json').read()

        # Run chair detection
        detected_chairs = chair_detector.predict(chair_image)

        # Format chair occupancy data
        chair_status = format_chair_data(detected_chairs)

        # Run wait time prediction
        wait_time = wait_predictor.predict(doorway_sensor_json)

        # Print or send structured data
        output = {
            'chairs': chair_status,
            'wait_time_minutes': wait_time,
        }
        print(output)

        time.sleep(1)  # simulate interval

if __name__ == '__main__':
    main()
