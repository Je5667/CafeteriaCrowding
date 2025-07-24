# app/detection/predictor.py

import torch
from PIL import Image

class ChairDetector:
    def __init__(self, model_path, device='cpu'):
        self.device = device
        self.model = torch.load(model_path, map_location=device)
        self.model.eval()

    def predict(self, image: Image.Image):
        # Preprocess image -> tensor
        # Run inference on model
        # Postprocess boxes, classes
        # Return list of detected chairs and their occupancy status
        # For simplicity, return list of chairs detected as occupied
        detected_chairs = ['chair_a', 'chair_b']  # Dummy example
        return detected_chairs
