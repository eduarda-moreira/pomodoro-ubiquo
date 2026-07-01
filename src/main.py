"""Protótipo 1 — execução local do timer no terminal.

Roda o ciclo Pomodoro no notebook, exibindo a contagem regressiva e as
transições automáticas. Aceita comandos para pausar, retomar e encerrar.

Uso:
    ./venv/bin/python src/main.py

Comandos (digite a letra e Enter):
    p = pausar    r = retomar    e = encerrar    q = sair

Dica de teste: para não esperar 25 min, use tempos curtos no config.json
(ex.: "foco_min": 0.1  →  6 segundos).
"""
from __future__ import annotations

import threading
import time

from config import carregar_config
from timer import ENCERRADO, MENSAGENS, PomodoroTimer


def formatar(segundos: int) -> str:
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


def anunciar(_anterior: str, proximo: str) -> None:
    # Ponto onde, nas Fases 3 e 4, entram os avisos de voz (Alexa) e vibração.
    print(f"\n>>> {MENSAGENS[proximo]}\n")


def main() -> None:
    cfg = carregar_config()
    timer = PomodoroTimer(cfg, ao_transicionar=anunciar)
    timer.iniciar()

    print("Pomodoro iniciado.  Comandos: [p]ausar  [r]etomar  [e]ncerrar  [q]sair")
    parar = threading.Event()

    def exibir() -> None:
        while not parar.is_set():
            timer.atualizar()
            if timer.situacao == ENCERRADO:
                print("\nSessão encerrada.")
                parar.set()
                break
            e = timer.estado()
            print(
                f"\r[{e['situacao']:^8}] {(e['periodo'] or '-'):<11} "
                f"{formatar(e['tempo_restante_seg'])}  (focos: {e['focos_completos']})   ",
                end="",
                flush=True,
            )
            time.sleep(0.25)

    thread = threading.Thread(target=exibir, daemon=True)
    thread.start()

    try:
        while not parar.is_set():
            comando = input().strip().lower()
            if comando == "p":
                timer.pausar()
            elif comando == "r":
                timer.retomar()
            elif comando == "e":
                timer.encerrar()
            elif comando == "q":
                parar.set()
    except (EOFError, KeyboardInterrupt):
        parar.set()

    print("\nAté logo.")


if __name__ == "__main__":
    main()
