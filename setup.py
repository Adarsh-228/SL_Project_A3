#!/usr/bin/env python3
"""
Setup script for Gesture Sync application
"""
import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_camera():
    """Check if camera is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera is working")
                return True
            else:
                print("⚠️  Camera detected but cannot capture frames")
                return False
        else:
            print("❌ No camera detected")
            return False
    except ImportError:
        print("⚠️  OpenCV not installed yet - camera check will be done after installation")
        return True
    except Exception as e:
        print(f"⚠️  Camera check failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["templates", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🎯 Gesture Sync Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check camera
    check_camera()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python main.py")
    print("2. Open your browser: http://localhost:8000")
    print("3. Allow camera access when prompted")
    print("4. Copy this folder to the second PC and repeat setup")
    print("\n📖 For detailed instructions, see README.md")
    print("🐛 For troubleshooting, check the Activity Log in the web interface")

if __name__ == "__main__":
    main()
