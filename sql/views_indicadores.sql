-- Views dos indicadores do painel (Power BI), no banco de destino.
-- CREATE OR ALTER: pode rodar quantas vezes quiser.

-- Base unica: um chamado por linha, com as descricoes ja resolvidas.
-- O Power BI pode montar quase todos os indicadores so a partir desta view.
CREATE OR ALTER VIEW dbo.vw_chamado_detalhado AS
SELECT
    c.id_chamado,
    c.nr_chamado,
    c.ds_tipo_chamado,
    c.ds_status_chamado,
    CASE WHEN c.ds_status_chamado IN ('OPEN', 'IN_PROGRESS', 'PENDING') THEN 1 ELSE 0 END
        AS fl_backlog,
    CASE WHEN c.ds_status_chamado IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END AS fl_resolvido,
    c.ds_prioridade,
    c.dt_criacao,
    CAST(c.dt_criacao AS DATE) AS dt_abertura,
    DATEFROMPARTS(YEAR(c.dt_criacao), MONTH(c.dt_criacao), 1) AS mes_abertura,
    c.dt_resolucao,
    CASE WHEN c.dt_resolucao IS NOT NULL
         THEN DATEDIFF(MINUTE, c.dt_criacao, c.dt_resolucao) / 60.0 END AS qt_horas_resolucao,
    a.nm_analista,
    a.ds_nivel AS ds_nivel_analista,
    cat.nm_categoria,
    f.nm_fila,
    co.nm_cliente_organizacao,
    s.nm_solicitante,
    sla.nm_sla,
    cs.qt_meta_minutos AS qt_meta_sla_minutos,
    cs.fl_breach AS fl_sla_violado,
    csat.nr_score AS nr_csat
FROM dbo.chamado c
LEFT JOIN dbo.analista a ON a.id_analista = c.id_analista_atual
LEFT JOIN dbo.categoria cat ON cat.id_categoria = c.id_categoria
LEFT JOIN dbo.fila f ON f.id_fila = c.id_fila_atual
LEFT JOIN dbo.cliente_organizacao co ON co.id_cliente_organizacao = c.id_cliente_organizacao
LEFT JOIN dbo.solicitante s ON s.id_solicitante = c.id_reporter
LEFT JOIN dbo.chamado_sla cs ON cs.id_chamado = c.id_chamado
LEFT JOIN dbo.sla sla ON sla.id_sla = cs.id_sla
LEFT JOIN dbo.csat_avaliacao csat ON csat.id_chamado = c.id_chamado;
GO

-- 1. Total de chamados e backlog
CREATE OR ALTER VIEW dbo.vw_ind_resumo AS
SELECT
    COUNT(*) AS qt_chamados,
    SUM(fl_backlog) AS qt_backlog,
    SUM(fl_resolvido) AS qt_resolvidos,
    CAST(100.0 * SUM(fl_resolvido) / NULLIF(COUNT(*), 0) AS DECIMAL(5, 1)) AS pc_resolvidos,
    CAST(AVG(qt_horas_resolucao) AS DECIMAL(10, 1)) AS qt_horas_media_resolucao,
    CAST(100.0 * SUM(CASE WHEN fl_sla_violado = 0 THEN 1 ELSE 0 END)
         / NULLIF(COUNT(fl_sla_violado), 0) AS DECIMAL(5, 1)) AS pc_dentro_sla,
    CAST(AVG(CAST(nr_csat AS DECIMAL(4, 2))) AS DECIMAL(4, 2)) AS nr_csat_medio
FROM dbo.vw_chamado_detalhado;
GO

-- 2. Chamados abertos e resolvidos por mes
CREATE OR ALTER VIEW dbo.vw_ind_chamados_por_mes AS
SELECT
    mes_abertura,
    COUNT(*) AS qt_abertos,
    SUM(fl_resolvido) AS qt_resolvidos,
    CAST(100.0 * SUM(fl_resolvido) / COUNT(*) AS DECIMAL(5, 1)) AS pc_resolvidos
FROM dbo.vw_chamado_detalhado
GROUP BY mes_abertura;
GO

-- 3 a 8. Chamados por dimensao (status, tipo, prioridade, categoria, fila, cliente)
CREATE OR ALTER VIEW dbo.vw_ind_chamados_por_dimensao AS
SELECT 'Status' AS ds_dimensao, ds_status_chamado AS ds_valor, COUNT(*) AS qt_chamados
FROM dbo.vw_chamado_detalhado GROUP BY ds_status_chamado
UNION ALL
SELECT 'Tipo', ds_tipo_chamado, COUNT(*) FROM dbo.vw_chamado_detalhado GROUP BY ds_tipo_chamado
UNION ALL
SELECT 'Prioridade', ds_prioridade, COUNT(*) FROM dbo.vw_chamado_detalhado GROUP BY ds_prioridade
UNION ALL
SELECT 'Categoria', nm_categoria, COUNT(*) FROM dbo.vw_chamado_detalhado GROUP BY nm_categoria
UNION ALL
SELECT 'Fila', nm_fila, COUNT(*) FROM dbo.vw_chamado_detalhado GROUP BY nm_fila
UNION ALL
SELECT 'Cliente', nm_cliente_organizacao, COUNT(*)
FROM dbo.vw_chamado_detalhado GROUP BY nm_cliente_organizacao;
GO

-- 9 e 10. Chamados x Analista (com nivel e CSAT)
CREATE OR ALTER VIEW dbo.vw_ind_chamados_por_analista AS
SELECT
    a.nm_analista,
    a.ds_nivel,
    COUNT(c.id_chamado) AS qt_chamados,
    SUM(CASE WHEN c.ds_status_chamado IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END)
        AS qt_resolvidos,
    SUM(CASE WHEN c.ds_status_chamado IN ('OPEN', 'IN_PROGRESS', 'PENDING') THEN 1 ELSE 0 END)
        AS qt_backlog,
    (SELECT CAST(AVG(CAST(x.nr_score AS DECIMAL(4, 2))) AS DECIMAL(4, 2))
     FROM dbo.csat_avaliacao x WHERE x.id_analista = a.id_analista) AS nr_csat_medio
FROM dbo.analista a
LEFT JOIN dbo.chamado c ON c.id_analista_atual = a.id_analista
GROUP BY a.id_analista, a.nm_analista, a.ds_nivel;
GO

-- 11 e 12. Tempo de resolucao e SLA por prioridade
CREATE OR ALTER VIEW dbo.vw_ind_sla_por_prioridade AS
SELECT
    ds_prioridade,
    COUNT(*) AS qt_chamados,
    SUM(CASE WHEN fl_sla_violado = 0 THEN 1 ELSE 0 END) AS qt_dentro_sla,
    SUM(CASE WHEN fl_sla_violado = 1 THEN 1 ELSE 0 END) AS qt_sla_violado,
    CAST(100.0 * SUM(CASE WHEN fl_sla_violado = 0 THEN 1 ELSE 0 END)
         / NULLIF(COUNT(fl_sla_violado), 0) AS DECIMAL(5, 1)) AS pc_dentro_sla,
    CAST(AVG(qt_horas_resolucao) AS DECIMAL(10, 1)) AS qt_horas_media_resolucao
FROM dbo.vw_chamado_detalhado
GROUP BY ds_prioridade;
GO

-- 13. Tempo medio em cada status
CREATE OR ALTER VIEW dbo.vw_ind_tempo_por_status AS
SELECT
    ds_status_chamado,
    COUNT(*) AS qt_passagens,
    CAST(AVG(CAST(qt_tempo_status_minutos AS DECIMAL(12, 2))) / 60.0 AS DECIMAL(10, 1))
        AS qt_horas_media
FROM dbo.chamado_status_historico
GROUP BY ds_status_chamado;
GO

-- 14. Distribuicao das notas de CSAT
CREATE OR ALTER VIEW dbo.vw_ind_csat_notas AS
SELECT nr_score, COUNT(*) AS qt_avaliacoes
FROM dbo.csat_avaliacao
GROUP BY nr_score;
GO

-- 12. % SLA cumprido x violado por fila
CREATE OR ALTER VIEW dbo.vw_ind_sla_por_fila AS
SELECT
    nm_fila,
    COUNT(*) AS qt_chamados,
    SUM(CASE WHEN fl_sla_violado = 0 THEN 1 ELSE 0 END) AS qt_dentro_sla,
    SUM(CASE WHEN fl_sla_violado = 1 THEN 1 ELSE 0 END) AS qt_sla_violado,
    CAST(100.0 * SUM(CASE WHEN fl_sla_violado = 0 THEN 1 ELSE 0 END)
         / NULLIF(COUNT(fl_sla_violado), 0) AS DECIMAL(5, 1)) AS pc_dentro_sla
FROM dbo.vw_chamado_detalhado
GROUP BY nm_fila;
GO
