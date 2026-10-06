-- Adequa a tabela existente de auditoria para registrar scores como números.
-- Execute uma vez nos bancos que já possuem a versão antiga da tabela.
ALTER TABLE log_auditoria
    ALTER COLUMN valor_antigo TYPE DOUBLE PRECISION
        USING NULLIF(valor_antigo::text, '')::DOUBLE PRECISION,
    ALTER COLUMN valor_novo TYPE DOUBLE PRECISION
        USING NULLIF(valor_novo::text, '')::DOUBLE PRECISION,
    ALTER COLUMN campo SET DEFAULT 'score',
    ALTER COLUMN data_hora SET DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS ix_log_auditoria_curso_data_hora
    ON log_auditoria (curso_id, data_hora DESC);
