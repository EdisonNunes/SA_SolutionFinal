-- Migração: Adicionar GRANTs para Data API (Supabase)
-- Conforme notificação do Supabase enviada em 2026-05-13
-- Prazo: 30/10/2026 (obrigatório em todos os projetos)

-- ====================================
-- TABELA: propostas
-- ====================================
GRANT SELECT ON public.propostas TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO service_role;

-- ====================================
-- TABELA: clientes
-- ====================================
GRANT SELECT ON public.clientes TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.clientes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.clientes TO service_role;

-- ====================================
-- TABELA: servicos
-- ====================================
GRANT SELECT ON public.servicos TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.servicos TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.servicos TO service_role;

-- ====================================
-- TABELA: itens_proposta
-- ====================================
GRANT SELECT ON public.itens_proposta TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.itens_proposta TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.itens_proposta TO service_role;

-- ====================================
-- TABELA: sasdata60
-- ====================================
GRANT SELECT ON public.sasdata60 TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sasdata60 TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sasdata60 TO service_role;

-- ====================================
-- NOTA: RLS (Row Level Security)
-- ====================================
-- Se você implementar RLS no futuro, adicione políticas específicas aqui.
-- Exemplo para tabela propostas com política baseada em usuário:
--
-- ALTER TABLE public.propostas ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "usuarios_autenticados_podem_ler" ON public.propostas
--   FOR SELECT TO authenticated USING (true);
-- CREATE POLICY "usuarios_autenticados_podem_escrever" ON public.propostas
--   FOR INSERT TO authenticated WITH CHECK (true);
