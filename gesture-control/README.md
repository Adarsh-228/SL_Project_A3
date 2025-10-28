Peer Messaging (Two-System Setup)

Prerequisites
- Python 3.10+
- Windows firewall allows inbound on port 8000 (or allow when prompted)

Install
1) Open terminal in this folder
2) (Optional) Create a virtualenv
3) Run: `python main.py`

Run (on both systems)
1) Start the server on System A and System B:
   - `python main.py`
   - The server listens on 0.0.0.0:8000
2) On each system, open `http://localhost:8000` in the browser.

Connect
1) Find the IPv4 of the peer system (e.g., 192.168.1.25)
2) Enter the peer IPv4 in the UI and click Connect
3) Use the Chat panel to send messages.

Notes
- Ensure both systems are on the same network and can reach port 8000.
- To use a different port, edit `uvicorn.run(..., port=YOUR_PORT)` in `main.py` and connect at `ws://<ip>:<port>/ws`.
