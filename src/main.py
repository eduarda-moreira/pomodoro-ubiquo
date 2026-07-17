"""
EXECUÇÃO EM TERMINAL

Executa o pomodoro no notebook, mostrando a contagem regressiva e as transições automáticas.

Comandos
    p = pausar
    r = retomar
    e = encerrar
    q = sair
"""

from __future__ import annotations

import threading
import time
from typing import Optional

from alexa import announce_voice
from config import load_config
from timer import (
    MESSAGES,
    PAUSE_MESSAGE,
    PAUSED,
    RESUME_MESSAGE,
    RUNNING,
    STOPPED,
    PomodoroTimer,
)


def format_time(seconds: int) -> str:
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def speak(message: str) -> None:
    print(f"\n>>> {message}\n")
    if not announce_voice(message):
        print(">>> [Alexa] Aviso de voz falhou; ciclo continua normalmente.\n")


def announce(_previous: Optional[str], next_period: str) -> None:
    speak(MESSAGES[next_period])


def main() -> None:
    cfg = load_config()
    timer = PomodoroTimer(cfg, on_transition=announce)
    timer.start()

    print("Pomodoro iniciado.  Comandos: [p]ausar  [r]etomar  [e]ncerrar  [q]sair")
    stop_event = threading.Event()

    def display() -> None:
        while not stop_event.is_set():
            timer.update()
            if timer.status == STOPPED:
                print("\nSessão encerrada.")
                stop_event.set()
                break
            state = timer.state()
            print(
                f"\r[{state['status']:^8}] {(state['period'] or '-'):<11} "
                f"{format_time(state['remaining_seconds'])}  (focos: {state['completed_focuses']})   ",
                end="",
                flush=True,
            )
            time.sleep(0.25)

    thread = threading.Thread(target=display, daemon=True)
    thread.start()

    try:
        while not stop_event.is_set():
            command = input().strip().lower()
            if command == "p":
                if timer.status == RUNNING:
                    timer.pause()
                    speak(PAUSE_MESSAGE)
            elif command == "r":
                if timer.status == PAUSED:
                    timer.resume()
                    speak(RESUME_MESSAGE)
            elif command == "e":
                timer.stop()
            elif command == "q":
                stop_event.set()
    except (EOFError, KeyboardInterrupt):
        stop_event.set()


if __name__ == "__main__":
    main()
