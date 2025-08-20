# yolov8n pretrained, with only persons class

from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def predict(self, source):
        # Force only person detections
        return self.model.predict(source, classes=[0])
