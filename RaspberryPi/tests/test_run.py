import sys
import os
import shutil
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

# --- Import real classes ---
from people_detection.headcount import HeadCount
from people_detection.chair import ChairDetector
from wait_prediction.predict import WaitTimePredictor
from core.data_formatter import format_chair_data, format_signal_count
# from core.storage import send_to_server, save_locally

# --- Mock server/storage functions ---
def send_to_server(data):
    print(f"[MOCK SEND] {data}")

def save_locally(data):
    print(f"[MOCK SAVE] {data}")

# --- Initialize ML models ---
hc = HeadCount(model_path="C:/Users/jenny/projects/SookmyungSymposium/CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt")
save_folder = "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/chaircam/boxed"
cd = ChairDetector(model_path="C:/Users/jenny/projects/SookmyungSymposium/CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt")
wtp = WaitTimePredictor(
    model_path="C:/Users/jenny/projects/SookmyungSymposium/CafeteriaCrowding/RaspberryPi/models/final_vanilla.pth",
    device="cpu",
    input_size=7  # <--- match your trained LSTM features
)

# --- Folders ---
doorcam_folders = [
    "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/doorcam/in",
    "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/doorcam/out",
    "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/doorcam/both"
]
chaircam_folder = "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/chaircam"

def run_once():
    total_people = 0
    total_sitting = 0

    # ---- DoorCam processing ----
    for folder in doorcam_folders:
        if not os.path.exists(folder):
            continue  # skip if folder doesn't exist

        processed_folder = os.path.join(folder, "processed")
        os.makedirs(processed_folder, exist_ok=True)

        # Count all people in this folder
        raw_count = hc.count_people_in_folder(folder)
        print(f"RAW COUNT from DoorCam folder {folder}: {raw_count}")
        total_people += raw_count

        print(f"[DoorCam] {folder}: {raw_count} people → Total={total_people}")

        # Move all images to processed
        for img_name in os.listdir(folder):
            img_path = os.path.join(folder, img_name)
            if os.path.isdir(img_path):
                continue
            shutil.move(img_path, os.path.join(processed_folder, img_name))

    # ---- ChairCam processing ----
    processed_chair_folder = os.path.join(chaircam_folder, "processed")
    os.makedirs(processed_chair_folder, exist_ok=True)

    for img_name in os.listdir(chaircam_folder):
        img_path = os.path.join(chaircam_folder, img_name)
        if os.path.isdir(img_path):
            continue

        detected_chairs = cd.detect_chairs(img_path)
        print(f"Detected chairs in {img_name}: {detected_chairs}")
        total_sitting += len(detected_chairs)


        camera_id = img_name.split("_")[0]  # e.g., chaircam00
        data = {
            "camera": camera_id,
            "chairs": format_chair_data(detected_chairs)
        }
        send_to_server(data)
        shutil.move(img_path, os.path.join(processed_chair_folder, img_name))

    print(f"Summary: total_people={total_people}, total_sitting={total_sitting}")

    # ---- WaitTime prediction ----
    standing_people = total_people - total_sitting
    travel_times = [5, 10, 15]  # adjust as needed

    # Predict queue wait only
    queue_waits, ts = wtp.predict(standing_people, travel_times)

    for travel_time, queue_wait in queue_waits.items():
        # Compute total wait outside
        total_wait = queue_wait + travel_time

        print(f"[WaitTime] {travel_time} min travel → Queue wait: {queue_wait:.2f} min, Total wait: {total_wait:.2f} min at {ts}")
        
        data = {
            "travel_time": travel_time,
            "queue_wait": queue_wait,      # keep label as queue wait
            "total_wait": total_wait,      # optional, for convenience
            "timestamp": ts.isoformat()
        }

        save_locally(data)
        send_to_server(data)


if __name__ == "__main__":
    run_once()
