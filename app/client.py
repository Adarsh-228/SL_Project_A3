"""
Phase 1: WebSocket Client
Simple client to connect to peer's WebSocket server
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, server_host, server_port=8000):
        self.server_host = server_host
        self.server_port = server_port
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        uri = f"ws://{self.server_host}:{self.server_port}/ws"
        logger.info(f"🔌 Connecting to {uri}")
        
        try:
            self.websocket = await websockets.connect(uri)
            self.connected = True
            logger.info(f"✅ Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    async def listen_for_messages(self):
        """Listen for messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"📨 Received: {data.get('type', 'unknown')} - {data.get('message', 'No message')}")
                    
                    # Handle different message types
                    if data.get("type") == "echo":
                        logger.info(f"🔄 Echo received: {data.get('original', {})}")
                    elif data.get("type") == "broadcast":
                        logger.info(f"📢 Broadcast: {data.get('message', 'No message')}")
                    
                except json.JSONDecodeError:
                    logger.error(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Connection closed by server")
            self.connected = False
        except Exception as e:
            logger.error(f"❌ Error listening for messages: {e}")
            self.connected = False
    
    async def send_message(self, message_type="test", message_text="Test message"):
        """Send message to server"""
        if not self.connected or not self.websocket:
            logger.error("❌ Not connected to server")
            return False
        
        try:
            data = {
                "type": message_type,
                "message": message_text,
                "timestamp": datetime.now().isoformat(),
                "client": f"{self.server_host}:{self.server_port}"
            }
            await self.websocket.send(json.dumps(data))
            logger.info(f"📤 Sent: {message_type} - {message_text}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.websocket:
            await self.websocket.close()
        logger.info("🔌 Disconnected from server")

async def interactive_client():
    """Interactive client for testing"""
    print("🎯 Gesture Sync - Phase 1: WebSocket Client")
    print("=" * 50)
    
    # Get server address
    server_host = input("Enter server IP address (e.g., 192.168.1.100): ").strip()
    if not server_host:
        server_host = "127.0.0.1"  # Default to localhost
    
    print(f"Connecting to {server_host}:8000...")
    
    client = WebSocketClient(server_host)
    
    # Try to connect
    if not await client.connect():
        print("❌ Failed to connect. Make sure server is running.")
        return
    
    print("\n✅ Connected! You can now send messages.")
    print("Commands:")
    print("  'test' - Send test message")
    print("  'hello' - Send hello message")
    print("  'quit' - Disconnect and exit")
    print("-" * 50)
    
    # Start listening in background
    listen_task = asyncio.create_task(client.listen_for_messages())
    
    try:
        while client.connected:
            message_text = input("Enter message: ").strip()
            
            if message_text.lower() == 'quit':
                break
            elif message_text.lower() == 'test':
                await client.send_message("test", "Test message from client")
            elif message_text.lower() == 'hello':
                await client.send_message("hello", f"Hello from client at {datetime.now().strftime('%H:%M:%S')}")
            elif message_text:
                await client.send_message("custom", message_text)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    
    finally:
        listen_task.cancel()
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(interactive_client())
