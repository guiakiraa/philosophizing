import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv
from src.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


def _init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
        if os.path.exists(cred_path):
            logger.info(f"Inicializando Firebase com credencial: {cred_path}")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            logger.info("Inicializando Firebase com Application Default Credentials")
            firebase_admin.initialize_app()
        logger.info("Firebase inicializado com sucesso")
    return firestore.client(database_id='philosopher-agent')


def get_sent_themes() -> list[str]:
    logger.info("Buscando temas já enviados no Firestore...")
    db = _init_firebase()
    docs = db.collection("sent_themes").stream()
    themes = [doc.to_dict().get("theme", "") for doc in docs]
    logger.info(f"{len(themes)} tema(s) encontrado(s) no histórico")
    return themes


def save_theme(theme: str, content: dict) -> None:
    logger.info(f"Salvando tema no Firestore: '{theme}'")
    db = _init_firebase()
    db.collection("sent_themes").add({
        "theme": theme,
        "phrase": content.get("phrase", ""),
        "context": content.get("context", ""),
        "question": content.get("question", ""),
        "sent_at": datetime.now().isoformat()
    })
    logger.info("Tema salvo com sucesso!")