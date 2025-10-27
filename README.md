# 🎯 Gesture Sync - Phase 1

A step-by-step implementation of gesture-based copy/paste between two PCs.

## 📁 Project Structure

```
gesture-sync/
├── app/
│   ├── main.py                ← Main entry point (server + client)
│   ├── server.py              ← FastAPI WebSocket server
│   ├── client.py              ← WebSocket client
│   └── config.json            ← Network configuration
├── templates/
│   └── index.html             ← Web interface
├── requirements.txt           ← Python dependencies
└── README.md                  ← This file
```

## 🚀 Phase 1: WebSocket Connectivity ✅ COMPLETED

### Goal
Ensure both PCs can communicate over WebSocket with bi-directional messaging.

## 🎥 Phase 2: OpenCV Camera Feed

### Goal
Test webcam capture and display video feed in browser with smooth frame rate.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start server on both PCs:**
   ```bash
   python -m app.main
   ```

3. **Open browser on both PCs:**
   ```
   http://localhost:8000
   ```

### Testing

1. **Test camera feed:**
   - Verify camera feed displays in browser
   - Check frame rate is smooth and consistent
   - Test "Toggle Camera" and "Test Camera" buttons

2. **Test WebSocket (still works):**
   - Click "Send Test Message" on both PCs
   - Verify messages appear in logs

3. **Test peer connection:**
   - On PC-B, click "Connect to Peer"
   - Enter PC-A's IP address
   - Send messages between PCs

### Success Criteria

- ✅ Camera opens and displays video feed
- ✅ Frame rate is smooth and consistent
- ✅ Video feed shows in browser
- ✅ WebSocket communication still works
- ✅ Both PCs can communicate with camera active

## 🔄 Next Phases

- **Phase 3:** MediaPipe Gesture Detection
  - ✊ **Fist** = Copy gesture
  - ✋ **Open hand** = Paste gesture
- **Phase 4:** Clipboard Actions Integration
- **Phase 5:** Complete Gesture + WebSocket + Clipboard System

## 🐛 Troubleshooting

- **Connection failed:** Check firewall settings, ensure ports 8000-8001 are open
- **No messages:** Verify both PCs are on the same network
- **WebSocket errors:** Check browser console for detailed error messages