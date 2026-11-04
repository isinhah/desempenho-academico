-- Permite que usuários autenticados tenham acesso à área administrativa
ALTER TABLE public.perfil_usuario
    DROP CONSTRAINT IF EXISTS ck_perfil_usuario_papel;

ALTER TABLE public.perfil_usuario
    ADD CONSTRAINT ck_perfil_usuario_papel
    CHECK (papel IN ('DECANO', 'COORDENADOR_CURSO', 'ADMINISTRADOR'));