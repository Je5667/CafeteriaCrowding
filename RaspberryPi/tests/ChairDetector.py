from app.people_detection.chair import ChairDetector
from app.core.data_formatter import format_chair_data

total_sitting = 0

for cam_signal in cameras:
    # ---- HeadCount ----
    raw_count = hc.count_people_in_folder(cam_signal)
    signed_count = format_signal_count(cam_signal, raw_count)
    total_people += signed_count

    # ---- ChairDetector ----
    folder = f"path/to/chair_folder_cam{cam_signal}"  # folder per camera
    cam_sitting = 0
    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)
        detected_chairs = cd.detect_chairs(img_path)
        cam_sitting += len(detected_chairs)
    total_sitting += cam_sitting
print(f"Time slot summary: total_people={total_people}, sitting={total_sitting}")