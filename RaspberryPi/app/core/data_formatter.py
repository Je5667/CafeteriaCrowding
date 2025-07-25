from app.config import CHAIR_LAYOUTS

def format_chair_data(detected_boxes, camera_id):
    """
    detected_boxes: list of [x1, y1, x2, y2] for detected people
    camera_id: string like "cam01"
    """
    layout = CHAIR_LAYOUTS.get(camera_id)
    if not layout:
        raise ValueError(f"No chair layout defined for camera: {camera_id}")

    def iou(boxA, boxB):
        # Compute Intersection over Union of two boxes
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou

    chair_status = {}
    for chair, zones in layout.items():
        # Check if any person box overlaps the chair zone
        occupied = any(iou(box, zone) > 0.3 for zone in zones for box in detected_boxes)
        chair_status[chair] = "occupied" if occupied else "empty"

    return chair_status
