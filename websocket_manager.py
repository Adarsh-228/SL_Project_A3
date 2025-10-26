"""
WebSocket communication system for peer-to-peer data exchange
"""
import asyncio
import json
import websockets
import logging
from typing import Dict, Set, Optional, Callable
from datetime import datetime
import uuid

class WebSocketManager:
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.connected_peers: Set[websockets.WebSocketServerProtocol] = set()
        self.message_callbacks: Dict[str, Callable] = {}
        self.server = None
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_message_callback(self, message_type: str, callback: Callable):
        """Add callback for specific message types"""
        self.message_callbacks[message_type] = callback
    
    async def handle_client(self, websocket, path):
        """Handle incoming WebSocket connections"""
        client_id = str(uuid.uuid4())[:8]
        self.logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        # Add to connected peers
        self.connected_peers.add(websocket)
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "connection_established",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat(),
                "server_info": {
                    "host": self.host,
                    "port": self.port
                }
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Handle messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(data, websocket, client_id)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON from {client_id}: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Remove from connected peers
            self.connected_peers.discard(websocket)
    
    async def process_message(self, data: dict, websocket, client_id: str):
        """Process incoming message and trigger appropriate callbacks"""
        message_type = data.get("type", "unknown")
        
        # Log message
        self.logger.info(f"Received {message_type} from {client_id}")
        
        # Trigger callback if registered
        if message_type in self.message_callbacks:
            try:
                await self.message_callbacks[message_type](data, websocket, client_id)
            except Exception as e:
                self.logger.error(f"Error in callback for {message_type}: {e}")
        
        # Handle special message types
        if message_type == "ping":
            await self.send_message(websocket, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
    
    async def send_message(self, websocket, message: dict):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
    
    async def broadcast_message(self, message: dict, exclude: Optional[websockets.WebSocketServerProtocol] = None):
        """Broadcast message to all connected peers"""
        if not self.connected_peers:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for peer in self.connected_peers:
            if peer != exclude:
                try:
                    await peer.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(peer)
                except Exception as e:
                    self.logger.error(f"Error broadcasting to peer: {e}")
                    disconnected.add(peer)
        
        # Remove disconnected peers
        self.connected_peers -= disconnected
    
    async def start_server(self):
        """Start the WebSocket server"""
        if self.running:
            return
        
        self.running = True
        self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        if not self.running:
            return
        
        self.running = False
        
        # Close all connections
        for peer in self.connected_peers.copy():
            try:
                await peer.close()
            except Exception:
                pass
        
        self.connected_peers.clear()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self.logger.info("WebSocket server stopped")
    
    def get_connection_count(self) -> int:
        """Get number of connected peers"""
        return len(self.connected_peers)
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running

class WebSocketClient:
    def __init__(self, peer_host: str, peer_port: int = 8001):
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.websocket = None
        self.connected = False
        self.message_callbacks: Dict[str, Callable] = {}
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_message_callback(self, message_type: str, callback: Callable):
        """Add callback for specific message types"""
        self.message_callbacks[message_type] = callback
    
    async def connect(self):
        """Connect to peer WebSocket server"""
        try:
            uri = f"ws://{self.peer_host}:{self.peer_port}"
            self.logger.info(f"Connecting to {uri}")
            
            self.websocket = await websockets.connect(uri)
            self.connected = True
            self.reconnect_attempts = 0
            
            self.logger.info(f"Connected to peer at {self.peer_host}:{self.peer_port}")
            
            # Start listening for messages
            await self.listen_for_messages()
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.connected = False
            await self.handle_reconnection()
    
    async def listen_for_messages(self):
        """Listen for messages from peer"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(data)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection closed by peer")
            self.connected = False
            await self.handle_reconnection()
        except Exception as e:
            self.logger.error(f"Error listening for messages: {e}")
            self.connected = False
            await self.handle_reconnection()
    
    async def process_message(self, data: dict):
        """Process incoming message and trigger appropriate callbacks"""
        message_type = data.get("type", "unknown")
        
        # Log message
        self.logger.info(f"Received {message_type} from peer")
        
        # Trigger callback if registered
        if message_type in self.message_callbacks:
            try:
                await self.message_callbacks[message_type](data)
            except Exception as e:
                self.logger.error(f"Error in callback for {message_type}: {e}")
    
    async def send_message(self, message: dict):
        """Send message to peer"""
        if not self.connected or not self.websocket:
            self.logger.error("Not connected to peer")
            return False
        
        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.connected = False
            return False
    
    async def handle_reconnection(self):
        """Handle reconnection logic"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return
        
        self.reconnect_attempts += 1
        self.logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        await asyncio.sleep(self.reconnect_delay)
        await self.connect()
    
    async def disconnect(self):
        """Disconnect from peer"""
        self.connected = False
        if self.websocket:
            await self.websocket.close()
        self.logger.info("Disconnected from peer")
    
    def is_connected(self) -> bool:
        """Check if connected to peer"""
        return self.connected
