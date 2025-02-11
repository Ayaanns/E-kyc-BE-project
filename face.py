import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
import os

class LivenessDetector:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize detectors
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        
        # Initialize variables for blink detection
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.blink_counter = 0
        self.previous_blink_state = False
        
        # Variables for wave detection
        self.previous_positions = []
        self.gesture_verified = False
        
        # Variables for capturing
        self.capture_folder = "captured_faces"
        if not os.path.exists(self.capture_folder):
            os.makedirs(self.capture_folder)
    
    def calculate_EAR(self, eye_points):
        """Calculate Eye Aspect Ratio"""
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, face_landmarks, frame):
        """Detect eye blinks"""
        if face_landmarks:
            mesh_points = np.array([
                np.multiply([p.x, p.y], [frame.shape[1], frame.shape[0]]).astype(int)
                for p in face_landmarks.landmark
            ])
            
            left_eye = mesh_points[self.LEFT_EYE]
            right_eye = mesh_points[self.RIGHT_EYE]
            
            left_ear = self.calculate_EAR(left_eye)
            right_ear = self.calculate_EAR(right_eye)
            
            avg_ear = (left_ear + right_ear) / 2
            
            if avg_ear < 0.25 and not self.previous_blink_state:
                self.blink_counter += 1
                self.previous_blink_state = True
            elif avg_ear >= 0.25:
                self.previous_blink_state = False
            
            cv2.polylines(frame, [left_eye], True, (0, 255, 0), 1)
            cv2.polylines(frame, [right_eye], True, (0, 255, 0), 1)
    
    def verify_wave(self, hand_landmarks):
        """Verify hand waving gesture"""
        if hand_landmarks:
            # Track wrist position for wave detection
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            self.previous_positions.append(wrist.x)
            
            # Keep only last 10 positions
            if len(self.previous_positions) > 10:
                self.previous_positions.pop(0)
            
            # Check for horizontal movement (wave)
            if len(self.previous_positions) >= 10:
                movement = max(self.previous_positions) - min(self.previous_positions)
                return movement > 0.2  # Threshold for wave detection
        return False
    
    def capture_face(self, frame):
        """Capture and save face image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"face_capture_{timestamp}.jpg"
        filepath = os.path.join(self.capture_folder, filename)
        cv2.imwrite(filepath, frame)
        return filepath
    
    def start_verification(self):
        """Start the liveness detection and face capture process"""
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        verification_complete = False
        
        instructions = [
            "Blink 3 times",
            "Wave your hand side to side",
            "Verification complete!",
            "Capturing face..."
        ]
        current_instruction = 0
        
        while cap.isOpened() and not verification_complete:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process face landmarks
            face_results = self.face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                self.detect_blink(face_results.multi_face_landmarks[0], frame)
            
            # Process hand landmarks
            hand_results = self.hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    if not self.gesture_verified:
                        self.gesture_verified = self.verify_wave(hand_landmarks)
            
            # Display current instruction and status
            cv2.putText(frame, instructions[current_instruction], (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Blinks: {self.blink_counter}/3", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Update verification stages
            if current_instruction == 0 and self.blink_counter >= 3:
                current_instruction = 1
            elif current_instruction == 1 and self.gesture_verified:
                current_instruction = 2
                time.sleep(1)
                current_instruction = 3
                filepath = self.capture_face(frame)
                print(f"Face captured and saved to: {filepath}")
                verification_complete = True
            
            cv2.imshow('Liveness Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if time.time() - start_time > 30:
                print("Verification timeout")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return verification_complete

# Example usage
if __name__ == "__main__":
    detector = LivenessDetector()
    if detector.start_verification():
        print("Verification successful!")
    else:
        print("Verification failed or timed out")