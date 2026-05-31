import websocket
import threading
import json
import time
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

WS_URL = "wss://{base_url}/ws/market/"

# =====================================================
# HEARTBEAT
# =====================================================

def heartbeat():

    while True:

        time.sleep(300)  # 5 minutes

        print(
            f"[HEARTBEAT] "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            f"Connection Alive"
        )

# =====================================================
# CALLBACKS
# =====================================================

def on_open(ws):

    print(
        f"[CONNECTED] "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    threading.Thread(
        target=heartbeat,
        daemon=True,
    ).start()


def on_message(ws, message):

    try:

        data = json.loads(message)

        print(
            f"[TICK] "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

        print(
            json.dumps(
                data,
                indent=2,
            )
        )

    except Exception:

        print(message)


def on_error(ws, error):

    print(
        f"[ERROR] "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(error)


def on_close(ws, close_status_code, close_msg):

    print(
        f"[DISCONNECTED] "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"Code={close_status_code} "
        f"Message={close_msg}"
    )

# =====================================================
# CONNECT LOOP
# =====================================================

def connect():

    while True:

        try:

            ws = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )

            ws.run_forever(
                ping_interval=30,
                ping_timeout=10,
            )

        except Exception as e:

            print(f"[RECONNECT ERROR] {e}")

        print("Reconnecting in 5 seconds...")
        time.sleep(5)

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    connect()