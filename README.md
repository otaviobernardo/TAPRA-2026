# TAPRA - 2026

Atividade de Tópicos Avançados Em Programação - Azure Functions.

## Integrantes da equipe

- João Pedro Sedrez
- Otávio Oliveira Bernardo
- Victor Luiz da Silva

## Descrição

O projeto contém três Azure Functions:

| Function            | Gatilho (trigger) | O que faz                                                                 |
|----------------------|--------------------|-----------------------------------------------------------------------------|
| `TimerTriggerLog`     | Timer              | Executa periodicamente e imprime apenas um log no terminal.                |
| `HttpTriggerEcho`     | HTTP (GET)         | Recebe um parâmetro via URL e o imprime/retorna na resposta.               |
| `TimerTriggerCaller`  | Timer              | Executa periodicamente, chama `HttpTriggerEcho` via HTTP e imprime o resultado combinado (parâmetro + texto identificador). |

## Estrutura do projeto

```
TAPRA/
├── HttpTriggerEcho/
│   ├── __init__.py
│   └── function.json
├── TimerTriggerLog/
│   ├── __init__.py
│   └── function.json
├── TimerTriggerCaller/
│   ├── __init__.py
│   └── function.json
├── host.json
├── requirements.txt
├── local.settings.json
├── local.settings.json.example
└── README.md
```