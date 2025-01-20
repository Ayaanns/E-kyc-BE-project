import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox
import threading
import time

class NameRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Name Recognition")
        self.root.geometry("400x300")
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Create GUI elements
        self.setup_gui()
        
        # Flag for recording state
        self.is_recording = False
        
    def setup_gui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame, 
            text="Press 'Start Recording' and say your name",
            wraplength=350
        )
        self.status_label.pack(pady=10)
        
        # Recording button
        self.record_button = tk.Button(
            self.main_frame,
            text="Start Recording",
            command=self.toggle_recording,
            width=15
        )
        self.record_button.pack(pady=10)
        
        # Name display frame
        self.name_frame = tk.Frame(self.main_frame)
        self.name_frame.pack(pady=20)
        
        # Name label
        self.name_label = tk.Label(self.name_frame, text="Recognized Name:")
        self.name_label.pack()
        
        # Name entry for editing
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            self.name_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(pady=5)
        
        # Edit button
        self.edit_button = tk.Button(
            self.name_frame,
            text="Save Edit",
            command=self.save_edit,
            width=10
        )
        self.edit_button.pack(pady=5)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Recording... Speak your name")
            
            # Start recording in a separate thread
            threading.Thread(target=self.record_audio, daemon=True).start()
        else:
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.status_label.config(text="Recording stopped")
    
    def record_audio(self):
        while self.is_recording:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        self.root.after(0, self.update_name, text)
                    except sr.UnknownValueError:
                        self.root.after(0, self.status_label.config, 
                                      {"text": "Could not understand audio"})
                    except sr.RequestError:
                        self.root.after(0, self.status_label.config,
                                      {"text": "Could not request results"})
                        
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Error", str(e))
                break
    
    def update_name(self, name):
        self.name_var.set(name)
        self.status_label.config(text=f"Recognized name: {name}")
    
    def save_edit(self):
        edited_name = self.name_var.get()
        self.status_label.config(text=f"Name updated to: {edited_name}")
        messagebox.showinfo("Success", f"Name saved: {edited_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NameRecognitionApp(root)
    root.mainloop()