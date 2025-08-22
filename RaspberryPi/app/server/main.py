from connect_firebase import ConnectFirebase
import time

# 스크립트를 실행하려면 여백의 녹색 버튼을 누릅니다.
if __name__ == '__main__':
    fdb = ConnectFirebase()

    # 읽기
    success, seats = fdb.read_seat()
    print("read_seat:", success, seats)

    #초기화
    time.sleep(1.1)
    success, _ = fdb.clear_all_seats(0)
    print("clear_all_seats valie:", success)

    # 잘못된 index 쓰기 (실패)
    success, _ = fdb.write_seat(100, 99)
    print("write_seat invalid:", success)

    # 올바른 index 쓰기 (성공)
    time.sleep(1.1)
    success, _ = fdb.write_seat(0, 1)
    print("write_seat valid:", success)

    # timer1 쓰기 실패(지나치게 빠른 시도)
    success, _ = fdb.write_timer1(15.3456789, 9)
    print("write_timer1:", success)

    # timer1 쓰기
    time.sleep(1.1)
    success, _ = fdb.write_timer1(12.3456789, 98.7654321)
    print("write_timer1:", success)

    # 데이터 입력
    test1 = {
        "camera": "chaircam04",
        "chair": {
            "chair_a": "occupied",
            "chair_b": "occupied",
            "chair_c": "occupied",
            "chair_e": "empty",
            "chair_f": "empty",
            "chair_g": "empty",
        }
    }
    time.sleep(1.1)
    success, _ = fdb.update_seat_data(test1["camera"], test1["chair"])
    print("update_seat_data:", success)


# https://www.jetbrains.com/help/pycharm/에서 PyCharm 도움말 참조
