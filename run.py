#!/usr/bin/env python3
"""
Simple run script for Gesture Sync
"""
import sys
import os

def main():
    """Run the Gesture Sync application"""
    print("🎯 Starting Gesture Sync...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Import and run the main application
        from main import main as app_main
        import asyncio
        asyncio.run(app_main())
    except KeyboardInterrupt:
        print("\n👋 Gesture Sync stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 Try running: python setup.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
