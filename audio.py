import pyttsx3 as ts
import os
import base64

base_dir = os.path.dirname(os.path.abspath(__file__))
def text_to_speech():
    engine = ts.init()
    file_path = os.path.join(base_dir, "output.md")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        print("Processing...")
        engine.say(content)
        engine.runAndWait()
    
    else: 
        print("Error. Cannot read!")

if __name__ == "__main__":
    text_to_speech()