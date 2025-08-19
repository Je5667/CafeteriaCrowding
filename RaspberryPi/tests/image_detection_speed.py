import torch
import time
from PIL import Image
from torchvision import transforms

# ---------------------------
# CONFIG
# ---------------------------
DEVICE = "cpu"  # or "cuda" if available
IMG_PATH = "test.jpg"
NUM_RUNS = 10

# ---------------------------
# LOAD IMAGE
# ---------------------------
img = Image.open(IMG_PATH).convert("RGB")
transform = transforms.Compose([
    transforms.Resize((640, 640)),
    transforms.ToTensor(),
])
img_tensor = transform(img).unsqueeze(0).to(DEVICE)

# ---------------------------
# LOAD MODELS
# ---------------------------
models = {}

# YOLOv8n (Ultralytics)
from ultralytics import YOLO
models["YOLOv8n"] = YOLO("yolov8n.pt").to(DEVICE)

# YOLOv9s (Ultralytics)
models["YOLOv9s"] = YOLO("yolov9s.pt").to(DEVICE)

# YOLOX small via Torch Hub
models["YOLOX_s"] = torch.hub.load("Megvii-BaseDetection/YOLOX", "yolox_s", pretrained=True).to(DEVICE)
models["YOLOX_s"].eval()

# RF-DETR via Torch Hub
models["RF-DETR"] = torch.hub.load("facebookresearch/detr", "detr_resnet50", pretrained=True).to(DEVICE)
models["RF-DETR"].eval()

# ---------------------------
# BENCHMARK FUNCTION
# ---------------------------
def benchmark(model, input_tensor, num_runs=10):
    with torch.no_grad():
        # Warm-up
        _ = model(input_tensor)
        # Timing
        start = time.time()
        for _ in range(num_runs):
            _ = model(input_tensor)
        end = time.time()
    avg_time = (end - start) / num_runs
    fps = 1 / avg_time
    return avg_time, fps

# ---------------------------
# RUN BENCHMARK
# ---------------------------
results = {}
for name, model in models.items():
    try:
        avg_time, fps = benchmark(model, img_tensor, NUM_RUNS)
        results[name] = (avg_time, fps)
    except Exception as e:
        results[name] = ("Error", "Error")
        print(f"Error running {name}: {e}")

# ---------------------------
# PRINT RESULTS
# ---------------------------
print(f"{'Model':<12} {'Avg Time (s)':<15} {'FPS':<10}")
print(f"{'-'*40}")
for name, (avg_time, fps) in results.items():
    print(f"{name:<12} {avg_time:<15} {fps:<10}")
