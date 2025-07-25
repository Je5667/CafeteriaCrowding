# app/core/data_formatter.py
from app.config import CHAIR_LAYOUTS

def format_chair_data(detected_boxes, camera_id):
    layout = CHAIR_LAYOUTS.get(camera_id)
    if not layout:
        raise ValueError(f"No chair layout defined for {camera_id}")

    def iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        return interArea / (boxAArea + boxBArea - interArea + 1e-5)

    chair_status = {}
    for chair, zones in layout.items():
        occupied = any(iou(box, zone) > 0.3 for zone in zones for box in detected_boxes)
        chair_status[chair] = "occupied" if occupied else "empty"

    return chair_status


def format_doorcam_data(detected_boxes):
    # Every box is a person
    return len(detected_boxes)
