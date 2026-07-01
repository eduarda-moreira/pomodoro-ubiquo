## 1. Visão Geral

Sistema de gerenciamento de ciclos de foco/pausa (Técnica Pomodoro) com um **orquestrador local em Python** que distribui o aviso de fim de ciclo entre múltiplos dispositivos e canais sensoriais (voz via Alexa, vibração via smartwatch), aplicando princípios de Computação Ubíqua.

### Atores do sistema

| Ator | Papel |
|------|-------|
| Usuário | Inicia o primeiro ciclo; recebe avisos passivos |
| Orquestrador (notebook/Python) | Núcleo lógico; controla ciclos e dispara notificações |
| Alexa (Echo) | Canal de voz (skill "Notify Me") |
| Smartwatch (Apple/Galaxy Watch) | Canal háptico (vibração) + disparo de início via HTTP |
| Serviço de push (ntfy/Pushover) | Intermediário de notificação para o pulso |

---

## 2. Requisitos Funcionais (RF)

### Núcleo do timer (Protótipo 1)
- **RF01** — Executar o ciclo Pomodoro com tempos configuráveis (padrão: 25 min foco / 5 min pausa curta / 15 min pausa longa).
- **RF02** — Transicionar automaticamente entre foco e pausa ao término de cada período, sem ação do usuário.
- **RF10** — Permitir **pausar** a sessão durante um período de foco ou de pausa, congelando a contagem do tempo restante.
- **RF11** — Permitir **retomar** a sessão pausada a partir do tempo em que foi interrompida.
- **RF12** — Permitir **encerrar** a sessão a qualquer momento, durante um período de foco ou de pausa, interrompendo a execução sem iniciar um novo período.

### Servidor e comunicação sem fio (Protótipo 2)
- **RF03** — Expor o núcleo via API local (Flask) acessível na rede Wi-Fi.
- **RF04** — Permitir **consultar o estado** atual do timer (foco/pausa, tempo restante, situação: rodando/pausado/encerrado) via endpoint HTTP (GET).
- **RF05** — Permitir **acionar/iniciar** um ciclo remotamente via endpoint HTTP (POST).
- **RF13** — Permitir **pausar, retomar e encerrar** a sessão remotamente via endpoints HTTP (POST).

### Interação por voz (Protótipo 3)
- **RF06** — Ao fim de cada ciclo, disparar requisição HTTP à skill de notificação da Alexa ("Notify Me").
- **RF07** — A Alexa deve anunciar em voz alta a transição (ex.: "Hora da pausa" / "Hora de focar").

### Feedback háptico (Protótipo 4)
- **RF08** — Em paralelo ao aviso por voz, enviar notificação push (ntfy/Pushover) espelhada ao smartwatch, gerando vibração no pulso.
- **RF09** — Iniciar um ciclo a partir do smartwatch (atalho → HTTP POST ao orquestrador) — fluxo bidirecional.

---

## 3. Requisitos Não Funcionais (RNF)

| ID | Categoria | Requisito |
|----|-----------|-----------|
| RNF01 | Usabilidade | Operação autônoma após o início do 1º ciclo — zero configuração manual durante a sessão |
| RNF02 | Usabilidade | Avisos discretos e não disruptivos |
| RNF03 | Confiabilidade | Tratamento de erros de rede e reconexão automática aos dispositivos |
| RNF04 | Confiabilidade | Falha de um canal (ex.: Alexa offline) não deve interromper o ciclo nem os demais canais |
| RNF05 | Desempenho | Latência do aviso (fim do ciclo → notificação) baixa e perceptivelmente imediata |
| RNF06 | Portabilidade | Reaproveitar serviços nativos existentes (skill Alexa, espelhamento de notificações) para favorecer reprodutibilidade |
| RNF07 | Compatibilidade | Suportar ecossistema Apple e Android (Apple Watch e Galaxy Watch) |
| RNF08 | Manutenibilidade | Tempos e endpoints parametrizáveis via arquivo de configuração |
| RNF09 | Disponibilidade | Operar continuamente durante uma sessão de trabalho completa |

---

## 4. Requisitos de Hardware e Software

**Hardware**
- Notebook (orquestrador local)
- Amazon Echo (Alexa)
- Smartwatch Galaxy Watch e Apple Watch
- Smartphone (espelhamento de notificações)
- Rede Wi-Fi local

**Software**
- Python 3
- Bibliotecas: `requests` (chamadas HTTP), `Flask` (API/servidor local)
- Skill Alexa "Notify Me"
- Serviço de push: ntfy **ou** Pushover

---

## 5. Interfaces Externas

- **API REST local (Flask):** endpoints de estado (GET) e de acionamento (POST).
- **Saída → Alexa:** HTTP request à API da skill "Notify Me" (requer token de acesso).
- **Saída → Push:** HTTP request ao ntfy/Pushover (tópico/canal configurado no app do smartwatch).
- **Entrada ← Smartwatch:** HTTP POST do atalho/Tasker para a API local.

---

## 6. Restrições e Premissas

- Todos os dispositivos na **mesma rede Wi-Fi local**; comunicação centrada no orquestrador.
- Arquitetura deliberadamente **simples**, reaproveitando recursos nativos (sem app dedicado no relógio).
- Notebook precisa estar ligado e com o script em execução durante a sessão.
- Dependência de serviços de terceiros (Notify Me, ntfy/Pushover) e de conta Alexa/IP estável na rede.
- Desenvolvimento **incremental e iterativo** em 4 protótipos como marcos.

---

## 7. Casos de Uso (Gherkin)

> Casos de uso no formato Gherkin (Dado / Quando / Então), rastreados aos requisitos
> funcionais (RF) e não funcionais (RNF) das seções 2 e 3.

### Funcionalidade: Iniciar uma sessão de foco

```gherkin
Funcionalidade: Iniciar uma sessão de foco
  Como usuário
  Quero iniciar o ciclo de foco com um único toque no relógio
  Para que o gerenciamento de tempo aconteça sem minha atenção contínua

  Contexto:
    Dado que o orquestrador está em execução no notebook
    E o relógio e a Alexa estão na mesma rede Wi-Fi
    E nenhum ciclo está em andamento

  # RF05, RF09
  Cenário: Início do ciclo de foco pelo relógio
    Quando o usuário toca o atalho "Iniciar foco" no relógio
    Então o orquestrador recebe a requisição HTTP POST de início
    E o ciclo de foco de 25 minutos é iniciado
```

### Funcionalidade: Pausar e retomar a sessão

```gherkin
Funcionalidade: Pausar e retomar a sessão
  Como usuário
  Quero pausar e retomar o Pomodoro durante um período de foco ou de pausa
  Para lidar com uma interrupção sem perder o tempo já decorrido

  # RF10, RF13
  Cenário: Pausar durante um período de foco
    Dado que um ciclo de foco está em andamento com 18:42 restantes
    Quando o usuário aciona o atalho "Pausar" no relógio
    Então o orquestrador recebe a requisição HTTP POST de pausa
    E a contagem do tempo é congelada em 18:42
    E o estado do sistema passa a "pausado"

  # RF10, RF13
  Cenário: Pausar durante um período de pausa
    Dado que uma pausa curta está em andamento com 03:10 restantes
    Quando o usuário aciona o atalho "Pausar" no relógio
    Então o orquestrador recebe a requisição HTTP POST de pausa
    E a contagem do tempo é congelada em 03:10
    E o estado do sistema passa a "pausado"

  # RF11, RF13
  Cenário: Retomar a sessão pausada
    Dado que a sessão está pausada com tempo restante congelado
    Quando o usuário aciona o atalho "Retomar" no relógio
    Então o orquestrador recebe a requisição HTTP POST de retomada
    E a contagem volta a decrescer a partir do tempo congelado
    E o estado do sistema passa a "rodando"
```

### Funcionalidade: Encerrar a sessão

```gherkin
Funcionalidade: Encerrar a sessão
  Como usuário
  Quero encerrar o Pomodoro durante um período de foco ou de pausa
  Para finalizar a sessão quando terminar meu trabalho

  # RF12, RF13
  Cenário: Encerrar durante um período de foco ou de pausa
    Dado que existe um período de foco ou de pausa em andamento ou pausado
    Quando o usuário aciona o atalho "Encerrar" no relógio
    Então o orquestrador recebe a requisição HTTP POST de encerramento
    E a execução do Pomodoro é interrompida
    E nenhum novo período é iniciado automaticamente
    E o estado do sistema passa a "encerrado"
```

### Funcionalidade: Consultar o estado do timer

```gherkin
Funcionalidade: Consultar o estado do timer
  Como dispositivo da rede
  Quero consultar o estado atual do timer
  Para refletir o período e o tempo restante

  # RF04
  Cenário: Consulta do estado atual
    Dado que existe um período em andamento
    Quando um dispositivo consulta o estado via HTTP GET
    Então o orquestrador responde com o tipo do período (foco ou pausa)
    E responde com o tempo restante do período
```

### Funcionalidade: Avisar o término do ciclo de foco

```gherkin
Funcionalidade: Avisar o término do ciclo de foco
  Como usuário
  Quero ser avisado pelo ambiente quando o foco terminar
  Para parar sem precisar olhar para a tela do notebook

  # RF02, RF06, RF07, RF08
  Cenário: Transição de foco para pausa com aviso multissensorial
    Dado que um ciclo de foco de 25 minutos está em andamento
    Quando a contagem do foco chega ao fim
    Então o orquestrador dispara uma requisição HTTP à skill "Notify Me"
    E a Alexa anuncia em voz alta "Hora da pausa"
    E uma notificação push é enviada ao smartwatch, gerando vibração no pulso
    E a pausa curta de 5 minutos é iniciada automaticamente
```

### Funcionalidade: Avisar o término da pausa

```gherkin
Funcionalidade: Avisar o término da pausa
  Como usuário
  Quero ser avisado pelo ambiente quando a pausa terminar
  Para retomar o foco automaticamente

  # RF02, RF06, RF07, RF08
  Cenário: Transição de pausa para foco com aviso multissensorial
    Dado que uma pausa curta de 5 minutos está em andamento
    Quando a contagem da pausa chega ao fim
    Então o orquestrador dispara uma requisição HTTP à skill "Notify Me"
    E a Alexa anuncia em voz alta "Hora de focar"
    E uma notificação push é enviada ao smartwatch, gerando vibração no pulso
    E um novo ciclo de foco de 25 minutos é iniciado automaticamente
```

### Funcionalidade: Encadear ciclos automaticamente

```gherkin
Funcionalidade: Encadear ciclos automaticamente
  Como usuário
  Quero que os ciclos se sucedam sozinhos
  Para que a sessão seja autônoma após o primeiro toque

  # RF01, RF02, RNF01
  Cenário: Pausa longa a cada quatro ciclos de foco
    Dado que o usuário já completou três ciclos de foco
    Quando o quarto ciclo de foco chega ao fim
    Então o orquestrador inicia uma pausa longa de 15 minutos
    E a Alexa anuncia "Hora da pausa longa"
    E o smartwatch vibra no pulso
```

### Funcionalidade: Robustez de comunicação (cenários de exceção)

```gherkin
Funcionalidade: Robustez de comunicação
  Como usuário
  Quero que a falha de um canal não interrompa minha sessão
  Para manter a confiabilidade do sistema

  # RNF04
  Cenário: Alexa indisponível no momento do aviso
    Dado que um período chega ao fim
    E a Alexa está offline ou não responde
    Quando o orquestrador tenta enviar o aviso de voz
    Então o aviso por voz falha sem interromper o ciclo
    E o smartwatch ainda vibra no pulso
    E o próximo período é iniciado normalmente

  # RNF03
  Cenário: Falha temporária de rede com o relógio
    Dado que um período está em andamento
    E o relógio perde a conexão com o orquestrador
    Quando a conexão é restabelecida
    Então o relógio volta a consultar o estado via HTTP GET
    E passa a refletir o tempo restante real do período
```