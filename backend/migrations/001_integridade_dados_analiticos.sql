-- Protege a fonte de dados e as tabelas analíticas contra registros duplicados (executar uma vez no SQL editor do supabase)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_cursos_escola_curso_mes_referencia'
    ) THEN
        ALTER TABLE cursos
            ADD CONSTRAINT uq_cursos_escola_curso_mes_referencia
            UNIQUE (escola, curso, mes_referencia);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_curso_escola_nome'
    ) THEN
        ALTER TABLE curso
            ADD CONSTRAINT uq_curso_escola_nome UNIQUE (escola_id, nome);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_historico_curso_mes_referencia'
    ) THEN
        ALTER TABLE historico_indicador
            ADD CONSTRAINT uq_historico_curso_mes_referencia
            UNIQUE (curso_id, mes_referencia);
    END IF;
END $$;
