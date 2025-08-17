import torch
import torchvision.transforms as T
import numpy as np
from PIL import Image, ImageDraw


# Preprocess image to tensor (for RT-DETR or YOLO)
def preprocess_image(image: Image.Image, size=(640, 640)):
    transform = T.Compose([
        T.Resize(size),
        T.ToTensor(),  # Converts to [0,1]
        T.Normalize(mean=[0.485, 0.456, 0.406],  # ImageNet normalization
                    std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0)  # Add batch dimension


# Postprocess model output (stub; customize based on your model's output format)
def postprocess_output(output, confidence_threshold=0.3):
    """
    Expected `output` is a list of detections per image.
    Each detection might be in format [x1, y1, x2, y2, score, class_id]
    """
    results = []

    for det in output:
        if det[4] >= confidence_threshold:
            results.append({
                "bbox": det[:4].tolist(),
                "score": float(det[4]),
                "class_id": int(det[5])
            })

    return results


# Draw bounding boxes (for visualization/testing)
def draw_boxes(image: Image.Image, boxes, labels=None):
    draw = ImageDraw.Draw(image)

    for i, box_info in enumerate(boxes):
        box = box_info["bbox"]
        class_id = box_info.get("class_id", None)
        score = box_info.get("score", None)

        draw.rectangle(box, outline="red", width=2)

        label = ""
        if labels and class_id is not None:
            label += labels[class_id]
        if score is not None:
            label += f" ({score:.2f})"

        if label:
            draw.text((box[0], box[1]), label, fill="red")

    return image


# Load class labels from file
def load_class_names(label_path):
    with open(label_path, 'r') as f:
        return [line.strip() for line in f.readlines()]
