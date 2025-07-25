# sensor_server.py — Flask endpoint for receiving sensor data from Arduino

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

# Flask setup
app = Flask(__name__)

# Path to save sensor data for use by run.py
SENSOR_DATA_FILE = "data/latest_sensor_data.json"
os.makedirs("data", exist_ok=True)

@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    try:
        data = request.get_json()
        if not data or "people_entered" not in data:
            return jsonify({"error": "Missing 'people_entered' in JSON"}), 400

        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()

        # Save to file so run.py can read it
        with open(SENSOR_DATA_FILE, "w") as f:
            json.dump(data, f)

        return jsonify({"status": "received", "data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)