# server.py — Flask server to receive images from ESP32s via HTTP POST (Push-Based Architecture)

from flask import Flask, request, jsonify
from datetime import datetime
import os
from queue import Queue

# Flask setup
app = Flask(__name__)

# Task queue for saving image data
task_queue = Queue()

@app.route("/upload", methods=["POST"])
def upload():
    try:
        camera_id = request.form.get("camera_id")
        if not camera_id:
            return jsonify({"error": "Missing camera_id"}), 400

        image_file = request.files.get("image")
        if not image_file:
            return jsonify({"error": "No image provided"}), 400

        image_bytes = image_file.read()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save image to disk with naming convention
        filename = f"{camera_id}_{timestamp}.jpg"
        save_path = os.path.join("data", "received_images", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(image_bytes)

        return jsonify({"status": "saved", "filename": filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    os.makedirs("data/received_images", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
