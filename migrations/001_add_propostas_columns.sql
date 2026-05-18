-- Migração: adicionar colunas ausentes na tabela propostas
-- Execute este script no banco de dados Supabase ou PostgreSQL associado.

ALTER TABLE public.propostas
    ADD COLUMN IF NOT EXISTS status_rel_01 text NULL,
    ADD COLUMN IF NOT EXISTS local_realizacao text NULL,
    ADD COLUMN IF NOT EXISTS dt_agendada_01 date NULL,
    ADD COLUMN IF NOT EXISTS dt_emissao_rel_01 date NULL,
    ADD COLUMN IF NOT EXISTS motivo_cancelamento text NULL;
