#!/usr/bin/env python3
"""
Web Server Launcher for Peer Messaging
"""
import uvicorn
import sys
import os

def main():
    print("Peer Messaging - Web Server")
    print("=" * 60)
    print("Starting web server...")
    print("Web UI:       http://localhost:8000")
    print("WebSocket:    ws://<host-ip>:8000/ws")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start the FastAPI server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
