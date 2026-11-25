-- Chaves estrangeiras do banco de destino (schema dbo).
-- Relacoes inferidas pelos nomes das colunas e validadas nos dados extraidos (nenhum registro orfao).
-- Idempotente: so cria a constraint se ela ainda nao existir.
-- Ordem de carga (pais antes dos filhos): fila, sla, categoria, cliente_organizacao, analista,
-- solicitante, chamado, chamado_sla, chamado_status_historico, csat_avaliacao.

IF OBJECT_ID('dbo.FK_analista_id_fila_atual', 'F') IS NULL
    ALTER TABLE dbo.analista ADD CONSTRAINT FK_analista_id_fila_atual
        FOREIGN KEY (id_fila_atual) REFERENCES dbo.fila (id_fila);
GO

IF OBJECT_ID('dbo.FK_solicitante_id_cliente_organizacao', 'F') IS NULL
    ALTER TABLE dbo.solicitante ADD CONSTRAINT FK_solicitante_id_cliente_organizacao
        FOREIGN KEY (id_cliente_organizacao) REFERENCES dbo.cliente_organizacao (id_cliente_organizacao);
GO

IF OBJECT_ID('dbo.FK_chamado_id_analista_atual', 'F') IS NULL
    ALTER TABLE dbo.chamado ADD CONSTRAINT FK_chamado_id_analista_atual
        FOREIGN KEY (id_analista_atual) REFERENCES dbo.analista (id_analista);
GO

IF OBJECT_ID('dbo.FK_chamado_id_reporter', 'F') IS NULL
    ALTER TABLE dbo.chamado ADD CONSTRAINT FK_chamado_id_reporter
        FOREIGN KEY (id_reporter) REFERENCES dbo.solicitante (id_solicitante);
GO

IF OBJECT_ID('dbo.FK_chamado_id_categoria', 'F') IS NULL
    ALTER TABLE dbo.chamado ADD CONSTRAINT FK_chamado_id_categoria
        FOREIGN KEY (id_categoria) REFERENCES dbo.categoria (id_categoria);
GO

IF OBJECT_ID('dbo.FK_chamado_id_cliente_organizacao', 'F') IS NULL
    ALTER TABLE dbo.chamado ADD CONSTRAINT FK_chamado_id_cliente_organizacao
        FOREIGN KEY (id_cliente_organizacao) REFERENCES dbo.cliente_organizacao (id_cliente_organizacao);
GO

IF OBJECT_ID('dbo.FK_chamado_id_fila_atual', 'F') IS NULL
    ALTER TABLE dbo.chamado ADD CONSTRAINT FK_chamado_id_fila_atual
        FOREIGN KEY (id_fila_atual) REFERENCES dbo.fila (id_fila);
GO

IF OBJECT_ID('dbo.FK_chamado_sla_id_chamado', 'F') IS NULL
    ALTER TABLE dbo.chamado_sla ADD CONSTRAINT FK_chamado_sla_id_chamado
        FOREIGN KEY (id_chamado) REFERENCES dbo.chamado (id_chamado);
GO

IF OBJECT_ID('dbo.FK_chamado_sla_id_sla', 'F') IS NULL
    ALTER TABLE dbo.chamado_sla ADD CONSTRAINT FK_chamado_sla_id_sla
        FOREIGN KEY (id_sla) REFERENCES dbo.sla (id_sla);
GO

IF OBJECT_ID('dbo.FK_chamado_status_historico_id_chamado', 'F') IS NULL
    ALTER TABLE dbo.chamado_status_historico ADD CONSTRAINT FK_chamado_status_historico_id_chamado
        FOREIGN KEY (id_chamado) REFERENCES dbo.chamado (id_chamado);
GO

IF OBJECT_ID('dbo.FK_chamado_status_historico_id_analista_responsavel', 'F') IS NULL
    ALTER TABLE dbo.chamado_status_historico ADD CONSTRAINT FK_chamado_status_historico_id_analista_responsavel
        FOREIGN KEY (id_analista_responsavel) REFERENCES dbo.analista (id_analista);
GO

IF OBJECT_ID('dbo.FK_chamado_status_historico_id_fila', 'F') IS NULL
    ALTER TABLE dbo.chamado_status_historico ADD CONSTRAINT FK_chamado_status_historico_id_fila
        FOREIGN KEY (id_fila) REFERENCES dbo.fila (id_fila);
GO

IF OBJECT_ID('dbo.FK_csat_avaliacao_id_chamado', 'F') IS NULL
    ALTER TABLE dbo.csat_avaliacao ADD CONSTRAINT FK_csat_avaliacao_id_chamado
        FOREIGN KEY (id_chamado) REFERENCES dbo.chamado (id_chamado);
GO

IF OBJECT_ID('dbo.FK_csat_avaliacao_id_analista', 'F') IS NULL
    ALTER TABLE dbo.csat_avaliacao ADD CONSTRAINT FK_csat_avaliacao_id_analista
        FOREIGN KEY (id_analista) REFERENCES dbo.analista (id_analista);
GO
