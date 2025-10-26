"""
Configuration settings for the Gesture Sync application
"""
import os
import json
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_file = "gesture_sync_config.json"
        self.default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "websocket_port": 8001
            },
            "peer": {
                "host": None,
                "port": 8001,
                "auto_discover": True
            },
            "gestures": {
                "copy_gesture": "peace_sign",  # Index and middle finger up
                "paste_gesture": "open_hand",  # All fingers extended
                "sensitivity": 0.7,
                "hold_duration": 1.0
            },
            "security": {
                "encryption_enabled": True,
                "shared_key": None  # Will be generated automatically
            },
            "ui": {
                "show_video_feed": True,
                "show_gesture_overlay": True,
                "theme": "dark"
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'server.port')"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

# Global config instance
config = Config()
