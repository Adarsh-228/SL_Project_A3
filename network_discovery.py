"""
Network utilities for peer discovery and communication
"""
import socket
import threading
import time
import json
from typing import List, Dict, Optional
import netifaces

class NetworkDiscovery:
    def __init__(self, port: int = 8001):
        self.port = port
        self.broadcast_port = 8002
        self.discovered_peers: List[Dict] = []
        self.running = False
        self.broadcast_socket = None
        self.listen_socket = None
    
    def get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            # Get the default gateway interface
            gateways = netifaces.gateways()
            default_interface = gateways['default'][netifaces.AF_INET][1]
            
            # Get IP address of the default interface
            addrs = netifaces.ifaddresses(default_interface)
            ip = addrs[netifaces.AF_INET][0]['addr']
            return ip
        except Exception:
            # Fallback method
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                return "127.0.0.1"
    
    def get_broadcast_address(self) -> str:
        """Get the broadcast address for the local network"""
        try:
            gateways = netifaces.gateways()
            default_interface = gateways['default'][netifaces.AF_INET][1]
            
            addrs = netifaces.ifaddresses(default_interface)
            broadcast = addrs[netifaces.AF_INET][0].get('broadcast')
            if broadcast:
                return broadcast
            
            # Calculate broadcast address
            ip = addrs[netifaces.AF_INET][0]['addr']
            netmask = addrs[netifaces.AF_INET][0]['netmask']
            
            ip_parts = [int(x) for x in ip.split('.')]
            mask_parts = [int(x) for x in netmask.split('.')]
            
            broadcast_parts = []
            for i in range(4):
                broadcast_parts.append(str(ip_parts[i] | (~mask_parts[i] & 0xFF)))
            
            return '.'.join(broadcast_parts)
        except Exception:
            return "255.255.255.255"
    
    def start_broadcast(self):
        """Start broadcasting this peer's information"""
        self.running = True
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        local_ip = self.get_local_ip()
        peer_info = {
            "ip": local_ip,
            "port": self.port,
            "timestamp": time.time(),
            "hostname": socket.gethostname()
        }
        
        def broadcast_loop():
            while self.running:
                try:
                    message = json.dumps(peer_info).encode()
                    self.broadcast_socket.sendto(message, (self.get_broadcast_address(), self.broadcast_port))
                    time.sleep(2)  # Broadcast every 2 seconds
                except Exception as e:
                    print(f"Broadcast error: {e}")
                    time.sleep(5)
        
        threading.Thread(target=broadcast_loop, daemon=True).start()
    
    def start_listening(self):
        """Start listening for peer broadcasts"""
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', self.broadcast_port))
        self.listen_socket.settimeout(1.0)
        
        def listen_loop():
            while self.running:
                try:
                    data, addr = self.listen_socket.recvfrom(1024)
                    peer_info = json.loads(data.decode())
                    
                    # Don't add ourselves
                    if peer_info["ip"] != self.get_local_ip():
                        # Update or add peer
                        existing_peer = None
                        for peer in self.discovered_peers:
                            if peer["ip"] == peer_info["ip"]:
                                existing_peer = peer
                                break
                        
                        if existing_peer:
                            existing_peer.update(peer_info)
                        else:
                            self.discovered_peers.append(peer_info)
                            print(f"Discovered peer: {peer_info['hostname']} at {peer_info['ip']}:{peer_info['port']}")
                
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Listen error: {e}")
                    time.sleep(1)
        
        threading.Thread(target=listen_loop, daemon=True).start()
    
    def get_peers(self) -> List[Dict]:
        """Get list of discovered peers"""
        # Remove stale peers (older than 10 seconds)
        current_time = time.time()
        self.discovered_peers = [
            peer for peer in self.discovered_peers 
            if current_time - peer.get("timestamp", 0) < 10
        ]
        return self.discovered_peers.copy()
    
    def stop(self):
        """Stop discovery service"""
        self.running = False
        if self.broadcast_socket:
            self.broadcast_socket.close()
        if self.listen_socket:
            self.listen_socket.close()
    
    def start_discovery(self):
        """Start both broadcasting and listening"""
        self.start_broadcast()
        self.start_listening()
        print(f"Network discovery started on port {self.broadcast_port}")
        print(f"Local IP: {self.get_local_ip()}")
        print(f"Broadcast address: {self.get_broadcast_address()}")
