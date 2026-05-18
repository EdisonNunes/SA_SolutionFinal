-- Migração: adicionar relação entre relatório de compatibilidade química e proposta
-- Execute este script no banco de dados Supabase ou PostgreSQL associado.

ALTER TABLE public.sasdata60
    ADD COLUMN IF NOT EXISTS id_proposta integer NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema = 'public'
          AND table_name = 'sasdata60'
          AND constraint_name = 'fk_sasdata60_proposta'
    ) THEN
        ALTER TABLE public.sasdata60
            ADD CONSTRAINT fk_sasdata60_proposta FOREIGN KEY (id_proposta)
            REFERENCES public.propostas (id_proposta);
    END IF;
END$$;
