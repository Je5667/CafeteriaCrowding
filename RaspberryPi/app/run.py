import os
import shutil
import time
from people_detection.headcount import HeadCount
from people_detection.chair import ChairDetector
from wait_prediction.predict import WaitTimePredictor
from core.data_formatter import format_chair_data, format_signal_count
from core.storage import send_to_server, save_locally

# --- Initialize classes ---
hc = HeadCount(model_path="CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt") # "path/to/your_model.pt"
cd = ChairDetector(model_path="CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt")
wtp = WaitTimePredictor(model_path="CafeteriaCrowding/RaspberryPi/models/final_vanilla.pth", device="cpu")

# --- Define folders ---
doorcam_folders = ["receive/data/doorcam/in",
                   "receive/data/doorcam/out",
                   "receive/data/doorcam/both"]

chaircam_folder = "receive/data/chaircam"

# --- Main loop ---
while True:
    total_people = 0
    total_sitting = 0

    # ---- Process DoorCam images for HeadCount ----
    for folder in doorcam_folders:
        processed_folder = os.path.join(folder, "processed")
        os.makedirs(processed_folder, exist_ok=True)

        for img_name in os.listdir(folder):
            img_path = os.path.join(folder, img_name)
            if os.path.isdir(img_path):
                continue  # skip folders

            # Run HeadCount
            raw_count = hc.count_people_in_image(img_path)
            signed_count = format_signal_count(folder, raw_count)
            total_people += signed_count
            print(f"[DoorCam] {img_name}: {signed_count} people, Total={total_people}")

            # Move image to processed
            shutil.move(img_path, os.path.join(processed_folder, img_name))

    # ---- Process ChairCam images for ChairDetector ----
    processed_chair_folder = os.path.join(chaircam_folder, "processed")
    os.makedirs(processed_chair_folder, exist_ok=True)

    for img_name in os.listdir(chaircam_folder):
        img_path = os.path.join(chaircam_folder, img_name)
        if os.path.isdir(img_path):
            continue  # skip folders

        # Run ChairDetector
        detected_chairs = cd.detect_chairs(img_path)
        total_sitting += len(detected_chairs)

        # Send chair occupancy to server
        data = {
            "camera": img_name[:8],  # e.g., 'chaircam00'
            "chairs": format_chair_data(detected_chairs)
        }
        send_to_server(data)

        # Move image to processed
        shutil.move(img_path, os.path.join(processed_chair_folder, img_name))

    print(f"Summary this loop: total_people={total_people}, total_sitting={total_sitting}")

    # ---- WaitTime prediction ----
    standing_people = total_people - total_sitting
    travel_times = [5, 10, 15]  # whatever you need

    # Predict queue wait only
    queue_waits, timestamp = wtp.predict(standing_people, travel_times=travel_times)

    for travel_time, queue_wait in queue_waits.items():
        total_wait = queue_wait + travel_time  # compute total wait externally

        print(f"[WaitTime] {travel_time} min travel → Queue wait: {queue_wait:.2f} min, Total wait: {total_wait:.2f} min at {timestamp}")

        # ---- Sending data to server ----
        data = {
            "travel_time": travel_time,
            "queue_wait": queue_wait,      # only the queue waiting time predicted by model
            "total_wait": total_wait,      # optional
            "timestamp": timestamp
        }
        save_locally(data)
        send_to_server(data)

    # --- Wait before next loop ---
    time.sleep(1)
