import cv2
import speech_recognition as sr
import threading
import time

def process_camera(stop_event):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
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
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                return text
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
        except sr.RequestError:
            print("Could not request results. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")

def main():
    # Create a stop event for camera thread
    stop_event = threading.Event()
    
    # Start camera thread
    camera_thread = threading.Thread(target=process_camera, args=(stop_event,))
    camera_thread.start()

    print("Camera is running. Please respond to the prompts...")
    
    # Get user information while camera is running
    try:
        name = get_speech_input("Please say your name:")
        print(f"Recorded name: {name}")
        
        age = get_speech_input("Please say your age:")
        print(f"Recorded age: {age}")
        
        print("\nPress 'q' to quit and display final information...")
        
        # Wait for user to press 'q'
        while not stop_event.is_set():
            time.sleep(0.1)

        # Display final information
        print("\n--- User Information ---")
        print(f"Name: {name}")
        print(f"Age: {age}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure camera thread stops
        stop_event.set()
        camera_thread.join()

if __name__ == "__main__":
    main()