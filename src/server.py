"""
LOCAL SERVER (Flask)

Encapsula timer.py em uma API HTTP acessível na rede Wi-Fi, permitindo que outros dispositivos consultem o estado e controlem a sessão (iniciar / pausar / retomar / encerrar)

Endpoints:
    GET  /state   -> estado atual (status, period, remaining time, focuses)
    POST /start   -> começa a sessão
    POST /pause   -> pausa o periodo atual
    POST /resume  -> retoma o periodo pausado
    POST /stop    -> encerra a sessão
"""

from __future__ import annotations

import threading
import time
from typing import Optional

from flask import Flask, jsonify

from config import load_config
from timer import MESSAGES, PomodoroTimer

TICK_INTERVAL_SEC = 0.5

cfg = load_config()
app = Flask(__name__)

# Lock para proteger o acesso ao timer entre threads (Flask + ticker)
_lock = threading.Lock()


def announce(_previous: Optional[str], next_period: str) -> None:
    print(f">>> {MESSAGES[next_period]}")


timer = PomodoroTimer(cfg, on_transition=announce)


def _ticker() -> None:
    """Avança a máquina de estados"""
    while True:
        with _lock:
            timer.update()
        time.sleep(TICK_INTERVAL_SEC)


@app.get("/state")
def get_state():
    with _lock:
        return jsonify(timer.state())


@app.post("/start")
def post_start():
    with _lock:
        timer.start()
        return jsonify(timer.state())


@app.post("/pause")
def post_pause():
    with _lock:
        timer.pause()
        return jsonify(timer.state())


@app.post("/resume")
def post_resume():
    with _lock:
        timer.resume()
        return jsonify(timer.state())


@app.post("/stop")
def post_stop():
    with _lock:
        timer.stop()
        return jsonify(timer.state())


def main() -> None:
    server_cfg = cfg["server"]

    threading.Thread(target=_ticker, daemon=True).start()
    print(
        f"Servidor Pomodoro em http://{server_cfg['notebook_ip']}:{server_cfg['port']} "
        f"(bind {server_cfg['host']})"
    )

    app.run(host=server_cfg["host"], port=server_cfg["port"], use_reloader=False)


if __name__ == "__main__":
    main()
