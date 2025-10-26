import asyncio
import json
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import queue
import os

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

# Thread-safe queue for outgoing messages
msg_queue = queue.Queue()

# Thread to read user input without blocking asyncio loop
def input_thread():
    while True:
        msg = input("Type message: ")
        msg_queue.put(msg)

# FastAPI server
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"✅ Peer connected: {websocket.client}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📩 Received from peer: {data}")
    except Exception as e:
        print(f"❌ Peer disconnected: {e}")
    finally:
        connected_clients.remove(websocket)

# Async client to connect to the peer
async def websocket_client():
    uri = f"ws://{CONFIG['peer_host']}:{CONFIG['peer_port']}/ws"
    while True:
        try:
            async with websockets.connect(uri, ping_interval=None) as websocket:
                print(f"✅ Connected to peer as client: {CONFIG['peer_host']}")

                # Task to receive messages
                async def receive_loop():
                    while True:
                        try:
                            msg = await websocket.recv()
                            print(f"📩 Received from peer: {msg}")
                        except Exception as e:
                            print(f"❌ Receive error: {e}")
                            break

                # Task to send messages from queue
                async def send_loop():
                    while True:
                        try:
                            msg = msg_queue.get_nowait()
                            await websocket.send(msg)
                        except queue.Empty:
                            await asyncio.sleep(0.1)
                        except Exception as e:
                            print(f"❌ Send error: {e}")
                            break

                # Run both tasks concurrently
                await asyncio.gather(receive_loop(), send_loop())

        except Exception as e:
            print(f"❌ Connection failed, retrying in 5s: {e}")
            await asyncio.sleep(5)

def start_client():
    asyncio.run(websocket_client())

if __name__ == "__main__":
    # Start input thread
    threading.Thread(target=input_thread, daemon=True).start()

    # Start WebSocket client in separate thread
    threading.Thread(target=start_client, daemon=True).start()

    # Start FastAPI server in main thread
    uvicorn.run("app.main:app", host=CONFIG['self_host'], port=CONFIG['self_port'], reload=False)
