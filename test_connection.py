#!/usr/bin/env python3
"""
Test WebSocket connection to System 1
"""
import asyncio
import websockets
import json

async def test_connection():
    """Test connection to System 1"""
    system1_ip = "172.19.247.156"
    system1_port = 8000
    uri = f"ws://{system1_ip}:{system1_port}/ws"
    
    print(f"Testing connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: Connected to System 1!")
            
            # Send test message
            test_message = {
                "type": "test",
                "message": "Test message from System 2",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            await websocket.send(json.dumps(test_message))
            print("SENT: Test message")
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"RECEIVED: {data}")
            
            print("SUCCESS: WebSocket communication working!")
            
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print("Make sure System 1 server is running on 172.19.247.156:8000")

if __name__ == "__main__":
    asyncio.run(test_connection())
