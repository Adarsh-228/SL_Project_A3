"""
Action handlers for different gestures
"""
import pyperclip
import pyautogui
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GestureActions:
    def __init__(self):
        self.last_action_time = 0
        self.min_action_interval = 0.5  # Minimum time between actions
        self.cursor_enabled = False
        self.selection_started = False
        
    def can_perform_action(self) -> bool:
        """Check if enough time has passed since last action"""
        current_time = time.time()
        if current_time - self.last_action_time >= self.min_action_interval:
            self.last_action_time = current_time
            return True
        return False
    
    def handle_copy(self):
        """Handle copy gesture - copy current clipboard content"""
        if not self.can_perform_action():
            return
        
        try:
            content = pyperclip.paste()
            if content:
                logger.info(f"Copy gesture: Content copied - {content[:50]}...")
                print(f"📋 Copy: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                logger.info("Copy gesture: No content in clipboard")
                print("📋 Copy: No content in clipboard")
        except Exception as e:
            logger.error(f"Copy gesture error: {e}")
            print(f"❌ Copy error: {e}")
    
    def handle_paste(self):
        """Handle paste gesture - paste clipboard content"""
        if not self.can_perform_action():
            return
        
        try:
            content = pyperclip.paste()
            if content:
                # Simulate Ctrl+V to paste
                pyautogui.hotkey('ctrl', 'v')
                logger.info(f"Paste gesture: Content pasted - {content[:50]}...")
                print(f"📋 Paste: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                logger.info("Paste gesture: No content to paste")
                print("📋 Paste: No content to paste")
        except Exception as e:
            logger.error(f"Paste gesture error: {e}")
            print(f"❌ Paste error: {e}")
    
    def handle_select_all(self):
        """Handle select all gesture - select all text"""
        if not self.can_perform_action():
            return
        
        try:
            pyautogui.hotkey('ctrl', 'a')
            logger.info("Select All gesture: All text selected")
            print("🔍 Select All: All text selected")
        except Exception as e:
            logger.error(f"Select All gesture error: {e}")
            print(f"❌ Select All error: {e}")
    
    def handle_cursor_toggle(self):
        """Handle cursor gesture - toggle cursor mode"""
        if not self.can_perform_action():
            return
        
        self.cursor_enabled = not self.cursor_enabled
        status = "enabled" if self.cursor_enabled else "disabled"
        logger.info(f"Cursor gesture: Cursor mode {status}")
        print(f"👆 Cursor: Mode {status}")
    
    def handle_select(self):
        """Handle select gesture - start text selection"""
        if not self.can_perform_action():
            return
        
        try:
            if not self.selection_started:
                # Start selection by holding down shift
                pyautogui.keyDown('shift')
                self.selection_started = True
                logger.info("Select gesture: Selection started")
                print("🔍 Select: Selection started")
            else:
                # End selection by releasing shift
                pyautogui.keyUp('shift')
                self.selection_started = False
                logger.info("Select gesture: Selection ended")
                print("🔍 Select: Selection ended")
        except Exception as e:
            logger.error(f"Select gesture error: {e}")
            print(f"❌ Select error: {e}")
    
    def handle_gesture(self, gesture: str):
        """Main gesture handler"""
        gesture_handlers = {
            "copy": self.handle_copy,
            "paste": self.handle_paste,
            "select_all": self.handle_select_all,
            "cursor": self.handle_cursor_toggle,
            "select": self.handle_select
        }
        
        handler = gesture_handlers.get(gesture)
        if handler:
            handler()
        else:
            logger.warning(f"Unknown gesture: {gesture}")
            print(f"⚠️ Unknown gesture: {gesture}")
    
    def cleanup(self):
        """Cleanup any ongoing actions"""
        try:
            if self.selection_started:
                pyautogui.keyUp('shift')
                self.selection_started = False
                logger.info("Cleanup: Released shift key")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Global instance
gesture_actions = GestureActions()
