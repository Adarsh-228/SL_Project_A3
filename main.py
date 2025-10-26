"""
Main application combining all components
"""
import asyncio
import cv2
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
import logging
from datetime import datetime

# Import our modules
from config import config
from gesture_recognition import GestureRecognizer
from clipboard_sync import ClipboardSync
from network_discovery import NetworkDiscovery
from websocket_manager import WebSocketManager, WebSocketClient
from gesture_actions import gesture_actions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GestureSyncApp:
    def __init__(self):
        # Initialize FastAPI app
        self.app = FastAPI(title="Gesture Sync", version="1.0.0")
        
        # Setup templates
        self.templates = Jinja2Templates(directory="templates")
        
        # Initialize components
        self.gesture_recognizer = GestureRecognizer()
        self.clipboard_sync = ClipboardSync()
        self.network_discovery = NetworkDiscovery(config.get('server.websocket_port', 8001))
        
        # WebSocket components
        self.ws_manager = WebSocketManager(
            host=config.get('server.host', '0.0.0.0'),
            port=config.get('server.websocket_port', 8001)
        )
        self.ws_client = None
        
        # Application state
        self.video_capture = None
        self.running = False
        self.connected_peers = []
        
        # Setup routes and WebSocket handlers
        self.setup_routes()
        self.setup_websocket_handlers()
        self.setup_gesture_callbacks()
        self.setup_clipboard_callbacks()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def read_root(request: Request):
            return self.templates.TemplateResponse("index.html", {
                "request": request,
                "config": config.config,
                "local_ip": self.network_discovery.get_local_ip()
            })
        
        @self.app.get("/video_feed")
        async def video_feed():
            return StreamingResponse(
                self.generate_video_frames(),
                media_type="multipart/x-mixed-replace; boundary=frame"
            )
        
        @self.app.get("/api/peers")
        async def get_peers():
            return {"peers": self.network_discovery.get_peers()}
        
        @self.app.get("/api/status")
        async def get_status():
            return {
                "running": self.running,
                "connected_peers": len(self.connected_peers),
                "ws_server_running": self.ws_manager.is_running(),
                "ws_client_connected": self.ws_client.is_connected() if self.ws_client else False,
                "local_ip": self.network_discovery.get_local_ip()
            }
        
        @self.app.post("/api/connect")
        async def connect_to_peer(request: Request):
            data = await request.json()
            peer_host = data.get("host")
            peer_port = data.get("port", 8001)
            
            if peer_host:
                await self.connect_to_peer(peer_host, peer_port)
                return {"status": "success", "message": f"Connecting to {peer_host}:{peer_port}"}
            else:
                return {"status": "error", "message": "Host is required"}
    
    def setup_websocket_handlers(self):
        """Setup WebSocket message handlers"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.now().isoformat()
                    }))
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
        
        # Setup WebSocket manager callbacks
        self.ws_manager.add_message_callback("clipboard_sync", self.handle_clipboard_sync)
        self.ws_manager.add_message_callback("gesture_command", self.handle_gesture_command)
    
    def setup_gesture_callbacks(self):
        """Setup gesture recognition callbacks"""
        self.gesture_recognizer.add_gesture_callback(self.handle_gesture)
    
    def setup_clipboard_callbacks(self):
        """Setup clipboard sync callbacks"""
        self.clipboard_sync.add_sync_callback(self.handle_clipboard_change)
    
    async def handle_gesture(self, gesture: str):
        """Handle detected gesture"""
        logger.info(f"Gesture detected: {gesture}")
        
        # Handle gesture locally
        gesture_actions.handle_gesture(gesture)
        
        # Handle network sync for copy/paste
        if gesture == "copy":
            # Get current clipboard content and sync to peers
            content = self.clipboard_sync.get_clipboard_content()
            if content:
                sync_data = self.clipboard_sync.sync_to_peer(content)
                await self.broadcast_to_peers(sync_data)
                logger.info(f"Copied content to peers: {content[:50]}...")
        
        elif gesture == "paste":
            # Trigger paste operation (content should already be in clipboard from peer sync)
            logger.info("Paste gesture detected - content should be in clipboard")
    
    async def handle_clipboard_change(self, content: str):
        """Handle clipboard content change"""
        logger.info(f"Clipboard changed: {content[:50]}...")
        # This is called when clipboard changes locally
        # We can optionally sync this to peers if needed
    
    async def handle_clipboard_sync(self, data: dict, websocket, client_id: str):
        """Handle clipboard sync from peer"""
        success = self.clipboard_sync.sync_from_peer(data)
        if success:
            logger.info(f"Clipboard synced from {client_id}")
    
    async def handle_gesture_command(self, data: dict, websocket, client_id: str):
        """Handle gesture command from peer"""
        gesture = data.get("gesture")
        logger.info(f"Received gesture command from {client_id}: {gesture}")
    
    async def connect_to_peer(self, peer_host: str, peer_port: int):
        """Connect to a peer"""
        if self.ws_client:
            await self.ws_client.disconnect()
        
        self.ws_client = WebSocketClient(peer_host, peer_port)
        
        # Setup client callbacks
        self.ws_client.add_message_callback("clipboard_sync", self.handle_peer_clipboard_sync)
        
        # Start connection in background
        asyncio.create_task(self.ws_client.connect())
    
    async def handle_peer_clipboard_sync(self, data: dict):
        """Handle clipboard sync from peer client"""
        success = self.clipboard_sync.sync_from_peer(data)
        if success:
            logger.info("Clipboard synced from peer")
    
    async def broadcast_to_peers(self, data: dict):
        """Broadcast data to all connected peers"""
        await self.ws_manager.broadcast_message(data)
        if self.ws_client and self.ws_client.is_connected():
            await self.ws_client.send_message(data)
    
    async def generate_video_frames(self):
        """Generate video frames with gesture recognition"""
        if not self.video_capture:
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                logger.error("Could not open video capture")
                return
        
        while self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                break
            
            # Process frame with gesture recognition
            processed_frame, gesture = self.gesture_recognizer.process_frame(frame)
            
            # Encode frame as JPEG
            (flag, encodedImage) = cv2.imencode(".jpg", processed_frame)
            if not flag:
                continue
            
            # Yield frame
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                   bytearray(encodedImage) + b'\r\n')
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    async def start(self):
        """Start the application"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting Gesture Sync application...")
        
        # Start network discovery
        self.network_discovery.start_discovery()
        
        # Start WebSocket server
        await self.ws_manager.start_server()
        
        logger.info("Gesture Sync application started")
    
    async def stop(self):
        """Stop the application"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping Gesture Sync application...")
        
        # Stop components
        if self.video_capture:
            self.video_capture.release()
        
        self.gesture_recognizer.cleanup()
        self.clipboard_sync.stop_monitoring()
        self.network_discovery.stop()
        gesture_actions.cleanup()
        
        # Stop WebSocket components
        await self.ws_manager.stop_server()
        if self.ws_client:
            await self.ws_client.disconnect()
        
        logger.info("Gesture Sync application stopped")

# Create app instance
app_instance = GestureSyncApp()

# Export FastAPI app for uvicorn
app = app_instance.app

async def main():
    """Main entry point"""
    await app_instance.start()
    
    # Start uvicorn server
    config_obj = uvicorn.Config(
        app,
        host=config.get('server.host', '0.0.0.0'),
        port=config.get('server.port', 8000),
        log_level="info"
    )
    server = uvicorn.Server(config_obj)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await app_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())
