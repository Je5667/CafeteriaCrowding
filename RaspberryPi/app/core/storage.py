# app/core/storage.py
# sends data to server via POST

import requests
import json
import os
from datetime import datetime

# URL of the backend or database API (set in config.py)
try:
    from app.config import BACKEND_URL
except ImportError:
    BACKEND_URL = "http://localhost:5001/api/data"  # fallback for testing


# Send data to backend server (POST request)
def send_to_server(data: dict):
    try:
        response = requests.post(BACKEND_URL, json=data)
        response.raise_for_status()
        print(f"[✔] Sent to server: {data}")
    except Exception as e:
        print(f"[✘] Failed to send to server: {e}")
        save_locally(data)


# Save to local JSON file (fallback for testing/simulation)
def save_locally(data: dict, folder="saved_data"):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"data_{timestamp}.json")

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"[↓] Saved locally to {filename}")
