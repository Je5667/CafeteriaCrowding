import time
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

