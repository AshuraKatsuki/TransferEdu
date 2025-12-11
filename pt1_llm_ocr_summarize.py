import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mistralai import Mistral

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
            include_image_base64=True,
        )

        output_path = os.path.join(output_dir, 'output.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in response.pages:
                f.write(page.markdown)
                # Export images if needed
                for image in page.images:
                    self._export_image(image, output_dir)
        
        return output_path

    def _data_uri_to_bytes(self, data_uri):
        _, encoded = data_uri.split(',', 1)
        return base64.b64decode(encoded)

    def _export_image(self, image, output_dir):
        parsed_image = self._data_uri_to_bytes(image.image_base64)
        image_path = os.path.join(output_dir, image.id)
        with open(image_path, 'wb') as f:
            f.write(parsed_image)

class LLMModel:
    """
    Large Language Model Using Gemini API
    """
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def summarize_document(self, file_path, prompt_instruction="tóm tắt văn bản"):
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
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
        ):
            print(chunk.text, end="")

class Workflow:
    """
    Processing.
    """
    def __init__(self, mistral_key, gemini_key):
        self.ocr_processor = OCRProcessor(api_key=mistral_key)
        self.llm_summarizer = LLMModel(api_key=gemini_key)

    def run_workflow(self, input_file_path):
        print("Start Processing...")
        file_id = self.ocr_processor.upload_document(input_file_path)
        file_url = self.ocr_processor.get_signed_url(file_id)
        output_file = self.ocr_processor.process_ocr(file_url)
        print("End Process.")
        
        self.llm_summarizer.summarize_document(output_file)

if __name__ == '__main__':
    # Load env
    load_dotenv()
    
    # API keys
    mistral_api_key = '8gKDvv9jlEsUsNDce70tXPLhO6f01Ehr' 
    gemini_api_key = 'AIzaSyAQe-j4N3eJGe6fUxR6rX5_A8dUULtzZuo'
    input_pdf_file = 'U1170655.pdf'
    
    # Run Process
    workflow = Workflow(mistral_key=mistral_api_key, gemini_key=gemini_api_key)
    workflow.run_workflow(input_pdf_file)