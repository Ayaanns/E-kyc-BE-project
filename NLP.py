import cv2
import speech_recognition as sr
import threading
import time

class UserInfo:
    def __init__(self):
        self.name = "Waiting for name..."
        self.age = "Waiting for age..."

def process_camera(stop_event, user_info):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_color = (255, 255, 255)  # White color
    thickness = 2

    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            # Add black background for text
            cv2.rectangle(frame, (10, 30), (300, 80), (0, 0, 0), -1)
            
            # Add text to frame
            cv2.putText(frame, f"Name: {user_info.name}", (20, 50), font, 
                        font_scale, font_color, thickness)
            cv2.putText(frame, f"Age: {user_info.age}", (20, 70), font, 
                        font_scale, font_color, thickness)
            
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break

    cap.release()
    cv2.destroyAllWindows()

def get_speech_input(prompt):
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print(prompt)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                return text.strip()
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
        except sr.RequestError:
            print("Could not request results. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")

def get_user_info(stop_event, user_info):
    try:
        # Get name
        name = get_speech_input("Please say your name:")
        user_info.name = name
        print(f"Recorded name: {name}")
        
        # Get age
        age = get_speech_input("Please say your age:")
        user_info.age = age
        print(f"Recorded age: {age}")
        
        print("\nPress 'q' to quit...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        stop_event.set()

def main():
    stop_event = threading.Event()
    user_info = UserInfo()
    
    # Start camera thread
    camera_thread = threading.Thread(target=process_camera, args=(stop_event, user_info))
    camera_thread.start()
    
    # Start user info thread
    info_thread = threading.Thread(target=get_user_info, args=(stop_event, user_info))
    info_thread.start()

    try:
        camera_thread.join()
        info_thread.join()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        stop_event.set()
        print("\nProgram terminated")

if __name__ == "__main__":
    main()