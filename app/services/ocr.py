import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables, but we will use a local directory for uploads
load_dotenv()

# Use a local 'uploads' directory to avoid permission issues.
# This overrides any UPLOAD_DIRECTORY value from the .env file.
UPLOAD_DIRECTORY = "uploads"

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using OCR.
    """
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return ""

def save_uploaded_file(upload_file) -> str:
    """
    Saves an uploaded file to the UPLOAD_DIRECTORY.
    """
    # Ensure the directory exists
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIRECTORY, upload_file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path
