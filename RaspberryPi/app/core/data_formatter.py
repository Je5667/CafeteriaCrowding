# app/core/data_formatter.py
# outputs chair detection and door detection into desired format

def format_chair_data(detected_chairs):
    chairs = ['chair_a', 'chair_b', 'chair_c']
    status = {chair: ('occupied' if chair in detected_chairs else 'empty') for chair in chairs}
    return status

def format_signal_count(signal, num_people):
    """
    Convert the raw number of people into signed number based on signal
    """
    if signal == 0:
        return num_people
    elif signal == 1:
        return -num_people
    elif signal == 2:
        return 0
    else:
        return 0
