# TAPRA - 2026

Atividade de Tópicos Avançados em Programação: pipeline de dados com Azure Functions, do sistema
de chamados (ITSM) até um painel de indicadores no Power BI.

## Integrantes da equipe

- João Pedro Sedrez
- Otávio Oliveira Bernardo
- Victor Luiz da Silva

## Visão geral

```
Azure SQL de origem (schema itsm)
        │  extração de hora em hora (timer)
        ▼
Data Lake / Storage Account, container bronze (JSON particionado por data)
        │  carga diária às 06:00 UTC (03:00 de Brasília)
        ▼
Azure SQL de destino db-tapra-destino (schema dbo, 10 tabelas + views de indicadores)
        │  atualização agendada diária às 05:00 de Brasília
        ▼
Power BI: relatório "Painel Indicadores TAPRA"
```

| Recurso                 | Nome / detalhe                                                         |
|-------------------------|------------------------------------------------------------------------|
| Function App            | `FuncApp-TAPRA-JOAO-OTAVIO-VICTOR` (Flex Consumption, Linux, Python 3.13, Canada Central) |
| Storage (Data Lake)     | container `bronze`, caminho `itsm/<entidade>/ano=AAAA/mes=MM/dia=DD/`  |
| Banco de destino        | `db-tapra-destino` no servidor `sql-tapra-joao-otavio-victor` (oferta gratuita, com auto-pausa) |
| Painel                  | Power BI, relatório "Painel Indicadores TAPRA" (modelo "Indicadores ITSM", modo Import) |
| CI/CD                   | GitHub Actions com login OIDC no Azure                                 |

## Painel de indicadores (Power BI)

O painel lê as views de [`sql/views_indicadores.sql`](sql/views_indicadores.sql) no banco de
destino e é atualizado todo dia, depois da carga.

<!-- PRINTS_DO_PAINEL -->

Indicadores disponíveis nas views:

| View                              | Indicador                                                    |
|-----------------------------------|--------------------------------------------------------------|
| `vw_chamado_detalhado`            | Base única: um chamado por linha, com descrições resolvidas  |
| `vw_ind_resumo`                   | Total de chamados, backlog, % resolvidos, tempo médio de resolução, % dentro do SLA, CSAT médio |
| `vw_ind_chamados_por_mes`         | Chamados abertos e resolvidos por mês                        |
| `vw_ind_chamados_por_dimensao`    | Chamados por status, tipo, prioridade, categoria, fila e cliente |
| `vw_ind_chamados_por_analista`    | Chamados por analista, com nível e CSAT                      |
| `vw_ind_sla_por_prioridade`       | Tempo de resolução e SLA por prioridade                      |
| `vw_ind_sla_por_fila`             | Cumprimento de SLA por fila                                  |
| `vw_ind_tempo_por_status`         | Tempo médio em cada status                                   |
| `vw_ind_csat_notas`               | Distribuição das notas de CSAT                               |

## Functions

Todas ficam em [`function_app.py`](function_app.py) (modelo de programação Python v2).

| Function                        | Gatilho                     | O que faz                                                        |
|---------------------------------|-----------------------------|------------------------------------------------------------------|
| `extract_<tabela>` (10 funções) | Timer, de hora em hora      | Lê uma tabela `itsm.*` da origem e grava o JSON no container `bronze` |
| `extrair_agora`                 | HTTP (chave de função)      | Roda a extração na hora; `?entidade=<nome>` para uma só          |
| `load_destino`                  | Timer, diário às 06:00 UTC  | Recarrega as tabelas `dbo.*` do destino a partir do JSON mais recente de cada entidade, numa única transação |
| `carregar_agora`                | HTTP (chave de função)      | Roda a carga do destino na hora e devolve as linhas inseridas por tabela |

Tabelas extraídas: analistas, categorias, chamados, chamados_sla, chamados_status_historico,
clientes_organizacao, csat_avaliacoes, filas, slas e solicitantes.

As pastas `HttpTriggerEcho`, `TimerTriggerLog` e `TimerTriggerCaller` são da primeira entrega da
disciplina (modelo v1) e foram mantidas no repositório.

## Banco de destino

Scripts em [`sql/`](sql/), executados nesta ordem:

1. [`create_tables.sql`](sql/create_tables.sql): cria as 10 tabelas `dbo`.
2. [`add_foreign_keys.sql`](sql/add_foreign_keys.sql): adiciona as chaves estrangeiras.
3. [`views_indicadores.sql`](sql/views_indicadores.sql): cria as views usadas pelo Power BI.

## Configuração

Copie `local.settings.json.example` para `local.settings.json` e preencha:

| Variável                       | Uso                                            |
|--------------------------------|------------------------------------------------|
| `HOST`, `DATABASE`, `SQL_USER`, `PASSWORD` | Banco de origem (ITSM)             |
| `DATALAKE_CONNECTION_STRING`, `BRONZE_CONTAINER` | Storage do Data Lake         |
| `DEST_HOST`, `DEST_DATABASE`, `DEST_USER`, `DEST_PASSWORD` | Banco de destino   |

Na Function App, as mesmas variáveis ficam nas configurações do aplicativo.

Para rodar localmente (precisa do Azure Functions Core Tools e do ODBC Driver 18):

```bash
pip install -r requirements.txt
func start
```

## CI/CD

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em todo push e pull
request para `main`:

1. **Validação:** compila o código e checa `ruff`, `black` e `isort` (regras em `pyproject.toml`).
2. **Deploy** (só em push na `main`): login no Azure via OIDC e publicação na Function App com
   build remoto.

## Estrutura do projeto

```
TAPRA-2026/
├── .github/workflows/ci.yml
├── function_app.py              # extração, carga e funções HTTP
├── sql/
│   ├── create_tables.sql
│   ├── add_foreign_keys.sql
│   └── views_indicadores.sql
├── docs/img/                    # prints do painel
├── HttpTriggerEcho/             # primeira entrega (v1)
├── TimerTriggerLog/             # primeira entrega (v1)
├── TimerTriggerCaller/          # primeira entrega (v1)
├── host.json
├── requirements.txt
├── pyproject.toml
├── local.settings.json.example
└── README.md
```
