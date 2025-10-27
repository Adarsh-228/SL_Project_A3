#!/usr/bin/env python3
"""
Simple run script for Phase 2: Camera Feed
"""
import sys
import os

def main():
    """Run Phase 2: Camera Feed"""
    print("Gesture Sync - Phase 2: Camera Feed")
    print("=" * 50)
    print("Open your browser to: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Import and run the main application
        from app.main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nPhase 2 stopped by user")
    except Exception as e:
        print(f"\nERROR starting Phase 2: {e}")
        print("Make sure you have installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
