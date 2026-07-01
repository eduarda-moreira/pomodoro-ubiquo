"""Protótipo 2 — Servidor local (Flask).

Encapsula o núcleo do timer (src/timer.py) numa API HTTP acessível na rede
Wi-Fi, permitindo que o smartwatch e outros dispositivos consultem o estado e
controlem a sessão (iniciar / pausar / retomar / encerrar).

Um thread em segundo plano avança a máquina de estados (`atualizar`) para que
as transições foco↔pausa aconteçam automaticamente, mesmo sem requisições.

Uso:
    ./venv/bin/python src/server.py

Endpoints:
    GET  /estado    → estado atual (situação, período, tempo restante, focos)
    POST /iniciar   → inicia a sessão
    POST /pausar    → pausa o período atual
    POST /retomar   → retoma o período pausado
    POST /encerrar  → encerra a sessão
"""
from __future__ import annotations

import threading
import time

from flask import Flask, jsonify

from config import carregar_config
from timer import MENSAGENS, PomodoroTimer

INTERVALO_TICK_SEG = 0.5

cfg = carregar_config()
app = Flask(__name__)

# Trava para serializar acesso ao timer entre o ticker e as requisições HTTP.
_lock = threading.Lock()


def anunciar(_anterior: str, proximo: str) -> None:
    # Gancho para os avisos de voz (Fase 3) e vibração (Fase 4).
    print(f">>> {MENSAGENS[proximo]}")


timer = PomodoroTimer(cfg, ao_transicionar=anunciar)


def _ticker() -> None:
    """Avança a máquina de estados periodicamente (transições automáticas)."""
    while True:
        with _lock:
            timer.atualizar()
        time.sleep(INTERVALO_TICK_SEG)


@app.get("/estado")
def get_estado():
    with _lock:
        return jsonify(timer.estado())


@app.post("/iniciar")
def post_iniciar():
    with _lock:
        timer.iniciar()
        return jsonify(timer.estado())


@app.post("/pausar")
def post_pausar():
    with _lock:
        timer.pausar()
        return jsonify(timer.estado())


@app.post("/retomar")
def post_retomar():
    with _lock:
        timer.retomar()
        return jsonify(timer.estado())


@app.post("/encerrar")
def post_encerrar():
    with _lock:
        timer.encerrar()
        return jsonify(timer.estado())


def main() -> None:
    servidor = cfg["servidor"]
    # O ticker roda em daemon para as transições ocorrerem sem requisições.
    threading.Thread(target=_ticker, daemon=True).start()
    print(
        f"Servidor Pomodoro em http://{servidor['ip_notebook']}:{servidor['porta']} "
        f"(bind {servidor['host']})"
    )
    # use_reloader=False evita iniciar dois tickers (o reloader duplica o processo).
    app.run(host=servidor["host"], port=servidor["porta"], use_reloader=False)


if __name__ == "__main__":
    main()
