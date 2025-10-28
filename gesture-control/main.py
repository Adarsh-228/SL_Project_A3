#!/usr/bin/env python3
"""
Simple Messaging Server
Run this on any system; connect from another system by entering the host IPv4.
"""
import asyncio
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI(title="Peer Messaging")

# Templates setup
templates = Jinja2Templates(directory="templates")

# Connected WebSocket clients
connected_clients: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def api_status():
    return {"online": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            message_text = await websocket.receive_text()
            # Prepare relay payload: who and what
            payload = json.dumps({
                "message": message_text
            })

            # Relay to all other clients
            stale: List[WebSocket] = []
            for client in connected_clients:
                if client is websocket:
                    continue
                try:
                    await client.send_text(payload)
                except Exception:
                    stale.append(client)
            # Cleanup stale clients
            for client in stale:
                if client in connected_clients:
                    connected_clients.remove(client)
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    print("Starting Peer Messaging Server...")
    print("Open: http://localhost:8000")
    print("WebSocket: ws://<host-ip>:8000/ws")
    uvicorn.run(app, host="0.0.0.0", port=8000)