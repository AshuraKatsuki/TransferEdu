import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mistralai import Mistral

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
            include_image_base64=True,
        )

        output_path = os.path.join(output_dir, 'output.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in response.pages:
                f.write(page.markdown)
                # Export images if needed
                # for image in page.images:
                #     self._export_image(image, output_dir)
        
        return output_path

    def _data_uri_to_bytes(self, data_uri):
        _, encoded = data_uri.split(',', 1)
        return base64.b64decode(encoded)

    # def _export_image(self, image, output_dir):
    #     parsed_image = self._data_uri_to_bytes(image.image_base64)
    #     image_path = os.path.join(output_dir, image.id)
    #     with open(image_path, 'wb') as f:
    #         f.write(parsed_image)

class LLMModel:
    """
    Large Language Model Using Gemini API
    """
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def summarize_document(self, file_path):
        #Prompt from txt file
        prompt_file = "TransferEdu/txt_file/prompt_instruction.txt"
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

class Workflow:
    """
    Processing.
    """
    def __init__(self, mistral_key, gemini_key):
        self.ocr_processor = OCRProcessor(api_key=mistral_key)
        self.llm_summarizer = LLMModel(api_key=gemini_key)

    def run_workflow(self, input_file_path):
        print(input_pdf_file)
        print("Start Processing...")
        file_id = self.ocr_processor.upload_document(input_file_path)
        file_url = self.ocr_processor.get_signed_url(file_id)
        output_file = self.ocr_processor.process_ocr(file_url)
        print("End Process.")
        self.output_saving(output_file)

    def output_saving(self, output_file, filename="output.md"):
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
    
    # Run Process
    workflow = Workflow(mistral_key=mistral_api_key, gemini_key=gemini_api_key)
    workflow.run_workflow(input_pdf_file)