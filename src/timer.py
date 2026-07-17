"""
CORE DO PROJETO

Maquina de estados controla os ciclos de foco e pausa.
Arquivo de lógica pura, reutilizado pelo runner de terminal e pelo servidor Flask.
"""

from __future__ import annotations
from typing import Callable, Optional
import time

# Periodos
FOCUS = "focus"
SHORT_BREAK = "short_break"
LONG_BREAK = "long_break"

# Estados
IDLE = "idle"
RUNNING = "running"
PAUSED = "paused"
STOPPED = "stopped"

# Mensagens
MESSAGES = {
    FOCUS: "Hora de focar",
    SHORT_BREAK: "Faça uma pausa curta",
    LONG_BREAK: "Faça uma pausa longa",
}

# Anúncios para comandos manuais
PAUSE_MESSAGE = "Pausando"
RESUME_MESSAGE = "Retomando"


class PomodoroTimer:
    """
    Controla os ciclos do pomodoro
    """

    def __init__(
        self,
        config: dict,
        on_transition: Optional[Callable[[Optional[str], str], None]] = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        timing = config["timing"]
        self._duration = {
            FOCUS: round(timing["focus_min"] * 60),
            SHORT_BREAK: round(timing["short_break_min"] * 60),
            LONG_BREAK: round(timing["long_break_min"] * 60),
        }
        self._cycles_until_long_break = int(timing["cycles_until_long_break"])
        self._on_transition = on_transition
        self._clock = clock

        self.status = IDLE
        self.period: Optional[str] = None
        self.completed_focuses = 0
        self._end = 0.0
        self._paused_remaining = 0

    # consultas
    def _raw_remaining(self) -> float:
        """Segundos restantes em float"""
        if self.status == RUNNING:
            return self._end - self._clock()
        if self.status == PAUSED:
            return self._paused_remaining
        return 0.0

    def remaining_time(self) -> int:
        """Segundos restantes do periodo atual"""
        return max(0, int(round(self._raw_remaining())))

    def state(self) -> dict:
        """Snapshot serializável do estado"""
        return {
            "status": self.status,
            "period": self.period,
            "remaining_seconds": self.remaining_time(),
            "completed_focuses": self.completed_focuses,
        }

    # comandos
    def start(self) -> None:
        """Começa a sessão, iniciando o primeiro periodo de foco"""
        if self.status in (RUNNING, PAUSED):
            return
        self.completed_focuses = 0
        self._start_period(FOCUS)
        if self._on_transition:
            self._on_transition(None, FOCUS)

    def pause(self) -> None:
        """Pausa o periodo atual, mantendo o tempo restante para retomar depois"""
        if self.status != RUNNING:
            return
        self._paused_remaining = self._raw_remaining()
        self.status = PAUSED

    def resume(self) -> None:
        """Retoma o periodo pausado"""
        if self.status != PAUSED:
            return
        self._end = self._clock() + self._paused_remaining
        self.status = RUNNING

    def stop(self) -> None:
        """Encerra a sessão sem iniciar um novo periodo"""
        self.status = STOPPED
        self.period = None

    # engine
    def update(self) -> None:
        """Avança a maquina de estados quando o periodo atual termina"""
        if self.status == RUNNING and self._raw_remaining() <= 0:
            self._transition()

    # internos
    def _start_period(self, period: str) -> None:
        self.period = period
        self._end = self._clock() + self._duration[period]
        self.status = RUNNING

    def _transition(self) -> None:
        previous = self.period
        if previous == FOCUS:
            self.completed_focuses += 1
            if self.completed_focuses % self._cycles_until_long_break == 0:
                next_period = LONG_BREAK
            else:
                next_period = SHORT_BREAK
        else:
            next_period = FOCUS

        self._start_period(next_period)
        if self._on_transition:
            self._on_transition(previous, next_period)
