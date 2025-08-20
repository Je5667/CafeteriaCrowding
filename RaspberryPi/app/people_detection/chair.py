# cam_id 받아와서 사용

from ultralytics import YOLO
import cv2
import os
import string

class ChairDetector:
    def __init__(self, model_path="/home/electronic/myproject/CafeteriaCrowding/RaspberryPi/CafeteriaCrowding/RaspberryPi/models/yolov8n.pt"):
        """
        Initialize YOLOv8n model.
        """
        self.model = YOLO(model_path)
        self.save_folder = save_folder
        os.makedirs(self.save_folder, exist_ok=True)
        # Define chair coordinates per camera
        # Format: cam_id: [ (x1, y1, x2, y2) for each chair ]
        self.chair_coords = {
            "chaircam00": [(82, 84, 146, 127), (122, 176, 187, 220), (215, 276, 273, 323), (274, 106, 351, 151), (466, 314, 589, 388)]  # 2 chairs
           # "cam02": [(60, 110, 210, 310), (230, 110, 380, 310), (400,100,550,300)],  # 3 chairs
            # Add more cameras as needed
        }
        

    def detect_chairs(self, image_path):
        """
        Returns a list of detected chairs (e.g., ['chair_a', 'chair_b'])
        """
        img_name = os.path.basename(image_path)
        cam_id = img_name.split('_')[0]  # 'chaircam00'  # assumes first 5 chars are 'cam01', 'cam02', etc.

        if cam_id not in self.chair_coords:
            print(f"No chair coordinates defined for {cam_id}")
            return []

        coords = self.chair_coords[cam_id]
        img = cv2.imread(image_path)
        if img is None:
            print(f"Unable to read {image_path}")
            return []

        results = self.model(img)
        detected_chairs = []

        # Assign letters dynamically: 'a', 'b', 'c', ...
        for idx, (x1, y1, x2, y2) in enumerate(coords):
            chair_label = f"chair_{string.ascii_lowercase[idx]}"
            for result in results:
                boxes = result.boxes.xyxy
                classes = result.boxes.cls
                for i, cls in enumerate(classes):
                    if int(cls) != 0:  # class 0 = person
                        continue
                    bx1, by1, bx2, by2 = boxes[i]
                    # Check if person box overlaps chair area
                    if not (bx2 < x1 or bx1 > x2 or by2 < y1 or by1 > y2):
                        detected_chairs.append(chair_label)
                        break  # only one person per chair

        # --- Save the image with YOLO boxes ---
        for result in results:
            annotated_img = result.plot()  # draw boxes on image
            save_path = os.path.join(self.save_folder, img_name)
            cv2.imwrite(save_path, annotated_img)
            print(f"[↓] Saved annotated image to {save_path}")

        return detected_chairs
    

