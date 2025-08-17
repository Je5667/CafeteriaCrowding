# yolov8n pretrained, with only persons class

from ultralytics import YOLO

# Load pretrained YOLOv8n
model = YOLO("yolov8n.pt")

# Wrap the model to only detect 'person' (class 0)
class PersonOnlyYOLO(YOLO):
    def predict(self, *args, **kwargs):
        kwargs['classes'] = [0]  # force only persons
        return super().predict(*args, **kwargs)

# Save this wrapped model as a .pt file if needed, or just use in memory
person_model = PersonOnlyYOLO("yolov8n.pt")
person_model.save("person_yolov8n.pt")  # optional, if you want a .pt
