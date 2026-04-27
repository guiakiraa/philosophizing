import json
from openai import OpenAI
from src.agent.prompts import SYSTEM_PROMPT, USER_PROMPT
from src.database.firestore import get_sent_themes, save_theme
from src.logger import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)
client = OpenAI()

def _call_llm(themes_text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(sent_themes=themes_text)}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "reflection",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "theme": {
                            "type": "string",
                            "description": "Tema curto em até 5 palavras"
                        },
                        "phrase": {
                            "type": "string",
                            "description": "Frase ou situação provocativa"
                        },
                        "context": {
                            "type": "string",
                            "description": "Contexto filosófico em 3 a 5 linhas"
                        },
                        "question": {
                            "type": "string",
                            "description": "Uma pergunta profunda para reflexão"
                        }
                    },
                    "required": ["theme", "phrase", "context", "question"],
                    "additionalProperties": False
                }
            }
        }
    )
    return json.loads(response.choices[0].message.content)

def generate_reflection() -> dict:
    logger.info("Iniciando geração de reflexão...")

    sent_themes = get_sent_themes()

    if sent_themes:
        themes_text = "\n".join(f"- {t}" for t in sent_themes)
        logger.info(f"{len(sent_themes)} tema(s) no histórico")
    else:
        themes_text = "Nenhum tema enviado ainda — esse é o primeiro!"
        logger.info("Nenhum tema no histórico — primeira execução")

    logger.info("Chamando GPT-4o para gerar reflexão...")
    content = _call_llm(themes_text)
    logger.info(f"Reflexão gerada com tema: '{content['theme']}'")

    save_theme(theme=content["theme"], content=content)

    return content