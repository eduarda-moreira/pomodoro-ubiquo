"""Carregamento da configuração do Pomodoro Ubíquo.

Lê os parâmetros de `config.json` (na raiz do projeto) e substitui os
placeholders `${VAR}` pelos valores do ambiente, carregados do arquivo `.env`
(não versionado). Assim, dados específicos da máquina/rede e segredos (IP do
notebook, porta, tokens) ficam fora do `config.json` versionado.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from string import Template

from dotenv import load_dotenv

# Raiz do projeto = pasta pai de /src
RAIZ = Path(__file__).resolve().parent.parent

# Campos que devem ser convertidos para inteiro após a substituição
_CAMPOS_INTEIROS = {("servidor", "porta")}


def _converter_inteiros(config: dict) -> None:
    """Converte campos numéricos que vieram como texto do `.env`."""
    for secao, chave in _CAMPOS_INTEIROS:
        valor = config.get(secao, {}).get(chave)
        if isinstance(valor, str) and valor.strip():
            config[secao][chave] = int(valor)


def carregar_config() -> dict:
    """Retorna a configuração com os placeholders `${VAR}` já resolvidos."""
    load_dotenv(RAIZ / ".env")

    texto = (RAIZ / "config.json").read_text(encoding="utf-8")
    # `safe_substitute` mantém intactos placeholders sem variável definida
    texto = Template(texto).safe_substitute(os.environ)

    config = json.loads(texto)
    _converter_inteiros(config)
    return config


if __name__ == "__main__":
    cfg = carregar_config()
    print("Configuração carregada com sucesso:")
    print(f"  Servidor: {cfg['servidor']['host']}:{cfg['servidor']['porta']}")
    print(f"  Tempos:   {cfg['tempos']}")
