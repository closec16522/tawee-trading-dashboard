import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:19000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if data.get("type") == "MT5_UPDATE":
                    print("Received MT5_UPDATE")
                    if "journal_entries" in data:
                        print("journal_entries:", data["journal_entries"])
                    else:
                        print("journal_entries NOT FOUND in payload")
                    break
    except Exception as e:
        print("Error:", e)

asyncio.run(test_ws())
