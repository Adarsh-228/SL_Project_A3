"""
Secure clipboard synchronization between peers
"""
import pyperclip
import json
import time
import threading
from typing import Optional, Callable, List
from cryptography.fernet import Fernet
import base64
import hashlib

class ClipboardSync:
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.last_clipboard_content = ""
        self.last_sync_time = 0
        self.sync_callbacks: List[Callable] = []
        self.monitoring = False
        self.monitor_thread = None
        
        # Start monitoring clipboard changes
        self.start_monitoring()
    
    def add_sync_callback(self, callback: Callable):
        """Add callback function to be called when clipboard changes"""
        self.sync_callbacks.append(callback)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt clipboard data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt clipboard data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def get_encryption_key_string(self) -> str:
        """Get encryption key as string for sharing with peer"""
        return base64.b64encode(self.encryption_key).decode()
    
    def set_encryption_key(self, key_string: str):
        """Set encryption key from string"""
        try:
            self.encryption_key = base64.b64decode(key_string.encode())
            self.cipher = Fernet(self.encryption_key)
        except Exception as e:
            print(f"Error setting encryption key: {e}")
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error reading clipboard: {e}")
            return ""
    
    def set_clipboard_content(self, content: str):
        """Set clipboard content"""
        try:
            pyperclip.copy(content)
            self.last_clipboard_content = content
            self.last_sync_time = time.time()
            print(f"Clipboard updated: {content[:50]}{'...' if len(content) > 50 else ''}")
        except Exception as e:
            print(f"Error setting clipboard: {e}")
    
    def start_monitoring(self):
        """Start monitoring clipboard for changes"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring clipboard"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_clipboard(self):
        """Monitor clipboard for changes"""
        while self.monitoring:
            try:
                current_content = self.get_clipboard_content()
                
                # Check if clipboard content has changed
                if current_content != self.last_clipboard_content:
                    self.last_clipboard_content = current_content
                    self.last_sync_time = time.time()
                    
                    # Notify callbacks
                    for callback in self.sync_callbacks:
                        try:
                            callback(current_content)
                        except Exception as e:
                            print(f"Callback error: {e}")
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
                time.sleep(1)
    
    def sync_to_peer(self, content: str) -> dict:
        """Prepare clipboard content for syncing to peer"""
        encrypted_content = self.encrypt_data(content)
        sync_data = {
            "type": "clipboard_sync",
            "content": encrypted_content,
            "timestamp": time.time(),
            "checksum": hashlib.md5(content.encode()).hexdigest()
        }
        return sync_data
    
    def sync_from_peer(self, sync_data: dict) -> bool:
        """Process clipboard sync from peer"""
        try:
            if sync_data.get("type") != "clipboard_sync":
                return False
            
            encrypted_content = sync_data.get("content", "")
            if not encrypted_content:
                return False
            
            # Decrypt content
            decrypted_content = self.decrypt_data(encrypted_content)
            if not decrypted_content:
                return False
            
            # Verify checksum
            expected_checksum = sync_data.get("checksum", "")
            actual_checksum = hashlib.md5(decrypted_content.encode()).hexdigest()
            
            if expected_checksum != actual_checksum:
                print("Checksum mismatch in clipboard sync")
                return False
            
            # Update clipboard if content is different
            current_content = self.get_clipboard_content()
            if decrypted_content != current_content:
                self.set_clipboard_content(decrypted_content)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing clipboard sync: {e}")
            return False
