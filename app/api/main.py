from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorsiMaster
from app.services import ocr, entity_extraction

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db)):
    return db.query(CorsiMaster).all()

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = ocr.save_uploaded_file(file)
    text = ocr.extract_text_from_pdf(file_path)
    entities = entity_extraction.extract_entities(text, db)
    return {"filename": file.filename, "text": text, "entities": entities}
