import speech_recognition as sr

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    
    print("Speech to Text CLI")
    print("Press Ctrl+C to exit")
    print("-" * 20)
    
    while True:
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source)
                
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"Text: {text}")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    listen_and_transcribe() 