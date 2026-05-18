# 📋 Guia de Execução - Script SQL Simplificado

## 🎯 Resumo do que o Script Faz

Este script SQL **simplificado** resolve apenas o problema crítico do Supabase Data API:

1. ✅ **Concede permissões de Data API (GRANTs)** para todas as 6 tabelas
2. ❌ **Não adiciona colunas** (já existem)
3. ❌ **Não ativa RLS** (não há necessidade de isolamento)
4. ❌ **Não cria políticas** (não há necessidade de isolamento)
5. ❌ **Não cria triggers** (não há necessidade de isolamento)

---

## 📝 Passo a Passo de Execução

### **Passo 1: Acessar o Supabase Dashboard**
1. Abra seu navegador e vá para [app.supabase.com](https://app.supabase.com)
2. Faça login com suas credenciais
3. Selecione seu projeto

### **Passo 2: Ir ao SQL Editor**
```
Navegação:
  Dashboard → SQL Editor (menu esquerdo)
```

### **Passo 3: Criar uma Nova Query**
1. Clique no botão **"New Query"** (ou **"+"**)
2. Você verá um editor em branco

### **Passo 4: Copiar o Script SQL**
1. Abra o arquivo: `migrations/003_complete_schema_and_rls.sql`
2. **Copie TODO o conteúdo** (Ctrl+A → Ctrl+C)
3. Cole no editor do Supabase (Ctrl+V)

### **Passo 5: Executar o Script**
1. Clique no botão **"Run"** (ou pressione Ctrl+Enter)
2. Aguarde a execução (normalmente < 10 segundos)
3. Você verá mensagens de sucesso para cada comando

### **Passo 6: Verificar Execução**
Após a execução, você deve ver no painel de "Results":
- ✅ Múltiplas linhas de sucesso (sem erros)
- ℹ️ Mensagens de tipo `GRANT` são normais

---

## 🔍 Como Verificar que Tudo Funcionou

### **Verificação Única: GRANTs Aplicados**
Execute esta query no SQL Editor:
```sql
SELECT grantee, privilege_type, table_name
FROM information_schema.role_table_grants
WHERE table_name IN ('propostas', 'clientes', 'servicos', 'itens_proposta', 'sasdata60', 'sequencia')
ORDER BY table_name, grantee;
```

Você deve ver para cada tabela:
- `anon` com `SELECT`
- `authenticated` com `SELECT, INSERT, UPDATE, DELETE`
- `service_role` com `SELECT, INSERT, UPDATE, DELETE`

---

## ⚠️ Possíveis Erros e Soluções

### **Erro: "Already exists"**
```
Error: GRANT SELECT ON public.propostas TO anon... already exists
```
✅ **Solução:** Normalmente não é erro. GRANTs são idempotentes. Execute novamente o script sem problemas.

### **Erro: "Permission denied"**
```
Error: permission denied for schema public
```
❌ **Solução:** Você não tem permissão no Supabase.
- Verifique se está logado na conta correta
- Verifique se é administrador do projeto
- Tente novamente

### **Erro: "Table does not exist"**
```
Error: relation "public.propostas" does not exist
```
❌ **Solução:** A tabela não existe ainda.
- Crie as tabelas primeiro (consulte o schema no crud.py)
- Ou execute este script após criar as tabelas

### **Script Demora Muito**
Se o script levar > 1 minuto:
- ✅ Normal em bancos muito grandes. Aguarde a conclusão.
- Se tiver timeout: execute em partes (comentar seções).

---

## 📌 O Que Cada Parte do Script Faz

### **GRANTs (Única Parte)**
```sql
GRANT SELECT ON public.propostas TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO service_role;
```
Permite que o app acesse as tabelas via supabase-js após 30/10/2026.

---

## 💡 Dicas

- **Script seguro**: Pode executar múltiplas vezes (GRANTs são idempotentes)
- **Sem downtime**: Execução instantânea no banco
- **Sem mudanças no código**: Seu app continua funcionando normalmente
- **Backup opcional**: GRANTs são fáceis de reverter se necessário

---

## 📅 Timeline

| Data | Evento |
|------|--------|
| 🔵 13/05/2026 | ✅ Você executou este script |
| 🟡 30/05/2026 | GRANTs obrigatórios para **novos** projetos |
| 🔴 30/10/2026 | GRANTs obrigatórios para **TODOS** projetos |

**Status:** ✅ Você está ADIANTADO!

---

## ✅ Checklist Final

- [ ] Arquivo `migrations/003_complete_schema_and_rls.sql` copiado
- [ ] Conteúdo colado no Supabase SQL Editor
- [ ] Botão "Run" clicado
- [ ] Execução concluída sem erros
- [ ] Query de verificação executada
- [ ] GRANTs confirmados para todas as 6 tabelas
- [ ] App testada (criar/editar proposta funciona)

---

## 💡 Próximos Passos

1. Execute o script (passos acima)
2. Verifique os GRANTs com a query de verificação
3. Teste a app: `streamlit run main.py`
4. Crie uma proposta para confirmar que funciona
5. Pronto! Seu app está compatível com o deadline

---

## ❓ Dúvidas Frequentes

**P: Preciso executar o script novamente?**
R: Não. Uma vez executado, os GRANTs são permanentes. Executar novamente não causa danos.

**P: O app vai quebrar após executar?**
R: Não. Os GRANTs só permitem acesso que já funcionava. Seu app continua funcionando normalmente.

**P: Quanto tempo leva?**
R: < 10 segundos no Supabase. Seu app não é afetado.

**P: Posso executar apenas parte do script?**
R: Sim, mas execute tudo para garantir consistência.

**P: E se eu quiser reverter?**
R: GRANTs podem ser removidos com `REVOKE`, mas normalmente não é necessário.

---

## 📖 Documentação Completa

Veja: `migrations/QUICK_START.txt`
├─ Resumo visual
├─ Timeline
├─ Checklist
└─ Dicas rápidas

---

**Última atualização:** 2026-05-13
**Script versão:** 003 (simplificado)
**Status:** ✅ Pronto para execução

## 🔍 Como Verificar que Tudo Funcionou

### **Verificação 1: Colunas Adicionadas**
Execute esta query no SQL Editor:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'propostas' 
ORDER BY ordinal_position;
```

Você deve ver as colunas:
- `status_rel_01` (text)
- `local_realizacao` (text)
- `dt_agendada_01` (date)
- `dt_emissao_rel_01` (date)
- `motivo_cancelamento` (text)
- `user_id` (uuid)

### **Verificação 2: RLS Ativado**
Execute esta query:
```sql
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('propostas', 'clientes', 'itens_proposta');
```

Você deve ver `rowsecurity = true` para essas 3 tabelas.

### **Verificação 3: Políticas RLS**
Execute esta query:
```sql
SELECT * FROM pg_policies WHERE tablename IN ('propostas', 'clientes', 'itens_proposta');
```

Você verá todas as políticas criadas (auth_can_read, auth_can_create, etc).

### **Verificação 4: Triggers**
Execute esta query:
```sql
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_name LIKE 'trg_set_user_id%';
```

Você verá os 3 triggers para preencher user_id.

---

## ⚠️ Possíveis Erros e Soluções

### **Erro: "Already exists"**
```
Error: CREATE POLICY IF NOT EXISTS "auth_can_read_own_propostas"... already exists
```
✅ **Solução:** Normalmente não é erro. O `CREATE POLICY IF NOT EXISTS` impede duplicação. Execute novamente o script sem problemas.

### **Erro: "Permission denied"**
```
Error: permission denied for schema public
```
❌ **Solução:** Você não tem permissão no Supabase. 
- Verifique se está logado na conta correta
- Verifique se é administrador do projeto
- Tente novamente

### **Erro: "Table does not exist"**
```
Error: relation "public.propostas" does not exist
```
❌ **Solução:** A tabela não existe ainda.
- Crie as tabelas primeiro (consulte o schema no crud.py)
- Ou execute este script após criar as tabelas

### **Script Demora Muito**
Se o script levar > 2 minutos:
- ✅ Normal em bancos muito grandes. Aguarde a conclusão.
- Se tiver timeout: execute em partes (comentar seções).

---

## 🔐 O Que Cada Parte do Script Faz

### **Parte 1: Adicionar Colunas**
```sql
ALTER TABLE public.propostas
    ADD COLUMN IF NOT EXISTS status_rel_01 text NULL,
    ...
```
Adiciona as 5 colunas que o app precisa.

### **Parte 2: Adicionar user_id**
```sql
ALTER TABLE public.propostas
    ADD COLUMN IF NOT EXISTS user_id uuid NULL;
```
Necessário para RLS saber a qual usuário cada registro pertence.

### **Parte 3: GRANTs (Data API)**
```sql
GRANT SELECT ON public.propostas TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.propostas TO authenticated;
```
Permite que o app acesse as tabelas via supabase-js após 30/10/2026.

### **Parte 4: Ativar RLS**
```sql
ALTER TABLE public.propostas ENABLE ROW LEVEL SECURITY;
```
Ativa o filtro de segurança em nível de linha.

### **Parte 5: Políticas RLS**
```sql
CREATE POLICY "auth_can_read_own_propostas" ON public.propostas
    FOR SELECT TO authenticated 
    USING (auth.uid() = user_id OR user_id IS NULL);
```
Define quem pode fazer o quê (SELECT, INSERT, UPDATE, DELETE).

### **Parte 6: Funções + Triggers**
```sql
CREATE OR REPLACE FUNCTION fn_set_user_id_propostas()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id IS NULL THEN
        NEW.user_id := auth.uid();
    END IF;
    RETURN NEW;
END;
$$
```
Preenche automaticamente `user_id` quando um novo registro é inserido.

---

## 📌 Próximos Passos no Código Python

### **1. Atualizar crud.py (opcional)**
Se quiser passivamente o `user_id`, deixe o Trigger cuidar. Se quiser explícito:

```python
def criar_proposta(dados: dict, user_id: str = None) -> int:
    if user_id is None:
        user_id = get_current_user_id()  # Sua função de autenticação
    dados["user_id"] = user_id
    res = supabase.table("propostas").insert(dados).execute()
    return res.data[0]["id_proposta"]
```

### **2. Atualizar proposta.py (opcional)**
Se quiser filtrar por usuário:

```python
# Em vez de buscar TODAS as propostas:
# propostas = buscar_propostas(filtro)

# Filtre por usuário (se implementado):
# propostas = supabase.table("propostas")\
#     .select("*")\
#     .eq("user_id", get_current_user())\
#     .order("num_proposta", desc=True)\
#     .execute().data
```

### **3. Testar a Aplicação**
1. Execute `streamlit run main.py`
2. Crie uma nova proposta
3. Verifique no Supabase Dashboard se `user_id` foi preenchido
4. Edite e salve propostas normalmente

---

## 🛡️ Segurança

### **O que RLS Protege:**

| Operação | Anônimo | Autenticado | Service Role |
|----------|---------|------------|--------------|
| SELECT   | ❌ Bloqueado | ✅ Seus dados | ✅ Tudo |
| INSERT   | ❌ Bloqueado | ✅ Com seu user_id | ✅ Tudo |
| UPDATE   | ❌ Bloqueado | ✅ Seus dados | ✅ Tudo |
| DELETE   | ❌ Bloqueado | ✅ Seus dados | ✅ Tudo |

### **Exemplo Prático:**

**Usuário A** tenta ver proposta de **Usuário B**:
```python
supabase.table("propostas").select("*").execute()
```

✅ **Com RLS:** Retorna APENAS propostas onde `user_id = auth.uid()` (Usuário A)  
❌ **Sem RLS:** Retornaria TODAS as propostas (inseguro!)

---

## 📅 Timeline

| Data | Evento |
|------|--------|
| 🔵 13/05/2026 | ✅ Você executou este script |
| 🟡 30/05/2026 | GRANTs obrigatórios para **novos** projetos |
| 🔴 30/10/2026 | GRANTs obrigatórios para **TODOS** projetos |

**Status:** ✅ Você está ADIANTADO! Seu app está seguro e compatível.

---

## 💡 Dúvidas Frequentes

**P: Preciso executar o script novamente?**  
R: Não. Uma vez executado, as mudanças são permanentes. Executar novamente não causa danos (usa `IF NOT EXISTS`).

**P: Posso executar apenas parte do script?**  
R: Sim, mas não é recomendado. Execute tudo de uma vez para garantir consistência.

**P: O app vai quebrar após executar?**  
R: Não. O script é backward-compatible. Seu app continua funcionando normalmente.

**P: E se eu quiser rollback?**  
R: Difícil sem backup. GRANTs e RLS são fáceis de reverter, mas colunas adicionadas são permanentes. Sempre faça backup antes!

**P: Preciso mudar a senha ou chaves de API?**  
R: Não. Segurança de autenticação é separada de RLS.

---

## ✅ Checklist Final

- [ ] Arquivo `migrations/003_complete_schema_and_rls.sql` criado
- [ ] Copiei TODO o conteúdo para o Supabase SQL Editor
- [ ] Cliquei em "Run" e aguardei conclusão
- [ ] Executei as 4 verificações acima
- [ ] Não há erros no painel de resultados
- [ ] Testei a aplicação (criar e editar proposta)
- [ ] Verifiquei se `user_id` foi preenchido no banco

---

## 📞 Suporte

Se encontrar erros:
1. Copie a mensagem de erro exata
2. Verifique o contexto no script SQL (linha do erro)
3. Consulte a documentação do Supabase: https://supabase.com/docs
4. Ou execute o script em partes para isolar o problema

---

**Última atualização:** 2026-05-13  
**Script versão:** 003  
**Status:** ✅ Pronto para execução
