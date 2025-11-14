import logging
from app.db.session import engine
from app.db.models import Base

logging.basicConfig(level=logging.INFO)

def init_db():
    logging.info("Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
