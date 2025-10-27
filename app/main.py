"""
Phase 2: OpenCV Camera Feed
Test webcam capture and display video feed
"""
import cv2
import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import websockets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Gesture Sync - Phase 2", version="2.0.0")

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
        logger.info(f"SUCCESS: Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"DISCONNECTED: Client disconnected. Total clients: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, exclude: WebSocket = None):
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"ERROR: Error broadcasting to client: {e}")

manager = ConnectionManager()

# Global camera capture
camera = None

def get_camera():
    """Get camera instance"""
    global camera
    if camera is None:
        try:
            camera = cv2.VideoCapture(0)
            # Set camera properties for better performance
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize delay
            
            if not camera.isOpened():
                logger.error("ERROR: Could not open camera")
                return None
            
            # Test if we can actually read a frame
            ret, test_frame = camera.read()
            if not ret or test_frame is None:
                logger.error("ERROR: Camera opened but cannot read frames")
                camera.release()
                camera = None
                return None
            
            # Read a few more frames to warm up the camera
            for i in range(3):
                ret, _ = camera.read()
                if not ret:
                    logger.warning(f"WARNING: Frame {i+1} failed during warmup")
                
            logger.info("SUCCESS: Camera opened and tested successfully")
        except Exception as e:
            logger.error(f"ERROR: Camera initialization error: {e}")
            if camera:
                camera.release()
                camera = None
            return None
    return camera

def generate_frames():
    """Generate video frames for streaming"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("ERROR: Cannot open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    logger.info("SUCCESS: Camera opened for streaming")
    frame_count = 0
    
    while True:
        try:
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning("WARNING: Failed to read frame")
                continue
            
            frame_count += 1
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Add timestamp overlay
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"Phase 2 - Camera Feed", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, timestamp, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
        except Exception as e:
            logger.error(f"ERROR: Error in frame generation: {e}")
            continue
    
    cap.release()
    logger.info("Camera released")

@app.get("/", response_class=HTMLResponse)
async def get_status():
    """Main status page with camera feed"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gesture Sync - Phase 2</title>
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
            .phase-info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .camera-container { text-align: center; margin: 20px 0; }
            .camera-feed { border: 2px solid #007bff; border-radius: 10px; max-width: 640px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Gesture Sync - Phase 2</h1>
            
            <div class="phase-info">
                <h3>Phase 2: OpenCV Camera Feed</h3>
                <p><strong>Goal:</strong> Test webcam capture and display video feed</p>
                <p><strong>Status:</strong> Camera feed integration</p>
            </div>
            
            <div id="status" class="status disconnected">
                Server Running - Camera Feed Active
            </div>
            
            <div class="camera-container">
                <h3>📹 Live Camera Feed</h3>
                <img id="cameraFeed" class="camera-feed" src="/video_feed" alt="Camera Feed" onload="cameraLoaded()" onerror="cameraError()">
                <div>
                    <button class="btn-primary" onclick="toggleCamera()">Toggle Camera</button>
                    <button class="btn-success" onclick="testCamera()">Test Camera</button>
                    <button class="btn-success" onclick="restartCamera()">Restart Camera</button>
                </div>
                <div id="cameraStatus" style="margin-top: 10px; padding: 5px; border-radius: 3px; background: #f8f9fa;"></div>
            </div>
            
            <div>
                <button class="btn-primary" onclick="sendTestMessage()">Send Test Message</button>
                <button class="btn-success" onclick="connectToPeer()">Connect to Peer</button>
                <button class="btn-success" onclick="sendMessageToPeer()">Send to Peer</button>
                <button class="btn-danger" onclick="disconnect()">Disconnect</button>
            </div>
            
            <h3>Connection Log</h3>
            <div id="log" class="log"></div>
            
            <div class="phase-info">
                <h4>Phase 2 Success Criteria:</h4>
                <ul>
                    <li>✅ Camera opens and displays video feed</li>
                    <li>✅ Frame rate is smooth and consistent</li>
                    <li>✅ Video feed shows in browser</li>
                    <li>✅ WebSocket communication still works</li>
                </ul>
                <h4>Next: Phase 3 - MediaPipe Gesture Detection</h4>
            </div>
        </div>

        <script>
            let ws = null;
            let peerHost = null;
            let cameraActive = true;

            function connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected to WebSocket server', 'connected');
                    addLog('SUCCESS: WebSocket connection established');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addLog(`RECEIVED: ${data.type} - ${data.message || JSON.stringify(data)}`);
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected from WebSocket server', 'disconnected');
                    addLog('DISCONNECTED: WebSocket connection closed');
                };
                
                ws.onerror = function(error) {
                    addLog(`ERROR: WebSocket error: ${error}`);
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
                        message: 'Test message from Phase 2',
                        timestamp: new Date().toISOString()
                    };
                    ws.send(JSON.stringify(message));
                    addLog('SENT: Test message');
                } else {
                    addLog('ERROR: WebSocket not connected');
                }
            }

            function sendMessageToPeer() {
                if (window.peerConnection && window.peerConnection.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'peer_message',
                        message: 'Hello from System 1!',
                        from: 'System 1',
                        timestamp: new Date().toISOString()
                    };
                    window.peerConnection.send(JSON.stringify(message));
                    addLog('SENT: Message to peer');
                } else {
                    addLog('ERROR: Peer connection not established');
                    addLog('Click "Connect to Peer" first');
                }
            }

            function toggleCamera() {
                cameraActive = !cameraActive;
                const feed = document.getElementById('cameraFeed');
                if (cameraActive) {
                    feed.src = '/video_feed';
                    addLog('📹 Camera feed enabled');
                } else {
                    feed.src = '';
                    addLog('📹 Camera feed disabled');
                }
            }

            function testCamera() {
                const feed = document.getElementById('cameraFeed');
                feed.onload = function() {
                    addLog('SUCCESS: Camera feed loaded successfully');
                    updateCameraStatus('Camera working', 'success');
                };
                feed.onerror = function() {
                    addLog('ERROR: Camera feed failed to load');
                    updateCameraStatus('Camera failed', 'error');
                };
                addLog('Testing camera feed...');
            }

            function cameraLoaded() {
                addLog('SUCCESS: Camera feed loaded');
                updateCameraStatus('Camera active', 'success');
            }

            function cameraError() {
                addLog('ERROR: Camera feed error');
                updateCameraStatus('Camera error', 'error');
            }

            function updateCameraStatus(message, type) {
                const statusDiv = document.getElementById('cameraStatus');
                statusDiv.textContent = message;
                statusDiv.style.background = type === 'success' ? '#d4edda' : '#f8d7da';
                statusDiv.style.color = type === 'success' ? '#155724' : '#721c24';
            }

            function restartCamera() {
                const feed = document.getElementById('cameraFeed');
                addLog('Restarting camera...');
                updateCameraStatus('Restarting...', 'info');
                
                // Force reload the video feed
                const currentSrc = feed.src;
                feed.src = '';
                setTimeout(() => {
                    feed.src = currentSrc + '?t=' + new Date().getTime();
                }, 100);
            }

            function connectToPeer() {
                peerHost = prompt('Enter peer IP address (e.g., 172.19.247.215):');
                if (peerHost) {
                    addLog(`🔌 Attempting to connect to peer: ${peerHost}`);
                    
                    // Create new WebSocket connection to peer
                    const peerWsUrl = `ws://${peerHost}:8000/ws`;
                    addLog(`Connecting to: ${peerWsUrl}`);
                    
                    try {
                        const peerWs = new WebSocket(peerWsUrl);
                        
                        peerWs.onopen = function(event) {
                            addLog(`✅ Connected to peer ${peerHost}`);
                            addLog('You can now send messages to the peer');
                        };
                        
                        peerWs.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            addLog(`📨 Message from peer: ${data.message || JSON.stringify(data)}`);
                        };
                        
                        peerWs.onclose = function(event) {
                            addLog(`🔌 Connection to peer ${peerHost} closed`);
                        };
                        
                        peerWs.onerror = function(error) {
                            addLog(`❌ Error connecting to peer: ${error}`);
                            addLog('Make sure the peer server is running on port 8000');
                        };
                        
                        // Store peer connection for sending messages
                        window.peerConnection = peerWs;
                        
                    } catch (error) {
                        addLog(`❌ Failed to create peer connection: ${error}`);
                    }
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
                addLog('Phase 2: Camera feed integration');
                
                // Auto-start camera after a short delay
                setTimeout(() => {
                    addLog('Auto-starting camera...');
                    updateCameraStatus('Starting camera...', 'info');
                }, 1000);
            };
        </script>
    </body>
    </html>
    """

@app.get("/video_feed")
async def video_feed():
    """Video streaming route"""
    try:
        return StreamingResponse(
            generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"ERROR: Video feed error: {e}")
        return {"error": "Video feed unavailable", "details": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"RECEIVED: {message}")
            
            # Echo message back to sender
            response = {
                "type": "echo",
                "message": f"Echo: {message.get('message', 'No message')}",
                "original": message,
                "timestamp": datetime.now().isoformat(),
                "server": "Phase 2 Server"
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
        logger.info("DISCONNECTED: Client disconnected")
    except Exception as e:
        logger.error(f"ERROR: WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_server_status():
    """API endpoint to check server status"""
    camera_status = "active" if get_camera() is not None else "inactive"
    return {
        "status": "running",
        "connected_clients": len(manager.active_connections),
        "phase": "Phase 2 - Camera Feed",
        "camera_status": camera_status,
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global camera
    if camera is not None:
        camera.release()
        logger.info("Camera released on shutdown")

if __name__ == "__main__":
    import socket
    
    # Get local IP address
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    
    print("🎯 Gesture Sync - Phase 2: Camera Feed")
    print("=" * 50)
    print("Starting FastAPI server with camera integration...")
    print(f"Open browser to: http://localhost:8000")
    print(f"Or use local IP: http://{local_ip}:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("Camera feed: http://localhost:8000/video_feed")
    print("Command: python -m app.main")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)