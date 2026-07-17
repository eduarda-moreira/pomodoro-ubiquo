# Checklist de Execução — Pomodoro Ubíquo

> Ordem recomendada de desenvolvimento, do núcleo local até a integração ubíqua.
> Marque `[x]` conforme concluir. Cada fase tem um **critério de pronto** (Definition of Done).

---

## Fase 0 — Preparação do ambiente

- [x] Definir o ecossistema-alvo do relógio: **Galaxy Watch (Tasker/AutoWear)**
- [x] Criar repositório Git do projeto e estrutura de pastas (`/src`, `/docs`)
- [x] Instalar Python 3 e criar ambiente virtual (`python -m venv venv`)
- [x] Instalar dependências: `pip install flask requests`
- [x] Criar arquivo `requirements.txt` (Flask, requests)
- [x] Criar arquivo de configuração `config.py`/`config.json` (tempos, IPs, tokens)
- [x] Parametrizar IP do notebook e segredos via `.env` (`NOTEBOOK_IP`, `SERVER_PORT`, tokens) resolvidos em `config.json`
- [ ] Reservar o IP fixo real no roteador (reserva DHCP) e preencher `NOTEBOOK_IP` no `.env` *(config de rede — fazer antes da Fase 2)*

**✅ Pronto quando:** o ambiente roda um "hello world" em Python e o Git está versionando.

---

## Fase 1 — Protótipo 1: Núcleo do Timer (local)  · *RF01, RF02, RF10, RF11, RF12*

- [x] Implementar a contagem de um período de foco (25 min)
- [x] Implementar a transição automática foco → pausa curta (5 min) → foco
- [x] Implementar pausa longa (15 min) a cada 4 ciclos de foco
- [x] Tornar os tempos configuráveis (ler do `config`)
- [x] Implementar **pausar** (congela o tempo restante)
- [x] Implementar **retomar** (volta do tempo congelado)
- [x] Implementar **encerrar** (interrompe sem iniciar novo período)
- [x] Modelar a máquina de estados: `rodando / pausado / encerrado` + período atual
- [x] Testar o ciclo completo com relógio falso (transições/pausa/encerrar) e smoke test do terminal

**✅ Pronto quando:** o script roda os ciclos sozinho no terminal e aceita pausar/retomar/encerrar.

---

## Fase 2 — Protótipo 2: Servidor Local (Flask)  · *RF03, RF04, RF05, RF13*

- [x] Encapsular o núcleo do timer numa aplicação Flask
- [x] Rodar o servidor acessível na rede Wi-Fi (`host='0.0.0.0'`)
- [x] Endpoint `GET /estado` → período atual, tempo restante, situação
- [x] Endpoint `POST /iniciar` → inicia um ciclo
- [x] Endpoint `POST /pausar` → pausa a sessão
- [x] Endpoint `POST /retomar` → retoma a sessão
- [x] Endpoint `POST /encerrar` → encerra a sessão
- [x] Garantir que o timer rode em paralelo ao servidor (thread ticker + lock) sem travar a API
- [x] Testar os endpoints via `curl` (falta validar de outro aparelho da rede — depende do IP fixo)

**✅ Pronto quando:** dá para iniciar/pausar/retomar/encerrar e consultar o estado via HTTP de outro aparelho na mesma rede.

---

## Fase 3 — Protótipo 3: Interação por Voz (Alexa)  · *RF06, RF07*

- [ ] Instalar e configurar a skill **"Notify Me"** na conta Alexa
- [ ] Obter o `accessCode`/token da skill
- [ ] Implementar função que envia notificação à Alexa via `requests` (HTTP POST)
- [ ] Disparar o anúncio "Hora da pausa" ao fim do foco
- [ ] Disparar o anúncio "Hora de focar" ao fim da pausa
- [ ] Disparar o anúncio "Hora da pausa longa" ao fim do 4º foco
- [ ] Testar de ponta a ponta: ciclo termina → Alexa fala

**✅ Pronto quando:** ao término de cada período a Echo anuncia a transição em voz alta.

---

## Fase 4 — Protótipo 4: Feedback Háptico + Controle pelo Relógio  · *RF08, RF09, RF13*

- [ ] Criar conta/tópico no serviço de push (**ntfy** ou **Pushover**)
- [ ] Instalar o app de push no smartphone e parear com o smartwatch (espelhamento)
- [ ] Implementar envio de push (vibração) **em paralelo** ao aviso de voz
- [ ] Validar que o pulso vibra ao fim de cada período
- [ ] Criar atalho no relógio: **Iniciar** → `POST /iniciar`
- [ ] Criar atalho no relógio: **Pausar** → `POST /pausar`
- [ ] Criar atalho no relógio: **Retomar** → `POST /retomar`
- [ ] Criar atalho no relógio: **Encerrar** → `POST /encerrar`
- [ ] Testar fluxo bidirecional completo: inicia pelo relógio → voz + vibração nas transições

**✅ Pronto quando:** o usuário controla a sessão pelo pulso e recebe voz + vibração sem olhar para o notebook.

---

## Fase 5 — Robustez e Toques Finais  · *RNF03, RNF04, RNF05*

- [ ] Tratar erros de rede (timeout/retry) nas chamadas à Alexa e ao push
- [ ] Garantir que falha de um canal não interrompa o ciclo (degradação graciosa)
- [ ] Tratar reconexão automática dos dispositivos
- [ ] Medir e ajustar a latência do aviso (fim do ciclo → notificação)
- [ ] Desabilitar suspensão do notebook durante a sessão
- [ ] Teste de ponta a ponta de uma sessão real completa (vários ciclos)
- [ ] Revisar e finalizar a documentação técnica

**✅ Pronto quando:** o sistema opera uma sessão completa de forma autônoma e estável, mesmo com falhas pontuais de canal.

---

## Fase 6 — Apresentação

- [ ] Preparar slides (motivação, arquitetura, demo, resultados)
- [ ] Roteiro da **demonstração ao vivo** do fluxo completo
- [ ] Ensaiar a demo e ter um plano B (vídeo gravado caso a rede falhe)

**✅ Pronto quando:** material e demonstração prontos e ensaiados.

---

### Sugestão de divisão de frentes (paralelizável após a Fase 2)
- **Frente A (backend):** Fases 1, 2 e 5 (núcleo, API, robustez)
- **Frente B (voz):** Fase 3 (skill Alexa)
- **Frente C (dispositivos):** Fase 4 (push, atalhos do relógio)
- **Frente D (documentação/apresentação):** Fase 6 em paralelo
