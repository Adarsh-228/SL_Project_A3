
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scapy.all import *
import threading
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dictionary to store protocol counts
protocol_counts = {
    'TCP': 0,
    'UDP': 0,
    'ICMP': 0,
    'OTHER': 0
}

def packet_sniffer():
    sniff(prn=process_packet, store=0)

def process_packet(packet):
    if packet.haslayer(TCP):
        protocol_counts['TCP'] += 1
    elif packet.haslayer(UDP):
        protocol_counts['UDP'] += 1
    elif packet.haslayer(ICMP):
        protocol_counts['ICMP'] += 1
    else:
        protocol_counts['OTHER'] += 1

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/data")
async def get_data():
    return protocol_counts

if __name__ == '__main__':
    sniffer_thread = threading.Thread(target=packet_sniffer)
    sniffer_thread.daemon = True
    sniffer_thread.start()
    uvicorn.run(app, host="127.0.0.1", port=5000)
