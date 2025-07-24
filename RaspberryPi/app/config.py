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

# --- Chair Mapping (optional for visualization or logic) ---
CHAIR_NAMES = ["A", "B", "C"]
