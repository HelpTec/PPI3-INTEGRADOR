import os
import requests
import logging

logger = logging.getLogger(__name__)

DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


def translate_to_spanish(text):
    if not text or not text.strip():
        return text
    api_key = DEEPL_API_KEY or os.getenv('DEEPL_API_KEY')
    if not api_key:
        logger.warning("DEEPL_API_KEY not set, skipping translation")
        return text
    try:
        resp = requests.post(
            DEEPL_URL,
            headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
            json={"text": [text], "target_lang": "ES"},
            timeout=8,
        )
        resp.raise_for_status()
        return resp.json()["translations"][0]["text"]
    except Exception as e:
        logger.error("DeepL translation error: %s", e)
        return text
