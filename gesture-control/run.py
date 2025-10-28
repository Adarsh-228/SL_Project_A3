#!/usr/bin/env python3
"""
Peer Messaging - Run Script
"""
import sys
import os

def main():
    print("🎯 Peer Messaging")
    print("=" * 50)
    print("🚀 Starting server...")
    print("-" * 50)
    
    try:
        # Launch the FastAPI server
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run 'python setup.py' to install dependencies")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Ensure port 8000 is free and firewall allows access")

if __name__ == "__main__":
    main()
