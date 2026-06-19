import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mistralai import Mistral
import pyttsx3 as ts

base_dir = os.path.dirname(os.path.abspath(__file__))
class OCRProcessor:
    """
    Using Mistral AI for OCR
    """
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)

    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            uploaded_file = self.client.files.upload(
                file={
                    'file_name': os.path.basename(file_path),
                    'content': f
                },
                purpose='ocr'
            )
        return uploaded_file.id

    def get_signed_url(self, file_id):
        file_url = self.client.files.get_signed_url(file_id=file_id)
        return file_url.url

    def process_ocr(self, file_url, output_dir='.'):
        response = self.client.ocr.process(
            model='mistral-ocr-latest',
            document={
                'type': 'document_url',
                'document_url': file_url
            },
            
        )

        output_path = os.path.join(output_dir, 'output.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in response.pages:
                f.write(page.markdown)
        
        return output_path

    def _data_uri_to_bytes(self, data_uri):
        _, encoded = data_uri.split(',', 1)
        return base64.b64decode(encoded)


class LLMModel:
    """
    Large Language Model Using Gemini API
    """
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def summarize_document(self, file_path):
        # Prompt from txt file
        prompt_file = os.path.join(base_dir, 'txt_file', 'prompt_instruction.txt')
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Error: Prompt file not found at {prompt_file}")

        #In case prompt not exist
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_instruction = f.read()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Error: Not Found {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            document_content = f.read()

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_instruction),
                    types.Part.from_text(text=document_content),
                ],
            ),
        ]

        # Use streaming to print content as it's generated
        full_response = ""
        print("Summarizing...")
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
        ):
            if chunk.text:
                # print(chunk.text, end="")   #  Print out the result
                full_response += chunk.text # Adding content to variable
        return full_response

class TextandAudio:
    def __init__(self):
        self.engine = ts.init()

    def text_to_speech(self, text):
        file_path = os.path.join(base_dir, "output.md")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            clean_text = text.replace("#", "").replace("*", "")
            self.engine.say(content)
            self.engine.runAndWait()
        

class Workflow:
    """
    Processing.
    """
    def __init__(self, mistral_key, gemini_key):
        self.ocr_processor = OCRProcessor(api_key=mistral_key)
        self.llm_summarizer = LLMModel(api_key=gemini_key)
        self.audio = TextandAudio()

    def run_workflow(self, input_file_path):
        print("Getting file from:", input_pdf_file)
        # Run OCR and save into output.md
        print("Start Processing...")
        file_id = self.ocr_processor.upload_document(input_file_path)
        file_url = self.ocr_processor.get_signed_url(file_id)
        output_file = self.ocr_processor.process_ocr(file_url)
        print("End Process.")
        self.llm_processing(output_file)
        self.audio.text_to_speech(output_file)
        

    def llm_processing(self, output_file, filename="output.md"):
        output_path = os.path.join(base_dir, filename)
        summary_result = self.llm_summarizer.summarize_document(output_file)

        # Saving to md file
        if summary_result:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary_result)
                print(f"Saved at {output_path}")
        
        else:
            print("Error. AI not return. Cannot saved")
    
if __name__ == '__main__':
    # Load env
    load_dotenv()
    # API keys
    mistral_api_key = os.getenv('MISTRAL_AI_API') 
    gemini_api_key = os.getenv('GEMINI_API')
    input_pdf_file = os.path.join(base_dir, 'pdf_file', 'module01.pdf')
    print(input_pdf_file)
    
    # Run Process
    workflow = Workflow(mistral_key=mistral_api_key, gemini_key=gemini_api_key)
    workflow.run_workflow(input_pdf_file)
# By Ashura