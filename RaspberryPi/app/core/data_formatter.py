# app/core/data_formatter.py
# outputs chair detection and door detection into desired format

def format_chair_data(detected_chairs, coords):
    num_chairs = len(coords)
    all_chairs = [f"chair_{chr(ord('a') + i)}" for i in range(num_chairs)]
    return {chair: ('occupied' if chair in detected_chairs else 'empty') for chair in all_chairs}