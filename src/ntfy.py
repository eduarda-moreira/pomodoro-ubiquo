"""
INTEGRAÇÃO NTFY

POST de uma notificação de texto simples no tópico configurado (push.ntfy_topic_url).
Os apps ntfy inscritos no tópico (iPhone/Android) recebem a notificação e a espelham nativamente para o smartwatch pareado.

Endpoint: POST <ntfy_topic_url>  (ver https://docs.ntfy.sh/publish/)
"""

import requests
from __future__ import annotations
from config import load_config

TIMEOUT_SEC = 5


def notify(text: str) -> bool:
    """
    Publica `text` como notificação
    Retorna True em caso de sucesso, False caso contrário.
    """
    try:
        topic_url = load_config()["push"]["ntfy_topic_url"]
    except KeyError as error:
        print(f"[ntfy] Configuração ausente: {error}")
        return False

    try:
        response = requests.post(
            topic_url,
            data=text.encode("utf-8"),
            timeout=TIMEOUT_SEC,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"[ntfy] Erro HTTP {response.status_code} ao publicar: {error}")
        return False
    except requests.RequestException as error:
        print(f"[ntfy] Falha de rede/timeout ao contatar o ntfy: {error}")
        return False

    return True
