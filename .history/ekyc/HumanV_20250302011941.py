import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time
import os

class HumanVerificationSystem:
    def __init__(self):
        # Previous initialization code remains the same
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            refine_landmarks=True
        )
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Core landmarks for eye height measurement
        self.LEFT_EYE_TOP = 386
        self.LEFT_EYE_BOTTOM = 374
        self.RIGHT_EYE_TOP = 159
        self.RIGHT_EYE_BOTTOM = 145

        # State management
        self.blink_counter = 0
        self.blink_timestamps = []
        self.eye_heights = deque(maxlen=5)
        self.baseline_height = None
        self.blinks_verified = False
        self.wave_count = 0
        
        # Wave detection parameters
        self.hand_positions = deque(maxlen=10)
        self.wave_start_time = None
        self.wave_in_progress = False
        self.start_position = None
        self.max_position = None
        
        # State flags
        self.wave_phase_complete = False
        self.current_phase = "wave"
        self.showing_excellent = False
        self.excellent_start_time = None
        
        # Prompt states
        self.show_wave_prompt = True
        self.show_blink_prompt = True
        self.last_blink_time = None
        
        # UI settings
        self.TEXT_COLOR = (0, 255, 0)
        
        # New photo capture states
        self.photo_prompt_shown = False
        self.countdown_start = None
        self.countdown_duration = 5

        # Prompt duration
        self.prompt_start_time = None
        self.prompt_duration = 120  # 2 minutes

    # Previous methods remain the same
    def get_eye_height(self, landmarks, top_idx, bottom_idx):
        top = landmarks[top_idx]
        bottom = landmarks[bottom_idx]
        return np.sqrt((top.x - bottom.x)**2 + (top.y - bottom.y)**2)

    def detect_blink(self, frame):
        if not self.wave_phase_complete or self.showing_excellent:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:
            return

        landmarks = results.multi_face_landmarks[0].landmark
        
        left_height = self.get_eye_height(landmarks, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM)
        right_height = self.get_eye_height(landmarks, self.RIGHT_EYE_TOP, self.RIGHT_EYE_BOTTOM)
        current_height = (left_height + right_height) / 2
        
        if self.baseline_height is None and len(self.eye_heights) == 5:
            self.baseline_height = np.mean(self.eye_heights)
            
        self.eye_heights.append(current_height)

        if self.baseline_height is not None:
            height_ratio = current_height / self.baseline_height

            if len(self.blink_timestamps) == 0 or \
               (time.time() - self.blink_timestamps[-1] >= 0.4):
                
                if height_ratio < 0.6:
                    if len(self.blink_timestamps) == 0 or \
                       time.time() - self.blink_timestamps[-1] >= 0.4:
                        self.blink_counter += 1
                        self.blink_timestamps.append(time.time())
                        self.show_blink_prompt = True
                        self.last_blink_time = time.time()
                        
                        if self.blink_counter >= 3:
                            self.blinks_verified = True

    def detect_wave(self, frame):
        if self.wave_phase_complete or self.showing_excellent:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if not results.multi_hand_landmarks:
            if self.show_wave_prompt:
                print("Please wave your hand")
            self.wave_start_time = None
            self.wave_in_progress = False
            self.start_position = None
            self.max_position = None
            return
            
        hand_landmarks = results.multi_hand_landmarks[0].landmark
        current_position = hand_landmarks[0].x
        self.hand_positions.append(current_position)
        
        if not self.wave_in_progress:
            self.wave_start_time = time.time()
            self.wave_in_progress = True
            self.start_position = current_position
            self.max_position = current_position
        else:
            self.max_position = max(self.max_position, current_position)
            
            if time.time() - self.wave_start_time <= 1.5:
                if self.max_position - self.start_position > 0.3:
                    self.wave_count += 1
                    self.wave_in_progress = False
                    self.show_wave_prompt = True
                    
                    if self.wave_count >= 2:
                        self.wave_phase_complete = True
                        self.showing_excellent = True
                        self.excellent_start_time = time.time()
            else:
                self.wave_in_progress = False
                self.start_position = None
                self.max_position = None

    def save_photo(self, frame):
        # Create 'captured_photos' directory if it doesn't exist
        if not os.path.exists('captured_photos'):
            os.makedirs('captured_photos')
            
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f'captured_photos/photo_{timestamp}.jpg'
        
        # Save the image
        cv2.imwrite(filename, frame)
        print(f"Photo saved as {filename}")

    def verify_human(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False

        print("Instructions:")
        print("1. Wave your hand from left to right twice")
        print("2. Blink three times when prompted")
        print("3. Move to a clear background for photo capture")
        print("4. Press ESC to exit")

        self.prompt_start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            
            if self.showing_excellent:
                if time.time() - self.excellent_start_time <= 3.0:
                    print("Excellent!")
                else:
                    self.showing_excellent = False
                    self.current_phase = "blink"
                    self.prompt_start_time = time.time()
            else:
                self.detect_wave(frame)
                self.detect_blink(frame)
            
                if self.current_phase == "wave":
                    print(f"Waves completed: {self.wave_count}/2")
                    
                    if self.wave_count > 0 and self.wave_count < 2 and self.show_wave_prompt:
                        print("Please wave your hand")
                else:
                    print(f"Blinks detected: {self.blink_counter}/3")
                    
                    if not self.blinks_verified:
                        print("Please blink your eye")

            if self.blinks_verified and self.wave_phase_complete:
                if not self.photo_prompt_shown:
                    print("Kindly move to a clear background for photo capture")
                    print("Press SPACE when ready")
                    self.photo_prompt_shown = True
                
                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # SPACE key
                    if self.countdown_start is None:
                        self.countdown_start = time.time()
                    
                    remaining_time = int(self.countdown_duration - (time.time() - self.countdown_start))
                    
                    if remaining_time > 0:
                        print(f"Photo in {remaining_time}...")
                    else:
                        # Capture and save photo
                        self.save_photo(frame)
                        print("Photo captured!")
                        break
            
            # Check if the prompt duration has exceeded
            if time.time() - self.prompt_start_time > self.prompt_duration:
                print("KYC process failed due to timeout.")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return self.blinks_verified and self.wave_phase_complete

def main():
    verifier = HumanVerificationSystem()
    result = verifier.verify_human()
    if result:
        print("Human verification successful!")
    else:
        print("Human verification failed or interrupted.")

if __name__ == "__main__":
    main()