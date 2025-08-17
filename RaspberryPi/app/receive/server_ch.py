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
    
    # 카메라ID 첫글자로 폴더 분기
    cam_char = camera_id[0].lower() if camera_id else ""
    if cam_char == "i":
        folder = os.path.join("Doorcam", "In")
    elif cam_char == "o":
        folder = os.path.join("Doorcam", "Out")
    elif cam_char == "b":
        folder = os.path.join("Doorcam", "Both")
    elif cam_char == "s":
        folder = "Seat"
    else:
        folder = "Others"

    save_path = os.path.join("data", folder)
    os.makedirs(save_path, exist_ok=True)
    filename = f"{camera_id}_{timestamp}.jpg"
    file_path = os.path.join(save_path, filename)
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    return jsonify({"status": "saved", "filename": filename, "path": file_path}), 200

if __name__ == "__main__":
    # 폴더 기본 생성
    os.makedirs("data/Doorcam/In", exist_ok=True)
    os.makedirs("data/Doorcam/Out", exist_ok=True)
    os.makedirs("data/Doorcam/Both", exist_ok=True)
    os.makedirs("data/Seat", exist_ok=True)
    os.makedirs("data/Others", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
