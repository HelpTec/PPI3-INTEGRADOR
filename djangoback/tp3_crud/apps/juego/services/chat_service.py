import os
import logging
from google import genai

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Eres un asistente virtual de una página web sobre videojuegos llamada GameBase. "
    "Responde de forma amistosa, útil y concisa al siguiente mensaje del usuario:\n\n"
    "Usuario: {message}"
)


def get_chat_reply(message: str) -> str:
    """
    Send a user message to Gemini and return the reply text.
    Raises ValueError('empty_message') or ValueError('missing_api_key') on bad config.
    """
    if not message or not message.strip():
        raise ValueError('empty_message')
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or api_key == 'TU_CLAVE_DE_GEMINI_AQUI':
        raise ValueError('missing_api_key')
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=_SYSTEM_PROMPT.format(message=message),
    )
    return response.text
