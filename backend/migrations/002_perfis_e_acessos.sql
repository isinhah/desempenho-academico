-- Perfis de acesso da aplicação.
-- Executar uma vez no SQL Editor do Supabase, após a migration 001.

CREATE TABLE IF NOT EXISTS public.perfil_usuario (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    papel TEXT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_perfil_usuario_papel
        CHECK (papel IN ('DECANO', 'COORDENADOR_CURSO'))
);

-- Um coordenador pode acompanhar um ou mais cursos.
CREATE TABLE IF NOT EXISTS public.usuario_curso (
    usuario_id UUID NOT NULL REFERENCES public.perfil_usuario(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES public.curso(id) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usuario_id, curso_id)
);

CREATE INDEX IF NOT EXISTS ix_usuario_curso_curso_id
    ON public.usuario_curso (curso_id);
