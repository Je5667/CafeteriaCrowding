# app/core/data_formatter.py
# outputs chair detection into desired format

def format_chair_data(detected_chairs):
    chairs = ['chair_a', 'chair_b', 'chair_c']
    status = {chair: ('occupied' if chair in detected_chairs else 'empty') for chair in chairs}
    return status
