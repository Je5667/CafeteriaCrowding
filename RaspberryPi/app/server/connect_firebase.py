import time
import re
import firebase_admin
from firebase_admin import credentials, db


class ConnectFirebase:
    def __init__(self):
        self.cred = credentials.Certificate("./firebase_key.json")
        firebase_admin.initialize_app(self.cred, {
            'databaseURL': "https://use-restaurant-default-rtdb.firebaseio.com/",
        })
        self.ref = db.reference()
        self._last_call_time = 0.0

    def _can_call(self) -> bool:
        now = time.time()
        if now - self._last_call_time < 1.0:
            return False
        self._last_call_time = now
        return True

    def read_seat(self):
        if not self._can_call():
            return False, None
        try:
            data = self.ref.child("restaurant_0").get()
            return True, data
        except Exception as e:
            print("Error in read_seat:", e)
            return False, None

    def write_seat(self, index: int, value: int):
        if not self._can_call():
            return False, None
        try:
            current_list = self.ref.child("restaurant_0").get()
            if not isinstance(current_list, list) or index >= len(current_list):
                return False, None
            self.ref.child(f"restaurant_0/{index}").set(value)
            return True, None
        except Exception as e:
            print("Error in write_seat:", e)
            return False, None

    def update_seat_data(self, camera_name: str, chair_data: dict[str, str]):
        if not self._can_call():
            return False, None

        update_data = dict()

        try:
            if camera_name == "chaircam00":
                for key, value in chair_data.items():
                    idx = ord(key.split("_")[1]) - ord('a')
                    if 0 <= idx <= 8:
                        if value == "occupied":
                            update_data[idx + 0] = 2
                        elif value == "empty":
                            update_data[idx + 0] = 0
                        else:
                            print("Error in update_seat_data:", value)
                            return False, None
                    else:
                        print("Error in update_seat_data:", key)
                        return False, None

            elif camera_name == "chaircam01":
                for key, value in chair_data.items():
                    idx = ord(key.split("_")[1]) - ord('a')
                    if 0 <= idx <= 11:
                        if value == "occupied":
                            update_data[idx + 9] = 2
                        elif value == "empty":
                            update_data[idx + 9] = 0
                        else:
                            print("Error in update_seat_data:", value)
                            return False, None
                    else:
                        print("Error in update_seat_data:", key)
                        return False, None

            elif camera_name == "chaircam03":
                for key, value in chair_data.items():
                    idx = ord(key.split("_")[1]) - ord('a')
                    if 0 <= idx <= 24:
                        if value == "occupied":
                            update_data[idx + 21] = 2
                        elif value == "empty":
                            update_data[idx + 21] = 0
                        else:
                            print("Error in update_seat_data:", value)
                            return False, None
                    else:
                        print("Error in update_seat_data:", key)
                        return False, None

            elif camera_name == "chaircam04":
                for key, value in chair_data.items():
                    idx = ord(key.split("_")[1]) - ord('a')
                    if 0 <= idx <= 9:
                        if value == "occupied":
                            update_data[idx + 46] = 2
                        elif value == "empty":
                            update_data[idx + 46] = 0
                        else:
                            print("Error in update_seat_data:", value)
                            return False, None
                    else:
                        print("Error in update_seat_data:", key)
                        return False, None
            else:
                return False, None

        except Exception as e:
            print("Error in update_seat_data:", e)
            return False, None

        try:
            data = self.ref.child("restaurant_0").get()
            if not isinstance(data, list):
                return False, None

            for key, value in update_data.items():
                if data[key] == 1 and value == 0:
                    pass
                elif data[key] == value:
                    pass
                else:
                    self.ref.child(f"restaurant_0/{key}").set(value)

        except Exception as e:
            print("Error in read_seat:", e)
            return False, None

        return True, None

    def clear_all_seats(self, value: int):
        if not self._can_call():
            return False, None

        try:
            current_list = self.ref.child("restaurant_0").get()

            if not isinstance(current_list, list):
                return False, None

            for i in range(len(current_list)):
                self.ref.child(f"restaurant_0/{i}").set(value)

            return True, None
        except Exception as e:
            print("Error in clear_all_seats:", e)
            return False, None

    def write_timer1(self, queue_wait: float, travel_time: float):
        if not self._can_call():
            return False, None
        try:
            self.ref.child("timer1").set({
                "queue_wait": round(queue_wait, 2),
                "travel_time": round(travel_time, 2)
            })
            return True, None
        except Exception as e:
            print("Error in write_timer1:", e)
            return False, None

    def write_timer2(self, queue_wait: float, travel_time: float):
        if not self._can_call():
            return False, None
        try:
            self.ref.child("timer2").set({
                "queue_wait": round(queue_wait, 2),
                "travel_time": round(travel_time, 2)
            })
            return True, None
        except Exception as e:
            print("Error in write_timer2:", e)
            return False, None

