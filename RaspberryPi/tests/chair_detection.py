import sys
import os
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from people_detection.chair import ChairDetector

# --- Paths ---
image_path = "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/chaircam/chaircam00_250819_162811.png"
save_folder = "C:/Users/jenny/projects/SookmyungSymposium/test_files/receive/data/chaircam/processed"
os.makedirs(save_folder, exist_ok=True)
ChairDetector.save_folder = save_folder

# --- Initialize detector ---
detector = ChairDetector(model_path="C:/Users/jenny/projects/SookmyungSymposium/CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt")

# --- Read image and run YOLO ---
img = cv2.imread(image_path)
if img is None:
    print(f"Unable to read {image_path}")
    exit()

results = detector.model(img)

# --- Print YOLO detected people ---
print("YOLO detected people boxes:")
for result in results:
    boxes = result.boxes.xyxy
    classes = result.boxes.cls
    for i, cls in enumerate(classes):
        if int(cls) == 0:  # class 0 = person
            bx1, by1, bx2, by2 = boxes[i]
            print(f"Person {i}: ({bx1}, {by1}, {bx2}, {by2})")

# --- Run chair detection ---
detected_chairs = detector.detect_chairs(image_path)
print(f"Detected chairs in {os.path.basename(image_path)}: {detected_chairs}")
