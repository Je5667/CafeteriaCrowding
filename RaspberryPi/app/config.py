# app/config.py

import os

# --- General Settings ---
DEBUG = True
LOG_LEVEL = "INFO"

# --- Model Paths ---
RTDETR_MODEL_PATH = os.getenv("RTDETR_MODEL_PATH", "models/rtdetr_model.pth")
LSTM_MODEL_PATH   = os.getenv("LSTM_MODEL_PATH", "models/lstm_model.pth")

# --- Backend Server ---
# This is the server you send processed results to
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001/api/data")

# --- Detection Settings ---
DETECTION_THRESHOLD = 0.4  # confidence threshold for bounding boxes

# --- Port Configuration for Flask Receiver ---
RECEIVER_HOST = "0.0.0.0"
RECEIVER_PORT = 8000

# --- Chair Layouts Per Camera (bounding box regions) ---
# Format: [x1, y1, x2, y2] for each chair area

CHAIR_LAYOUTS = {
    "cam01": {
        "chair_A": [[30, 50, 130, 150]],
        "chair_B": [[140, 50, 240, 150]],
        "chair_C": [[250, 50, 350, 150]],
    },
    "cam02": {
        "chair_X": [[60, 80, 180, 180]],
        "chair_Y": [[200, 80, 320, 180]],
    }
}
