"""
Phase 1: WebSocket Server
FastAPI WebSocket server for bi-directional communication
"""
import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Gesture Sync - Phase 1", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Store connected clients
connected_clients = set()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"🔌 Client disconnected. Total clients: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, exclude: WebSocket = None):
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"❌ Error broadcasting to client: {e}")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_status():
    """Main status page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gesture Sync - Phase 1</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background: #d4edda; color: #155724; }
            .disconnected { background: #f8d7da; color: #721c24; }
            .log { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; height: 300px; overflow-y: auto; font-family: monospace; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-danger { background: #dc3545; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Gesture Sync - Phase 1</h1>
            <h2>WebSocket Server Status</h2>
            
            <div id="status" class="status disconnected">
                Server Running - Waiting for connections
            </div>
            
            <div>
                <button class="btn-primary" onclick="sendTestMessage()">Send Test Message</button>
                <button class="btn-success" onclick="connectToPeer()">Connect to Peer</button>
                <button class="btn-danger" onclick="disconnect()">Disconnect</button>
            </div>
            
            <h3>Connection Log</h3>
            <div id="log" class="log"></div>
            
            <h3>Manual Test</h3>
            <input type="text" id="messageInput" placeholder="Enter test message" style="width: 300px; padding: 8px;">
            <button class="btn-primary" onclick="sendCustomMessage()">Send</button>
        </div>

        <script>
            let ws = null;
            let peerHost = null;

            function connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected to WebSocket server', 'connected');
                    addLog('✅ WebSocket connection established');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addLog(`📨 Received: ${data.type} - ${data.message || JSON.stringify(data)}`);
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected from WebSocket server', 'disconnected');
                    addLog('🔌 WebSocket connection closed');
                };
                
                ws.onerror = function(error) {
                    addLog(`❌ WebSocket error: ${error}`);
                };
            }

            function updateStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = `status ${type}`;
            }

            function addLog(message) {
                const logDiv = document.getElementById('log');
                const timestamp = new Date().toLocaleTimeString();
                logDiv.innerHTML += `[${timestamp}] ${message}<br>`;
                logDiv.scrollTop = logDiv.scrollHeight;
            }

            function sendTestMessage() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'test',
                        message: 'Test message from browser',
                        timestamp: new Date().toISOString()
                    };
                    ws.send(JSON.stringify(message));
                    addLog('📤 Sent test message');
                } else {
                    addLog('❌ WebSocket not connected');
                }
            }

            function sendCustomMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    const data = {
                        type: 'custom',
                        message: message,
                        timestamp: new Date().toISOString()
                    };
                    ws.send(JSON.stringify(data));
                    addLog(`📤 Sent: ${message}`);
                    input.value = '';
                } else if (!message) {
                    addLog('❌ Please enter a message');
                } else {
                    addLog('❌ WebSocket not connected');
                }
            }

            function connectToPeer() {
                peerHost = prompt('Enter peer IP address (e.g., 192.168.1.100):');
                if (peerHost) {
                    addLog(`🔌 Attempting to connect to peer: ${peerHost}`);
                    // This would connect to peer's WebSocket server
                    // For now, just log the attempt
                    addLog('ℹ️ Peer connection not implemented yet - Phase 1 focuses on server');
                }
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                    addLog('🔌 Manually disconnected');
                }
            }

            // Auto-connect on page load
            window.onload = function() {
                connect();
            };
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"📨 Received: {message}")
            
            # Echo message back to sender
            response = {
                "type": "echo",
                "message": f"Echo: {message.get('message', 'No message')}",
                "original": message,
                "timestamp": datetime.now().isoformat(),
                "server": "Phase 1 Server"
            }
            await manager.send_personal_message(json.dumps(response), websocket)
            
            # Broadcast to all other clients
            if len(manager.active_connections) > 1:
                broadcast_msg = {
                    "type": "broadcast",
                    "from": "server",
                    "message": message.get('message', 'Broadcast message'),
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast(json.dumps(broadcast_msg), exclude=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("🔌 Client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_server_status():
    """API endpoint to check server status"""
    return {
        "status": "running",
        "connected_clients": len(manager.active_connections),
        "phase": "Phase 1 - WebSocket Server",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🎯 Gesture Sync - Phase 1: WebSocket Server")
    print("=" * 50)
    print("Starting FastAPI WebSocket server...")
    print("Open browser to: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
