import functions_framework
from src.agent.agent import generate_reflection
from src.email.sender import send_email
from src.logger import get_logger

logger = get_logger(__name__)


@functions_framework.http
def run(request):
    logger.info("========== Philosopher Agent iniciado ==========")

    try:
        logger.info("Gerando reflexão...")
        content = generate_reflection()

        logger.info("Enviando email...")
        send_email(content)

        logger.info("========== Philosopher Agent finalizado com sucesso ==========")
        return {"status": "success", "theme": content["theme"]}, 200

    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        return {"status": "error", "message": str(e)}, 500