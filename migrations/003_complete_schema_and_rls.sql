-- ============================================================
-- SCRIPT SIMPLIFICADO - Apenas GRANTs para Data API
-- Data: 2026-05-13
-- Objetivo: Resolver erro 42501 após 30/10/2026
-- Nota: Colunas já existem, RLS não necessário
-- ============================================================

-- ============================================================
-- PASSO ÚNICO: CONCEDER PERMISSÕES DE DATA API (GRANTs)
-- ============================================================
-- Necessário para acesso via supabase-js/PostgREST a partir de 30/10/2026

-- PROPOSTAS
GRANT SELECT ON public.propostas TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO service_role;

-- CLIENTES
GRANT SELECT ON public.clientes TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.clientes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.clientes TO service_role;

-- SERVICOS
GRANT SELECT ON public.servicos TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.servicos TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.servicos TO service_role;

-- ITENS_PROPOSTA
GRANT SELECT ON public.itens_proposta TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.itens_proposta TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.itens_proposta TO service_role;

-- SASDATA60
GRANT SELECT ON public.sasdata60 TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sasdata60 TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sasdata60 TO service_role;

-- SEQUENCIA
GRANT SELECT ON public.sequencia TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sequencia TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sequencia TO service_role;

-- ============================================================
-- VERIFICAÇÃO
-- ============================================================

-- Para verificar se os GRANTs foram aplicados corretamente, execute:
-- SELECT grantee, privilege_type FROM information_schema.role_table_grants
-- WHERE table_name IN ('propostas', 'clientes', 'servicos', 'itens_proposta', 'sasdata60', 'sequencia')
-- ORDER BY table_name, grantee;

-- ============================================================
-- NOTAS IMPORTANTES
-- ============================================================

/*
✅ O QUE FOI FEITO:

1. ✅ Concedidos permissões de Data API (GRANTs) para todas as 6 tabelas:
   - SELECT para anon
   - SELECT, INSERT, UPDATE, DELETE para authenticated
   - SELECT, INSERT, UPDATE, DELETE para service_role

   Isso resolve o erro "42501 - Permission Denied" após 30/10/2026.

❌ O QUE NÃO FOI FEITO (por não ser necessário):

- Não adicionadas colunas (já existem)
- Não adicionada coluna user_id (não há necessidade de isolamento)
- Não ativado RLS (não há necessidade de isolamento)
- Não criadas políticas RLS (não há necessidade de isolamento)
- Não criados triggers (não há necessidade de isolamento)

⏰ DEADLINE:

- 30/05/2026: GRANTs obrigatórios para novos projetos
- 30/10/2026: GRANTs obrigatórios para TODOS projetos
- Data de execução: 13/05/2026 ✅ (ANTES DO PRAZO)

🔒 SEGURANÇA:

- GRANTs permitem acesso via Data API
- Sem RLS (dados compartilhados entre usuários)
- Aplicação pode acessar todas as tabelas normalmente
- Compatível com deadline Supabase

*/

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
