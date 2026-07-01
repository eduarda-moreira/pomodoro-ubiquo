# Diário de Bordo — Pomodoro Ubíquo

**Fases:** 0 (Preparação), 1 (Núcleo do Timer), 2 (Servidor Local) · **Voz:** Notify Me → Voice Monkey

---

### Fase 0 — Preparação do ambiente

- Ecossistema do relógio definido: **Galaxy Watch** (Tasker/AutoWear).
- Estrutura criada (`src/`, `docs/`), `venv` com **Python 3.14.5** e dependências **Flask**, **requests**, **python-dotenv** (em `requirements.txt`).
- **`config.json`** com os parâmetros (tempos, servidor, Alexa, push) e **`config.py`** para carregá-los.
- **`.env` / `.env.example`**: IP do notebook e tokens ficam fora do código versionado; o `config.json` os referencia via `${VAR}`.
- **Decisão:** removidos artefatos sem requisito (histórico e dashboard, resíduos de versões antigas) para manter o projeto objetivo.
- ✅ Verificado: `config.py` resolve os placeholders (`Servidor: 192.168.0.100:5000`).
- ⏳ Pendente: reservar o IP fixo real no roteador (config de rede).

### Fase 1 — Núcleo do Timer

- Criados **`src/timer.py`** (lógica pura) e **`src/main.py`** (execução no terminal).
- Implementado: ciclo de foco/pausa com tempos configuráveis (RF01), transição automática (RF02), pausa longa a cada 4 focos, **pausar** (RF10), **retomar** (RF11), **encerrar** (RF12); máquina de estados `ocioso/rodando/pausado/encerrado`.
- **Decisões:** relógio injetável (permite testar sem esperar tempo real); callback `ao_transicionar` como ponto único para os avisos das próximas fases; `estado()` serializável para o `GET /estado`.
- ✅ Verificado: teste com relógio falso (início, congelamento na pausa, sequência até a pausa longa) e smoke test do terminal — todos passaram.
- **Correções de robustez** achadas nos testes: `round` no lugar de `int` (evita truncamento) e motor comparando o tempo real, não o arredondado (antes o período fechava ~0,5 s cedo).

### Fase 2 — Servidor Local (Flask)

- Criado **`src/server.py`** encapsulando o timer numa API HTTP (`0.0.0.0:5000`, RF03).
- Endpoints (todos testados com `curl`): `GET /estado` (RF04), `POST /iniciar` (RF05), `POST /pausar`, `/retomar`, `/encerrar` (RF13).
- **Decisões:** *ticker* em thread separada chama `atualizar()` a cada 0,5 s (transições automáticas sem depender de requisição); `Lock` evita corrida entre ticker e HTTP; bind em `0.0.0.0` com `ip_notebook` à parte (endereço que o relógio usa); `use_reloader=False` para não duplicar o ticker.
- ✅ Verificado: fluxo completo iniciar→pausar (congelou)→retomar→encerrar e transição automática em tempo real (foco de 2 s fechou em 2,0 s), sem erros.
- ⏳ Pendente: validar de outro aparelho da rede (depende do IP fixo).

---

### Fase 3 — Voz: da Notify Me ao Voice Monkey

- **Bloqueio da Notify Me:** ao habilitar a skill (conta `amazon.com.br`), erro *"not eligible… geographical restrictions"*. A skill só funciona em contas dos EUA.
- **Rota de conta US avaliada e descartada:** a troca de país some em contas `.com.br` e exige endereço nos EUA; deixaria a Echo em inglês (pronúncia ruim do português) e afetaria Prime/pedidos ou exigiria re-registrar a Echo.
- **Fato técnico:** a Echo **não tem API local** — toda solução passa pela nuvem da Amazon; não há como falar direto com o aparelho na rede.
- **Alternativas:** TTS local no notebook (foge do conceito ubíquo); rotina + dispositivo virtual (frase fixa); método por cookie (sem terceiros e sem limite, mas não oficial e cookie expira); **Voice Monkey** (skill + API HTTP, com **pt-BR** e TTS dinâmico).
- **Voice Monkey — tentativa em andamento:** skill **habilitada e conta linkada com sucesso** (sem a barreira geográfica da Notify Me). Encaixa na arquitetura original (script → `POST /announce` → Echo fala em português). Faltam: criar o *Speaker*, gerar o token e o *device ID* (irão para o `.env`).
- **Custo (exigência: gratuito):** plano grátis = **200 requisições/mês**; cada anúncio = 1 requisição (~8 por sessão ⇒ ~25 sessões/mês). Suficiente para desenvolvimento e demo. **Mitigação:** modo *dry-run* (`alexa.habilitado`) imprime o aviso no terminal durante os testes, sem gastar cota.
- **Decisão em aberto:** Voice Monkey (menos esforço, confiável, grátis até 200/mês, mas é serviço terceiro) × método por cookie (sem terceiros e ilimitado, porém frágil). O núcleo já está pronto para qualquer um — muda só o módulo de notificação.

---

### Situação atual

| Fase | Situação |
|---|---|
| 0 — Preparação | ✅ concluída (pendente IP fixo) |
| 1 — Núcleo do Timer | ✅ concluída e testada |
| 2 — Servidor Flask | ✅ concluída (falta teste de outro aparelho) |
| 3 — Voz | 🔄 Notify Me descartada; Voice Monkey linkado, em desenvolvimento |
| 4 — Háptico + relógio | ⏳ pendente |

**Próximo:** definir o mecanismo de voz, plugar credenciais no `.env` e implementar o módulo de notificação com dry-run.
