from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    camera_id = request.form.get("camera_id")
    image_file = request.files.get("image")
    if not camera_id:
        return jsonify({"error": "Missing camera_id"}), 400
    if not image_file:
        return jsonify({"error": "No image provided"}), 400

    image_bytes = image_file.read()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 저장할 폴더 경로 지정
    if camera_id in ["in", "out", "both"]:
        folder = os.path.join("Doorcam", camera_id.capitalize())  # 예: Doorcam/In
    elif camera_id in ["seat01", "seat02"]:
        folder = "Seat"
    else:
        folder = "Others"  # 혹시 다른 id가 들어올 경우 대비

    # 전체 경로 생성 및 폴더 자동 생성
    save_path = os.path.join("data", folder)
    os.makedirs(save_path, exist_ok=True)

    filename = f"{camera_id}_{timestamp}.jpg"
    file_path = os.path.join(save_path, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return jsonify({"status": "saved", "filename": filename, "path": file_path}), 200


if __name__ == "__main__":
    # 최상위 폴더 기본 생성
    os.makedirs("data/Doorcam/In", exist_ok=True)
    os.makedirs("data/Doorcam/Out", exist_ok=True)
    os.makedirs("data/Doorcam/Both", exist_ok=True)
    os.makedirs("data/Seat", exist_ok=True)
    os.makedirs("data/Others", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
