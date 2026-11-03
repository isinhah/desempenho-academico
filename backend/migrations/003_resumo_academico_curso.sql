-- Resumo determinístico recalculado pelo ETL após a sincronização do histórico.
ALTER TABLE curso
    ADD COLUMN IF NOT EXISTS resumo_academico TEXT,
    ADD COLUMN IF NOT EXISTS resumo_referencia DATE,
    ADD COLUMN IF NOT EXISTS resumo_atualizado_em TIMESTAMPTZ;
