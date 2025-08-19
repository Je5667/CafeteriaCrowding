import os
from app.people_detection.headcount import HeadCount  # adjust import if file name is different

# Folder with test images
folder_path = "test_images"  # put your images here

# Initialize head count detector
detector = HeadCount(model_path="CafeteriaCrowding/RaspberryPi/models/person_yolov8n.pt")

# Count people in the folder
total_people = detector.count_people_in_folder(folder_path)

print(f"Total people detected in folder '{folder_path}': {total_people}")
