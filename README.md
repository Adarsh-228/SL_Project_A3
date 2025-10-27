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

## 🚀 Phase 1: WebSocket Connectivity

### Goal
Ensure both PCs can communicate over WebSocket with bi-directional messaging.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start server on PC-A:**
   ```bash
   python app/main.py
   ```

3. **Start server on PC-B:**
   ```bash
   python app/main.py
   ```

4. **Open browser on both PCs:**
   ```
   http://localhost:8000
   ```

### Testing

1. **Test local WebSocket:**
   - Click "Send Test Message" on both PCs
   - Verify messages appear in logs

2. **Test peer connection:**
   - On PC-B, click "Connect to Peer"
   - Enter PC-A's IP address
   - Send messages between PCs

### Success Criteria

- ✅ Both PCs can start WebSocket servers
- ✅ Both PCs can connect as clients to each other
- ✅ Messages can be sent PC-A → PC-B
- ✅ Messages can be sent PC-B → PC-A
- ✅ Both PCs receive and display messages

## 🔄 Next Phases

- **Phase 2:** OpenCV Camera Feed
- **Phase 3:** MediaPipe Gesture Detection
- **Phase 4:** Clipboard Actions Integration
- **Phase 5:** Complete Gesture + WebSocket + Clipboard System

## 🐛 Troubleshooting

- **Connection failed:** Check firewall settings, ensure ports 8000-8001 are open
- **No messages:** Verify both PCs are on the same network
- **WebSocket errors:** Check browser console for detailed error messages