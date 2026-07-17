"""
CONFIG SETUP
Reads the parameters from `config.json` and substitutes the placeholders with
the values from the environment in `.env`.
"""

from __future__ import annotations
from pathlib import Path
from string import Template
from dotenv import load_dotenv
import json
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
_INTEGER_FIELDS = {("server", "port")}


def _convert_integers(config: dict) -> None:
    """
    Converts numeric fields that arrived as text.
    """
    for section, key in _INTEGER_FIELDS:
        value = config.get(section, {}).get(key)
        if isinstance(value, str) and value.strip():
            config[section][key] = int(value)


def load_config() -> dict:
    """
    Returns the configuration with the placeholders already resolved.
    """

    load_dotenv(ROOT_DIR / ".env")

    text = (ROOT_DIR / "config.json").read_text(encoding="utf-8")
    text = Template(text).safe_substitute(os.environ)

    config = json.loads(text)
    _convert_integers(config)
    return config


if __name__ == "__main__":
    cfg = load_config()
    print("Configuração carregada com sucesso:")
    print(f"  Servidor: {cfg['server']['host']}:{cfg['server']['port']}")
    print(f"  Tempos:   {cfg['timing']}")
