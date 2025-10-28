#!/usr/bin/env python3
"""
Setup script for Peer Messaging
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🚀 Installing Peer Messaging dependencies...")
    print("=" * 50)
    
    try:
        # Install packages
        packages = ["fastapi==0.104.1", "uvicorn[standard]==0.24.0", "jinja2==3.1.2"]
        
        for package in packages:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def test_installation():
    """Test if all packages work"""
    print("\n🧪 Testing installation...")
    
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import jinja2   # noqa: F401
        print("🎉 All tests passed! Ready to run Peer Messaging!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Peer Messaging Setup")
    print("=" * 50)
    
    # Install requirements
    if install_requirements():
        # Test installation
        if test_installation():
            print("\n🚀 Setup complete! Run the server:")
            print("   python main.py")
        else:
            print("❌ Setup failed during testing")
    else:
        print("❌ Setup failed during installation")

if __name__ == "__main__":
    main()
