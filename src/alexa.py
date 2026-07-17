"""
INTEGRAÇÃO VOICE MONKEY (Alexa)

Utiliza a API de Anúncio do Voice Monkey v3 para pedir a um Speaker (vinculado a uma Rotina no app Alexa) que fala um texto dinâmico a cada chamada.

Endpoint: POST https://api-v3.voicemonkey.io/announce
Body:     {"token": ..., "device": ..., "speech": ...}
Success:  HTTP 200 {"success": true, "data": "OK"}
"""

from __future__ import annotations
import requests
from config import load_config


URL_ANNOUNCE = "https://api-v3.voicemonkey.io/announce"
TIMEOUT_SEC = 5


def announce_voice(text: str) -> bool:
    """
    Fala da Alexa coo texto fornecido via API do Voice Monkey.
    Retorna True em caso de sucesso, False caso contrário.
    """
    try:
        alexa_cfg = load_config()["alexa"]
        body = {
            "token": alexa_cfg["token"],
            "device": alexa_cfg["device"],
            "speech": text,
            "voice": alexa_cfg["voice"],
            "language": alexa_cfg["language"],
        }
    except KeyError as error:
        print(f"[Alexa] Configuração ausente: {error}")
        return False

    try:
        response = requests.post(URL_ANNOUNCE, json=body, timeout=TIMEOUT_SEC)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as error:
        print(f"[Alexa] Erro HTTP {response.status_code} do Voice Monkey: {error}")
        return False
    except requests.RequestException as error:
        print(f"[Alexa] Falha de rede/timeout ao contatar o Voice Monkey: {error}")
        return False
    except ValueError as error:
        print(f"[Alexa] Resposta inválida (não-JSON) do Voice Monkey: {error}")
        return False

    success = bool(data.get("success"))
    if not success:
        print(f"[Alexa] Voice Monkey retornou falha: {data}")
    return success
