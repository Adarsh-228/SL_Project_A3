"""
Enhanced gesture recognition system for copy/paste operations
"""
import cv2
import mediapipe as mp
import time
import math
import numpy as np
from typing import Optional, Callable, Tuple
from config import config

class GestureRecognizer:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=config.get('gestures.sensitivity', 0.7),
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture state tracking
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_hold_start = 0
        self.gesture_callbacks: list = []
        
        # Gesture thresholds
        self.hold_duration = config.get('gestures.hold_duration', 1.0)
        self.min_gesture_interval = 0.5  # Minimum time between gestures
        
    def add_gesture_callback(self, callback: Callable):
        """Add callback function to be called when gestures are detected"""
        self.gesture_callbacks.append(callback)
    
    def is_finger_extended(self, landmarks, finger_tip, finger_pip, finger_mcp) -> bool:
        """Check if a finger is extended"""
        return landmarks[finger_tip].y < landmarks[finger_pip].y < landmarks[finger_mcp].y
    
    def is_finger_folded(self, landmarks, finger_tip, finger_pip, finger_mcp) -> bool:
        """Check if a finger is folded"""
        return landmarks[finger_tip].y > landmarks[finger_pip].y > landmarks[finger_mcp].y
    
    def detect_copy_gesture(self, landmarks) -> bool:
        """Detect copy gesture: Index and middle finger extended, others folded"""
        # Check index finger (extended)
        index_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP
        )
        
        # Check middle finger (extended)
        middle_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP
        )
        
        # Check ring finger (folded)
        ring_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP
        )
        
        # Check pinky (folded)
        pinky_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
            self.mp_hands.HandLandmark.PINKY_MCP
        )
        
        # Check thumb (folded or neutral)
        thumb_folded = landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x > landmarks[self.mp_hands.HandLandmark.THUMB_IP].x
        
        return index_extended and middle_extended and ring_folded and pinky_folded and thumb_folded
    
    def detect_select_all_gesture(self, landmarks) -> bool:
        """Detect select all gesture: Fist (all fingers folded)"""
        # Check all fingers are folded
        index_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP
        )
        
        middle_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP
        )
        
        ring_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP
        )
        
        pinky_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
            self.mp_hands.HandLandmark.PINKY_MCP
        )
        
        # Thumb can be folded or neutral for fist
        thumb_folded = landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x > landmarks[self.mp_hands.HandLandmark.THUMB_IP].x
        
        return index_folded and middle_folded and ring_folded and pinky_folded and thumb_folded
    
    def detect_cursor_gesture(self, landmarks) -> bool:
        """Detect cursor gesture: Only index finger extended (pointing)"""
        # Check index finger (extended)
        index_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP
        )
        
        # Check other fingers are folded
        middle_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP
        )
        
        ring_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP
        )
        
        pinky_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
            self.mp_hands.HandLandmark.PINKY_MCP
        )
        
        # Thumb can be extended or neutral for pointing
        thumb_extended = landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x < landmarks[self.mp_hands.HandLandmark.THUMB_IP].x
        
        return index_extended and middle_folded and ring_folded and pinky_folded and thumb_extended
    
    def detect_select_gesture(self, landmarks) -> bool:
        """Detect select gesture: Index and thumb extended (OK sign)"""
        # Check index finger (extended)
        index_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP
        )
        
        # Check thumb (extended)
        thumb_extended = landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x < landmarks[self.mp_hands.HandLandmark.THUMB_IP].x
        
        # Check other fingers are folded
        middle_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP
        )
        
        ring_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP
        )
        
        pinky_folded = self.is_finger_folded(
            landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
            self.mp_hands.HandLandmark.PINKY_MCP
        )
        
        return index_extended and thumb_extended and middle_folded and ring_folded and pinky_folded
    
    def detect_paste_gesture(self, landmarks) -> bool:
        """Detect paste gesture: All fingers extended (open hand)"""
        # Check all fingers are extended
        index_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP
        )
        
        middle_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP
        )
        
        ring_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP
        )
        
        pinky_extended = self.is_finger_extended(
            landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
            self.mp_hands.HandLandmark.PINKY_MCP
        )
        
        # Thumb can be extended or neutral for paste gesture
        thumb_extended = landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x < landmarks[self.mp_hands.HandLandmark.THUMB_IP].x
        
        return index_extended and middle_extended and ring_extended and pinky_extended and thumb_extended
    
    def detect_gesture(self, landmarks) -> Optional[str]:
        """Detect the current gesture from hand landmarks"""
        if self.detect_copy_gesture(landmarks):
            return "copy"
        elif self.detect_paste_gesture(landmarks):
            return "paste"
        elif self.detect_select_all_gesture(landmarks):
            return "select_all"
        elif self.detect_cursor_gesture(landmarks):
            return "cursor"
        elif self.detect_select_gesture(landmarks):
            return "select"
        return None
    
    def process_gesture(self, gesture: str, current_time: float):
        """Process detected gesture with hold duration logic"""
        if gesture != self.last_gesture:
            # New gesture detected
            self.last_gesture = gesture
            self.gesture_hold_start = current_time
            self.last_gesture_time = current_time
        else:
            # Same gesture continuing
            hold_duration = current_time - self.gesture_hold_start
            
            # Check if gesture has been held long enough
            if hold_duration >= self.hold_duration:
                # Check minimum interval between gesture triggers
                if current_time - self.last_gesture_time >= self.min_gesture_interval:
                    # Trigger gesture callback
                    for callback in self.gesture_callbacks:
                        try:
                            callback(gesture)
                        except Exception as e:
                            print(f"Gesture callback error: {e}")
                    
                    self.last_gesture_time = current_time
                    print(f"Gesture triggered: {gesture}")
    
    def draw_gesture_overlay(self, frame, gesture: Optional[str], landmarks=None):
        """Draw gesture information overlay on frame"""
        if config.get('ui.show_gesture_overlay', True):
            # Draw hand landmarks
            if landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
            
            # Draw gesture status
            if gesture:
                current_time = time.time()
                hold_duration = current_time - self.gesture_hold_start if self.last_gesture == gesture else 0
                progress = min(hold_duration / self.hold_duration, 1.0)
                
                # Gesture name
                cv2.putText(frame, f"Gesture: {gesture.upper()}", 
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Progress bar
                bar_width = 200
                bar_height = 20
                bar_x = 50
                bar_y = 80
                
                # Background
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                
                # Progress
                progress_width = int(bar_width * progress)
                color = (0, 255, 0) if progress >= 1.0 else (0, 255, 255)
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), color, -1)
                
                # Border
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
                
                # Hold instructions
                if progress < 1.0:
                    cv2.putText(frame, f"Hold for {self.hold_duration:.1f}s", 
                               (bar_x, bar_y + bar_height + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                else:
                    cv2.putText(frame, "Gesture Ready!", 
                               (bar_x, bar_y + bar_height + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    
    def process_frame(self, frame) -> Tuple[np.ndarray, Optional[str]]:
        """Process a single frame and return annotated frame with detected gesture"""
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.hands.process(rgb_frame)
        
        detected_gesture = None
        current_time = time.time()
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Detect gesture
                gesture = self.detect_gesture(hand_landmarks.landmark)
                
                if gesture:
                    detected_gesture = gesture
                    self.process_gesture(gesture, current_time)
                
                # Draw overlay
                self.draw_gesture_overlay(frame, detected_gesture, hand_landmarks)
        
        return frame, detected_gesture
    
    def cleanup(self):
        """Cleanup resources"""
        self.hands.close()
