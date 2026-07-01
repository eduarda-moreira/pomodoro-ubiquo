"""Núcleo do Timer Pomodoro (Protótipo 1).

Máquina de estados que gerencia os ciclos de foco e pausa, com controle de
pausar / retomar / encerrar. Não depende de rede nem de terminal — é lógica
pura, reutilizada pelo runner de terminal (Fase 1) e pelo servidor Flask (Fase 2).

O tempo é medido por um "relógio" injetável (padrão: `time.monotonic`), o que
permite testar as transições instantaneamente com um relógio falso.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

# Períodos
FOCO = "foco"
PAUSA_CURTA = "pausa_curta"
PAUSA_LONGA = "pausa_longa"

# Situações
OCIOSO = "ocioso"
RODANDO = "rodando"
PAUSADO = "pausado"
ENCERRADO = "encerrado"

# Anúncio de cada transição (usado pelo runner / futuras notificações)
MENSAGENS = {
    FOCO: "Hora de focar",
    PAUSA_CURTA: "Hora da pausa",
    PAUSA_LONGA: "Hora da pausa longa",
}


class PomodoroTimer:
    """Controla um ciclo Pomodoro configurável.

    `ao_transicionar(periodo_anterior, periodo_novo)` é chamado a cada troca
    automática de período — ponto de extensão para os avisos de voz/vibração.
    """

    def __init__(
        self,
        config: dict,
        ao_transicionar: Optional[Callable[[str, str], None]] = None,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        tempos = config["tempos"]
        # round evita truncamento por ponto flutuante em minutos fracionários
        # usados em testes (ex.: 0.1 min → 6 s).
        self._dur = {
            FOCO: round(tempos["foco_min"] * 60),
            PAUSA_CURTA: round(tempos["pausa_curta_min"] * 60),
            PAUSA_LONGA: round(tempos["pausa_longa_min"] * 60),
        }
        self._ciclos_ate_longa = int(tempos["ciclos_ate_pausa_longa"])
        self._ao_transicionar = ao_transicionar
        self._relogio = relogio

        self.situacao = OCIOSO
        self.periodo: Optional[str] = None
        self.focos_completos = 0
        self._fim = 0.0             # instante (relógio) do fim, quando RODANDO
        self._restante_pausado = 0  # segundos congelados, quando PAUSADO

    # ------------------------------------------------------------------ consultas
    def _restante_raw(self) -> float:
        """Segundos restantes como float (uso interno, sem arredondar)."""
        if self.situacao == RODANDO:
            return self._fim - self._relogio()
        if self.situacao == PAUSADO:
            return self._restante_pausado
        return 0.0

    def tempo_restante(self) -> int:
        """Segundos restantes do período atual, arredondados para exibição."""
        return max(0, int(round(self._restante_raw())))

    def estado(self) -> dict:
        """Snapshot serializável do estado (base para o GET /estado da Fase 2)."""
        return {
            "situacao": self.situacao,
            "periodo": self.periodo,
            "tempo_restante_seg": self.tempo_restante(),
            "focos_completos": self.focos_completos,
        }

    # ------------------------------------------------------------------- comandos
    def iniciar(self) -> None:
        """Inicia a sessão a partir de um período de foco (RF05)."""
        if self.situacao in (RODANDO, PAUSADO):
            return  # já em andamento
        self.focos_completos = 0
        self._iniciar_periodo(FOCO)

    def pausar(self) -> None:
        """Congela a contagem do período atual (RF10)."""
        if self.situacao != RODANDO:
            return
        self._restante_pausado = self._restante_raw()
        self.situacao = PAUSADO

    def retomar(self) -> None:
        """Retoma do tempo em que foi pausado (RF11)."""
        if self.situacao != PAUSADO:
            return
        self._fim = self._relogio() + self._restante_pausado
        self.situacao = RODANDO

    def encerrar(self) -> None:
        """Encerra a sessão sem iniciar novo período (RF12)."""
        self.situacao = ENCERRADO
        self.periodo = None

    # --------------------------------------------------------------------- motor
    def atualizar(self) -> None:
        """Avança a máquina de estados; chame periodicamente.

        Quando o tempo do período em andamento chega a zero, faz a transição
        automática para o próximo período (RF02).
        """
        if self.situacao == RODANDO and self._restante_raw() <= 0:
            self._transicionar()

    # ------------------------------------------------------------------ internos
    def _iniciar_periodo(self, periodo: str) -> None:
        self.periodo = periodo
        self._fim = self._relogio() + self._dur[periodo]
        self.situacao = RODANDO

    def _transicionar(self) -> None:
        anterior = self.periodo
        if anterior == FOCO:
            self.focos_completos += 1
            # Pausa longa a cada N focos; caso contrário, pausa curta.
            if self.focos_completos % self._ciclos_ate_longa == 0:
                proximo = PAUSA_LONGA
            else:
                proximo = PAUSA_CURTA
        else:
            proximo = FOCO  # depois de qualquer pausa, volta ao foco

        self._iniciar_periodo(proximo)
        if self._ao_transicionar:
            self._ao_transicionar(anterior, proximo)
