import os
import shutil
import time
from people_detection.headcount import HeadCount
from people_detection.chair import ChairDetector
from wait_prediction.predict import WaitTimePredictor
from core.data_formatter import format_chair_data
from core.storage import save_locally
from server.connect_firebase import ConnectFirebase

# --- Initialize classes ---
hc = HeadCount(model_path="/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/models/yolov8n.pt") # "path/to/your_model.pt"
cd = ChairDetector(model_path="/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/models/yolov8n.pt")
wtp = WaitTimePredictor(model_path="/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/models/final_vanilla.pth", device="cpu")
fdb = ConnectFirebase()

# --- Define folders ---
doorcam_folders = ["/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/app/receive/data/doorcam/in",
                   "/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/app/receive/data/doorcam/out",
                   "/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/app/receive/data/doorcam/both"]

chaircam_folder = "/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/app/receive/data/chaircam"

# --- In-memory running total (resets on script restart) ---
running_total_people = 0

# --- Main loop ---
while True:
    total_people = 0
    total_sitting = 0
    
    # ---- Process DoorCam images for HeadCount ----
    for folder in doorcam_folders:
        processed_folder = os.path.join(folder, "processed")
        os.makedirs(processed_folder, exist_ok=True)

        # Collect file list before processing
        img_list = [f for f in os.listdir(folder) if not os.path.isdir(os.path.join(folder, f))]
        if not img_list:
            continue

        # Run HeadCount (may read/remove files)
        raw_count = hc.count_people_in_folder(folder)
        # Determine how to apply counts
        if folder.endswith("in"):
            delta = raw_count
        elif folder.endswith("out"):
            delta = -raw_count
        elif folder.endswith("both"):
            delta = 0
        else:
            delta = raw_count  # fallback

        total_people += delta
        print(f"RAW COUNT from DoorCam folder {folder}: {raw_count}")
        print(f"[DoorCam] {folder}: {delta:+} (raw={raw_count}) people, Total={total_people}")

        # Now move files only if they still exist
        for img_name in img_list:
            img_path = os.path.join(folder, img_name)
            if os.path.exists(img_path):  # ✅ prevent FileNotFoundError
                shutil.move(img_path, os.path.join(processed_folder, img_name))


    # ---- Accumulate running total (in-memory) ----
    running_total_people += total_people
    print(f"[RunningTotal] After applying loop delta {total_people:+}, running_total_people = {running_total_people}")

    # ---- Process ChairCam images for ChairDetector ----
    processed_chair_folder = os.path.join(chaircam_folder, "processed")
    os.makedirs(processed_chair_folder, exist_ok=True)

    for img_name in os.listdir(chaircam_folder):
        img_path = os.path.join(chaircam_folder, img_name)
        if os.path.isdir(img_path):
            continue  # skip folders

        # Run ChairDetector
        detected_chairs = cd.detect_chairs(img_path)
        print(f"Detected chairs in {img_name}: {detected_chairs}")
        total_sitting += len(detected_chairs)

        # Send chair occupancy to server

        # 2️⃣ Pull cam_id from image name
        cam_id = os.path.basename(img_path).split('_')[0]
        coords = cd.chair_coords.get(cam_id, [])
        if not coords:
            print(f"No coordinates defined for {cam_id}")

        chair_data = format_chair_data(detected_chairs, coords)
        fdb.update_seat_data(cam_id, chair_data)

        # Move image to processed
        shutil.move(img_path, os.path.join(processed_chair_folder, img_name))

    print(f"Summary this loop: total_people={total_people}, total_sitting={total_sitting}, running_total={running_total_people}")


    # ---- WaitTime prediction ----
    standing_people = running_total_people - total_sitting
    travel_times = [3.9245, 1.146]  # add more if needed

    # Predict queue wait only
    queue_waits, timestamp = wtp.predict(standing_people, travel_times=travel_times)

    # List of timer functions in the same order as travel_times
    timer_functions = [fdb.write_timer1, fdb.write_timer2]  # expand if you add more timers

    # Loop over predictions in order (travel_time → queue_wait)
    for i, travel_time in enumerate(travel_times):
        queue_wait = queue_waits[travel_time]
        total_wait = queue_wait + travel_time
        timer_name = f"timer{i+1}"

        # ---- Send to Firebase ----
        if i < len(timer_functions):
            timer_fn = timer_functions[i]
            ok, _ = timer_fn(queue_wait, travel_time)

            if ok:
                print(f"[Firebase] ✅ {timer_name} send success → queue_wait={queue_wait:.2f}, travel_time={travel_time:.2f}")
            else:
                print(f"[Firebase] ❌ {timer_name} send failed")

        time.sleep(1.1)  # respect Firebase rate limiter

        # ---- Print info ----
        print(f"[WaitTime] {travel_time:.2f} min travel → Queue wait: {queue_wait:.2f} min, "
              f"Total wait: {total_wait:.2f} min at {timestamp}")

        # ---- Save locally ----
        data = {
            "timer": timer_name,         
            "travel_time": travel_time,
            "queue_wait": queue_wait,    
            "total_wait": total_wait,    
            "timestamp": timestamp.isoformat()
        }
        save_locally(data)

    # --- Wait before next loop ---
    time.sleep(5)
