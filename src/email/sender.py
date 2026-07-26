import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
from dotenv import load_dotenv
from src.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


def _build_html(content: dict) -> str:
    date = datetime.now().strftime("%d/%m/%Y")
    return f"""
    <html>
      <body style="font-family: Georgia, serif; max-width: 600px; margin: auto; padding: 20px; color: #2c2c2c;">

        <h2 style="text-align: center; color: #4a4a4a; letter-spacing: 1px;">
          💭 Reflexão do dia — {date}
        </h2>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <h3 style="color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 2px;">
          💬 Frase do dia
        </h3>
        <blockquote style="font-size: 18px; font-style: italic; color: #2c2c2c;
                           border-left: 4px solid #aaa; padding-left: 16px; margin: 12px 0;">
          {content['phrase']}
        </blockquote>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <h3 style="color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 2px;">
          📖 Contexto
        </h3>
        <p style="font-size: 15px; line-height: 1.8; color: #3c3c3c;">
          {content['context']}
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <h3 style="color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 2px;">
          ❓ Pergunta para refletir
        </h3>
        <p style="font-size: 16px; font-style: italic; font-weight: bold; color: #2c2c2c;">
          {content['question']}
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <p style="text-align: center; font-size: 12px; color: #aaa;">
          Aporia · uma pergunta nova todo dia
        </p>

      </body>
    </html>
    """


def send_email(content: dict) -> None:
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    date = datetime.now().strftime("%d/%m/%Y")

    if not all([gmail_user, gmail_password, to_email]):
        raise ValueError("Variáveis de ambiente GMAIL_USER, GMAIL_APP_PASSWORD e TO_EMAIL são obrigatórias.")

    logger.info(f"Preparando email para: {to_email}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"💭 Reflexão do dia — {date}"
    msg["From"] = gmail_user
    msg["To"] = to_email

    html = _build_html(content)
    msg.attach(MIMEText(html, "html"))

    logger.info("Conectando ao servidor SMTP do Gmail...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.sendmail(gmail_user, to_email, msg.as_string())

    logger.info("Email enviado com sucesso!")