# app/core/storage.py
# sends data to server via POST
# saves data locally to JSOn

import requests
import json
import os
from datetime import datetime
from server.connect_firebase import ConnectFirebase
from core.data_formatter import format_chair_data

# Save to local JSON file (fallback for testing/simulation)
def save_locally(data: dict, folder="predict_time"):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"data_{timestamp}.json")

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"[↓] Saved locally to {filename}")

# Firebase uploads

def update_firebase_chairs(detected_chairs, cam_id, cd):
    """
    Update chair occupancy in Firebase for a single camera frame.
    """
    fdb = ConnectFirebase()
    chairs_data = format_chair_data(detected_chairs, cam_id, cd.chair_coords)

    for idx, value in enumerate(chairs_data):
        success, _ = fdb.write_seat(idx, value)
        print(f"Seat {idx}: {'Updated' if success else 'Failed'}")

def update_firebase_wait_times(queue_waits):
    """
    Send predicted queue wait times to Firebase.
    queue_waits: dict of {travel_time: queue_wait}
    """
    fdb = ConnectFirebase()

    for travel_time, queue_wait in queue_waits.items():
        total_wait = queue_wait + travel_time

        print(f"[WaitTime] {travel_time} min travel → Queue wait: {queue_wait:.2f} min, "
              f"Total wait: {total_wait:.2f} min")

        # Write to Firebase (example: timer1)
        success, _ = fdb.write_timer1(queue_wait, travel_time)
        print("Timer1 update:", "Success" if success else "Failed")
