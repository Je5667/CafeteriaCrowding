from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
from datetime import datetime
import os
import json

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        # 1. Get camera ID (required)
        camera_id = request.form.get("camera_id")
        if not camera_id:
            return jsonify({"error": "Missing camera_id"}), 400

        # 2. Get image from ESP32
        image_file = request.files.get("image")
        if not image_file:
            return jsonify({"error": "No image file provided"}), 400
        image = Image.open(BytesIO(image_file.read()))

        # 3. Optional: Save image for logging/debug
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_id}_{timestamp}.jpg"
        save_path = os.path.join("data", "received_images", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)

        # 4. Get sensor data (optional)
        sensor_data_raw = request.form.get("sensor_data")
        sensor_data = json.loads(sensor_data_raw) if sensor_data_raw else None

        # 5. Process through your pipeline
        from app.detection.predictor import run_detection
        from app.wait_prediction.predict import predict_wait_time
        from app.core.data_formatter import format_outputs
        from app.core.storage import send_to_server

        is_sitting = run_detection(image)
        wait_time = predict_wait_time(sensor_data)
        output = format_outputs(is_sitting, wait_time)
        output["camera_id"] = camera_id
        output["timestamp"] = timestamp

        send_to_server(output)

        return jsonify({"status": "success", "result": output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
