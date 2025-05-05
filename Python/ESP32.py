import asyncio
import websockets
import json

ws_url = "ws://192.168.218.173:8080"
min_send_interval = 0.1
last_send_time = 0

async def send_command(key):
    global last_send_time

    now = asyncio.get_event_loop().time()
    if now - last_send_time < min_send_interval:
        print("⏱ Gửi quá nhanh, bỏ qua")
        return False

    try:
        async with websockets.connect(ws_url) as websocket:
            message = json.dumps({"command": key})  # Gửi JSON đúng format
            await websocket.send(message)
            print(f"📤 Đã gửi WebSocket: {message}")
            last_send_time = now
            return True
    except Exception as e:
        print(f"❌ Lỗi kết nối WebSocket: {e}")
        return False
