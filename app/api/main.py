from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorsiMaster
from app.services import ocr, ai_extraction
from datetime import datetime
from dateutil.relativedelta import relativedelta

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db)):
    return db.query(CorsiMaster).all()

@router.get("/health")
def health_check():
    return {"status": "ok"}

def calculate_expiration_date(extracted_data: dict, db: Session) -> dict:
    """
    Applica la logica di business per calcolare la data di scadenza.
    """
    # Adatta i dati estratti allo schema interno
    entities = {
        "nome": extracted_data.get("nome"),
        "corso": extracted_data.get("corso"),
        "data_rilascio": None,
        "data_scadenza": None
    }

    data_rilascio_str = extracted_data.get("data_rilascio")

    # 1. Parsing della data
    if data_rilascio_str:
        try:
            # Gemini dovrebbe restituire DD-MM-YYYY, facciamo il parsing
            parsed_date = datetime.strptime(data_rilascio_str, '%d-%m-%Y').date()
            entities["data_rilascio"] = parsed_date
        except (ValueError, TypeError):
            entities["data_rilascio"] = None

    # 2. Logica di Business (Calcolo Scadenza)
    if entities["corso"] and entities["data_rilascio"]:
        corsi = db.query(CorsiMaster).all()
        course_names = {corso.nome_corso.lower(): corso for corso in corsi}
        extracted_course_lower = entities["corso"].lower()

        for course_name, corso_obj in course_names.items():
            if course_name in extracted_course_lower:
                if corso_obj.validita_mesi > 0:
                    expiration_date = entities["data_rilascio"] + relativedelta(months=corso_obj.validita_mesi)
                    entities["data_scadenza"] = expiration_date
                break

    # 3. Formatta le date come stringhe YYYY-MM-DD prima di restituirle
    if entities.get("data_rilascio"):
        entities["data_rilascio"] = entities["data_rilascio"].strftime('%Y-%m-%d')
    if entities.get("data_scadenza"):
        entities["data_scadenza"] = entities["data_scadenza"].strftime('%Y-%m-%d')

    return entities


@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = ocr.save_uploaded_file(file)
    text = ocr.extract_text_from_pdf(file_path)

    # Chiama il servizio AI (ora basato su Gemini)
    extracted_data = ai_extraction.extract_entities_with_ai(text)

    if "error" in extracted_data:
        return {"filename": file.filename, "text": text, "entities": {}, "error": extracted_data["error"]}

    # Applica la logica di business e formatta i dati
    final_entities = calculate_expiration_date(extracted_data, db)

    return {"filename": file.filename, "text": text, "entities": final_entities}
