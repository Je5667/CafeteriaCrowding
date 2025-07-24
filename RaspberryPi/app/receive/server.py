from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
import json

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        # Get the image from ESP32-CAM
        image_file = request.files.get("image")
        if image_file:
            image = Image.open(BytesIO(image_file.read()))
        else:
            return jsonify({"error": "No image file provided"}), 400

        # Get sensor data from Arduino (as JSON in a form field)
        sensor_data_raw = request.form.get("sensor_data")
        if sensor_data_raw:
            sensor_data = json.loads(sensor_data_raw)
        else:
            sensor_data = None  # Optional

        # At this point, you have:
        # - `image`: PIL image
        # - `sensor_data`: dict from Arduino

        # You can now call your detection pipeline here
        from app.detection.predictor import run_detection
        from app.wait_prediction.predict import predict_wait_time
        from app.core.data_formatter import format_outputs
        from app.core.storage import send_to_server

        is_sitting = run_detection(image)
        wait_time = predict_wait_time(sensor_data)
        output = format_outputs(is_sitting, wait_time)
        send_to_server(output)

        return jsonify({"status": "success", "result": output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Only run if launched directly (not when imported)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)