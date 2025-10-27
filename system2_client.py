#!/usr/bin/env python3
"""
System 2 - Connect to System 1
"""
import asyncio
import websockets
import json
from datetime import datetime

class System2Client:
    def __init__(self, system1_ip="172.19.247.156", system1_port=8000):
        self.system1_ip = system1_ip
        self.system1_port = system1_port
        self.websocket = None
        
    async def connect_to_system1(self):
        """Connect to System 1"""
        uri = f"ws://{self.system1_ip}:{self.system1_port}/ws"
        print(f"Connecting to System 1 at: {uri}")
        
        try:
            self.websocket = await websockets.connect(uri)
            print("SUCCESS: Connected to System 1!")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to System 1: {e}")
            return False
    
    async def send_message(self, message):
        """Send message to System 1"""
        if self.websocket:
            data = {
                "type": "system2_message",
                "message": message,
                "from": "System 2",
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket.send(json.dumps(data))
            print(f"SENT: {message}")
    
    async def listen_for_messages(self):
        """Listen for messages from System 1"""
        if self.websocket:
            try:
                async for message in self.websocket:
                    data = json.loads(message)
                    print(f"RECEIVED from System 1: {data}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection to System 1 closed")
            except Exception as e:
                print(f"Error listening: {e}")
    
    async def run(self):
        """Main run function"""
        print("=" * 50)
        print("SYSTEM 2 - CONNECTING TO SYSTEM 1")
        print("=" * 50)
        print(f"System 1 IP: {self.system1_ip}")
        print(f"System 1 Port: {self.system1_port}")
        print("-" * 50)
        
        # Connect to System 1
        if await self.connect_to_system1():
            # Send initial message
            await self.send_message("Hello from System 2!")
            
            # Start listening for messages
            await self.listen_for_messages()
        else:
            print("Failed to connect to System 1")

async def main():
    client = System2Client()
    await client.run()

if __name__ == "__main__":
    print("Starting System 2 client...")
    asyncio.run(main())
