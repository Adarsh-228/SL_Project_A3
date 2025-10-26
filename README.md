# 🎯 Gesture Sync - Copy & Paste with Hand Gestures

A Python-based gesture communication system that enables two PCs to copy and paste text between each other using hand gestures. Each PC runs the same application, acting as both a FastAPI WebSocket server and client.

## ✨ Features

- **Hand Gesture Recognition**: Uses OpenCV + MediaPipe to detect copy/paste gestures via webcam
- **Real-time Communication**: FastAPI WebSocket server for instant data synchronization
- **Automatic Peer Discovery**: Automatically discovers other PCs on the local network
- **Secure Data Transfer**: Encrypted clipboard synchronization with checksum verification
- **Modern Web UI**: Beautiful, responsive interface for monitoring and control
- **Cross-platform**: Works on Windows, macOS, and Linux
- **No Hardware Required**: Fully software-based solution

## 🎮 Gesture Controls

- **Copy Gesture**: Peace sign (index + middle finger extended, others folded)
- **Paste Gesture**: Open hand (all fingers extended)
- **Hold Duration**: Hold gesture for 1 second to trigger action
- **Visual Feedback**: Real-time gesture detection with progress bar

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Two PCs on the same local network

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

### Setup on Second PC

1. **Copy the entire project folder** to the second PC
2. **Install dependencies** (same as above)
3. **Run the application**:
   ```bash
   python main.py
   ```

4. **The applications will automatically discover each other** on the local network

## 🔧 Configuration

The application uses `config.py` for configuration. Key settings include:

- **Server Settings**: Host and port configuration
- **Gesture Sensitivity**: Detection confidence threshold (0.5-0.9)
- **Hold Duration**: Time to hold gesture before triggering (0.5-3.0 seconds)
- **Security**: Encryption settings for data transfer
- **UI Options**: Display preferences

## 📱 Usage

### Basic Operation

1. **Start both applications** on separate PCs
2. **Allow webcam access** when prompted
3. **Wait for peer discovery** - the second PC should appear in the "Discovered Peers" section
4. **Click "Connect"** next to the discovered peer
5. **Test gestures**:
   - Show peace sign to copy current clipboard content
   - Show open hand to paste (content should appear in clipboard)

### Manual Connection

If automatic discovery doesn't work:

1. **Note the IP address** of the first PC (shown in the Status panel)
2. **On the second PC**, enter the IP address in the "Manual Connect" field
3. **Click "Connect"**

### Troubleshooting

**Webcam not working:**
- Ensure webcam is not being used by another application
- Check camera permissions in your operating system
- Try restarting the application

**Peers not discovering each other:**
- Ensure both PCs are on the same local network
- Check firewall settings (allow ports 8000-8002)
- Try manual connection using IP addresses

**Gestures not detected:**
- Ensure good lighting
- Keep hand clearly visible in camera frame
- Adjust gesture sensitivity in Settings
- Try different hold durations

## 🏗️ Architecture

### Components

- **`main.py`**: Main application entry point and FastAPI server
- **`gesture_recognition.py`**: Hand gesture detection using MediaPipe
- **`clipboard_sync.py`**: Secure clipboard synchronization with encryption
- **`network_discovery.py`**: Automatic peer discovery on local network
- **`websocket_manager.py`**: WebSocket server and client for real-time communication
- **`config.py`**: Configuration management system
- **`templates/index.html`**: Modern web UI interface

### Data Flow

1. **Gesture Detection**: Webcam captures hand movements → MediaPipe processes landmarks → Gesture recognition
2. **Action Trigger**: Gesture held for required duration → Callback triggered
3. **Data Sync**: Clipboard content encrypted → Sent via WebSocket → Decrypted on peer
4. **UI Update**: Real-time status updates and activity logging

## 🔒 Security Features

- **End-to-end Encryption**: All clipboard data encrypted using Fernet (AES 128)
- **Checksum Verification**: MD5 checksums prevent data corruption
- **Automatic Key Generation**: Unique encryption keys per session
- **Local Network Only**: No external internet communication

## 🌐 Network Requirements

- **Ports Used**:
  - 8000: FastAPI web server
  - 8001: WebSocket communication
  - 8002: Peer discovery broadcasts
- **Firewall**: Allow these ports for local network communication
- **Network**: Both PCs must be on the same local network (WiFi/LAN)

## 🛠️ Development

### Project Structure
```
gesture-sync/
├── main.py                 # Main application
├── config.py              # Configuration management
├── gesture_recognition.py # Hand gesture detection
├── clipboard_sync.py      # Clipboard synchronization
├── network_discovery.py   # Peer discovery
├── websocket_manager.py   # WebSocket communication
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web UI
└── README.md            # This file
```

### Dependencies

- **FastAPI**: Web framework and API server
- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Hand landmark detection
- **WebSockets**: Real-time communication
- **Cryptography**: Data encryption
- **PyPerclip**: Clipboard access
- **Netifaces**: Network interface detection

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2GB available
- **Storage**: 100MB free space
- **Network**: Local network connection
- **Camera**: USB webcam or built-in camera

### Recommended Requirements
- **OS**: Latest version of Windows/macOS/Linux
- **Python**: 3.9 or higher
- **RAM**: 4GB available
- **Camera**: HD webcam with good lighting
- **Network**: Stable WiFi or Ethernet connection

## 🐛 Troubleshooting

### Common Issues

**"Could not open video capture"**
- Check if webcam is being used by another application
- Verify camera permissions
- Try unplugging and reconnecting USB camera

**"Connection failed"**
- Verify both PCs are on the same network
- Check firewall settings
- Ensure ports 8000-8002 are not blocked
- Try using IP address instead of hostname

**"No peers discovered"**
- Wait 10-15 seconds for discovery
- Check network connectivity
- Verify firewall allows UDP broadcasts
- Try manual connection

**Gestures not working**
- Ensure good lighting conditions
- Keep hand 1-2 feet from camera
- Make clear, deliberate gestures
- Adjust sensitivity settings

### Getting Help

1. **Check the Activity Log** in the web interface for error messages
2. **Verify all dependencies** are installed correctly
3. **Test with a single PC first** to ensure basic functionality
4. **Check network connectivity** between PCs

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Enjoy copying and pasting with hand gestures! 🎯✋**
