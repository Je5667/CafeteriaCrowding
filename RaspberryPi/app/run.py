# run.py — Background worker that processes saved ESP32 images and sends structured results to backend

import os
import time
import json
from datetime import datetime
from PIL import Image
from app.detection.predictor import run_detection
from app.wait_prediction.predict import WaitTimePredictor
from app.core.data_formatter import format_chair_data, format_doorcam_data
from app.core.storage import send_to_server

# Initialize LSTM predictor
wait_predictor = WaitTimePredictor("models/lstm_model.pth")

# Global state for occupancy tracking
global_state = {
    "chairs": {},
    "people_count": 0
}

IMAGE_DIR = "data/received_images"
PROCESSED_DIR = "data/processed_images"
SENSOR_DATA_FILE = "data/latest_sensor_data.json"
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("[INFO] Worker started. Watching for new images...")

while True:
    for filename in os.listdir(IMAGE_DIR):
        if not filename.endswith(".jpg"):
            continue

        filepath = os.path.join(IMAGE_DIR, filename)
        camera_id, timestamp_str = filename.replace(".jpg", "").split("_", 1)
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

        try:
            image = Image.open(filepath).convert("RGB")
            detected_boxes = run_detection(image)

            output = {
                "camera_id": camera_id,
                "timestamp": timestamp.strftime("%Y%m%d_%H%M%S")
            }

            if camera_id.startswith("cam"):
                chair_status = format_chair_data(detected_boxes, camera_id)
                global_state["chairs"][camera_id] = chair_status
                output["chairs"] = chair_status

            elif camera_id.startswith("doorcam"):
                people_count = format_doorcam_data(detected_boxes)
                global_state["people_count"] = people_count
                output["people_count"] = people_count

            # Calculate people sitting
            people_sitting = sum(
                sum(1 for status in chairs.values() if status == "occupied")
                for chairs in global_state["chairs"].values()
            )

            # Load sensor data from Arduino (if available)
            sensor_people_entered = global_state["people_count"]  # fallback
            if os.path.exists(SENSOR_DATA_FILE):
                try:
                    with open(SENSOR_DATA_FILE, "r") as f:
                        sensor_data_latest = json.load(f)
                        sensor_people_entered = sensor_data_latest.get("people_entered", sensor_people_entered)
                except Exception as e:
                    print(f"[WARN] Failed to read sensor data: {e}")

            sensor_data = {
                "timestamp": datetime.now().isoformat(),
                "people_in_room": global_state["people_count"],
                "people_sitting": people_sitting,
                "people_entered": sensor_people_entered
            }

            wait_time = wait_predictor.predict(json.dumps(sensor_data))
            output["wait_time_minutes"] = wait_time

            send_to_server(output)
            print(f"[✔] Sent result from {camera_id}: {output}")

        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")

        # Move processed image to archive folder
        os.rename(filepath, os.path.join(PROCESSED_DIR, filename))

    time.sleep(1)
