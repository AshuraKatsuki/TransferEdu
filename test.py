from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from mistralai import Mistral
from dotenv import load_dotenv
import io

load_dotenv()

app = FastAPI()

# Chỉ cần thư mục để lưu kết quả đầu ra
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class OCRProcessor:
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)

    async def process_and_save_only_md(self, file: UploadFile):
        # 1. Đọc nội dung file PDF vào bộ nhớ (không lưu xuống ổ cứng)
        pdf_content = await file.read()
        
        # 2. Upload trực tiếp từ bộ nhớ lên Mistral
        # Chúng ta bọc bytes vào io.BytesIO để giả lập một đối tượng file
        uploaded_file = self.client.files.upload(
            file={
                'file_name': file.filename,
                'content': pdf_content
            },
            purpose='ocr'
        )
        
        # 3. Lấy Signed URL và chạy OCR
        file_url = self.client.files.get_signed_url(file_id=uploaded_file.id).url
        response = self.client.ocr.process(
            model='mistral-ocr-latest',
            document={'type': 'document_url', 'document_url': file_url}
        )
        
        # 4. Xác định tên file .md
        base_name = os.path.splitext(file.filename)[0]
        md_filename = f"{base_name}.md"
        md_path = os.path.join(OUTPUT_DIR, md_filename)
        
        # 5. Chỉ lưu file Markdown xuống server
        with open(md_path, 'w', encoding='utf-8') as f:
            for page in response.pages:
                f.write(page.markdown)
                f.write("\n\n---\n\n")
        
        return md_path

ocr_tool = OCRProcessor(api_key=os.getenv("MISTRAL_AI_API"))

@app.post("/ocr-to-markdown/")
async def ocr_to_md(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Vui lòng gửi file PDF.")

    try:
        # Xử lý hoàn toàn trong bộ nhớ và chỉ lưu file .md
        result_path = await ocr_tool.process_and_save_only_md(file)
        
        return {
            "message": "Chuyển đổi thành công!",
            "saved_file": result_path,
            "note": "File PDF gốc không được lưu lại trên server."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))