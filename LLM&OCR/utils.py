import pandas as pd
from dotenv import load_dotenv
import json
from google import genai
from google.genai import types
import time
import os 
import numpy as np
import fitz  # PyMuPDF
from pathlib import Path
from mistralai import Mistral
import json 

load_dotenv()

def mistral_ocr_response(pdf_file, model_name):
    client = Mistral(api_key = os.getenv("mistral_api"))
    pdf_file = Path(pdf_file)
    # Upload PDF file to Mistral's OCR service
    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_file.stem,
            "content": pdf_file.read_bytes(),
        },
        purpose="ocr",
    )
    file_url = client.files.get_signed_url(file_id = uploaded_file.id)
    response = client.ocr.process(
        model = model_name,
        document = { 
            'type': 'document_url',
            'document_url': file_url.url
        },
        include_image_base64 = True,
    )
    return json.loads(response.model_dump_json())

def LLM_extraction(prompt, file_path, model = "gemini-2.5-pro"):
    start_time = time.time()
    client = genai.Client(
        api_key=os.getenv("gemini_api"),
    )

    files = [
        # Please ensure that the file is available in local system working direrctory or change the file path.
        client.files.upload(file=file_path),
    ]

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text=prompt),
                
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
                thinking_budget=8000,),
        temperature=0,
        top_p=0.95,
        top_k=40,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",  # Block none
            ),
        ],
        response_mime_type="text/plain",
    )

    response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
    end_time = time.time()
    print("token in extracting content")
    print('candidates_token_count:', response.usage_metadata.candidates_token_count)
    print("Thoughts tokens:",response.usage_metadata.thoughts_token_count)
    print('prompt_token_count:', response.usage_metadata.prompt_token_count)
    print('total_token_count:', response.usage_metadata.total_token_count)
    #cost_of_output_tokens = (int(response.usage_metadata.candidates_token_count) + int(response.usage_metadata.thoughts_token_count)) * 10 / 1000000
    #print('Cost of output tokens:', cost_of_output_tokens)
    #cost_of_input_tokens = int(response.usage_metadata.prompt_token_count) * 1.25 / 1000000
    #print("Cost of input tokens:", cost_of_input_tokens)
    #print(f"Total cost for this request: {cost_of_output_tokens + cost_of_input_tokens} USD")
    print(f"Time taken for LLM extraction: {end_time - start_time} seconds")
    #print(response.text.replace("```json", "").replace("```", "").replace("NONE", "null").replace("None", "null").replace("none", "null").replace(", \"null\"", ": \"null\"").replace(':"',''))
    return response.text.replace("```json", "").replace("```", "")


def helloworld(name):
    print("hello", name)