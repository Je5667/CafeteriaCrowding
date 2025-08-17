from ultralytics import YOLO
import cv2
import os
import shutil

class HeadCount:
    def __init__(self, model_path="path/to/your_model.pt"):
        self.model = YOLO(model_path)

    def count_people_in_folder(self, folder_path):
        """
        Count people in all images of a folder and move processed images
        """
        processed_folder = os.path.join(folder_path, "processed")
        os.makedirs(processed_folder, exist_ok=True)

        total_people = 0
        for img_name in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_name)
            if os.path.isdir(img_path):
                continue  # skip directories
            count = self.count_people(img_path)
            total_people += count

            # Move processed image
            shutil.move(img_path, os.path.join(processed_folder, img_name))

        return total_people

    def count_people(self, image_path):
        """
        Count number of people in a single image
        """
        img = cv2.imread(image_path)
        if img is None:
            return 0
        results = self.model(img)
        count = 0
        for result in results:
            classes = result.boxes.cls
            count += sum([1 for c in classes if int(c) == 0])  # class 0 = person
        return count
