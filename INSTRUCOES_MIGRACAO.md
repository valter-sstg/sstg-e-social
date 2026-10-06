# Como Executar a Migração DRE-DRPS

**Status:** 🔴 URGENTE — Aplicação indisponível  
**Tempo estimado:** 5 minutos  
**Requisitos:** Acesso ao console Supabase com conta `valter@sstgocupacional.com.br`

---

## Passo 1: Acessar o Console Supabase

1. Abra no navegador: **https://app.supabase.com**
2. Clique em **"Sign in"** (ou está já conectado?)
3. Se não estiver: use email `valter@sstgocupacional.com.br`

---

## Passo 2: Selecionar o Projeto Correto

1. Procure na lista de projetos por: **`sstg-app`**
   - Este é o projeto Supabase que a SSTG App e DRE-DRPS compartilham
2. Clique para abrir

---

## Passo 3: Abrir o SQL Editor

No painel esquerdo, localize e clique em:
- **"SQL Editor"** (ícone de chaves/comando)

---

## Passo 4: Criar uma Nova Query

1. Clique no botão **"+ New query"** (verde, no canto superior)
2. Uma aba em branco vai abrir

---

## Passo 5: Colar o SQL

Abra o arquivo `SUPABASE_MIGRATION_COMPLETA.sql` e:

1. **Copie TODO o conteúdo** do arquivo
2. **Cole** na aba branca que abriu no Supabase (Ctrl+V ou Cmd+V)

### Atalho Rápido:
- Arquivo está em: `C:\CLAUDE CODE\CHECKLIST SST\sstg-e-social\SUPABASE_MIGRATION_COMPLETA.sql`
- Ou use o caminho relativo: `sstg-e-social/SUPABASE_MIGRATION_COMPLETA.sql`

---

## Passo 6: Executar

1. Procure o botão **"Execute"** (verde, no canto superior direito)
2. Clique
3. Aguarde a conclusão (deve levar 5-10 segundos)

### O que você verá:
- ✅ **Sucesso:** Nenhuma mensagem de erro, só a confirmação
- ❌ **Erro:** Se houver erro tipo `relation "public.acessos" already exists`, significa que as tabelas já foram criadas (OK, tudo funciona)

---

## Passo 7: Validar

Para confirmar que tudo funcionou:

1. No painel esquerdo, clique em **"Database"**
2. Clique em **"Tables"**
3. Procure pelas 8 tabelas novas:
   - [ ] `acessos`
   - [ ] `respostas`
   - [ ] `respostas_aep`
   - [ ] `ajustes_aep`
   - [ ] `ajustes_drps`
   - [ ] `laudos`
   - [ ] `usuarios`
   - [ ] `config`

Se todas aparecerem, **está pronto! 🎉**

---

## Passo 8: Redeployar DRE-DRPS

Após criar as tabelas, a aplicação DRE-DRPS no Streamlit Cloud deve voltar online automaticamente em alguns minutos, ou:

1. Faça push de alguma mudança no repositório `valter-sstg/sstg-e-social`
2. Ou acesse: https://sstg-drps.streamlit.app

---

## Se Houver Problemas

### Erro: "relation already exists"
- **Significa:** As tabelas já existem (criadas em uma tentativa anterior)
- **Ação:** Continuar para Passo 7 (Validar)

### Erro: "permission denied"
- **Significa:** A chave `SUPABASE_KEY` não tem permissões de escrita
- **Ação:** Contato necessário — usar `SUPABASE_SERVICE_ROLE_KEY` em vez disso

### App ainda não funciona após tabelas criadas
- **Aguarde 5 minutos** (Streamlit Cloud redeploy é automático)
- **Ou force redeploy:** Push uma mudança para `sstg-e-social`

---

## Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `SUPABASE_MIGRATION_COMPLETA.sql` | SQL com 8 tabelas para copiar/colar |
| `execute_migration_via_api.py` | (Alternativo) Script Python para executar direto |
| `.streamlit/secrets.toml` | Credenciais Supabase (já criado) |
| `INSTRUCOES_MIGRACAO.md` | Este arquivo |

---

## Conclusão

Após concluir estes passos, o DRE-DRPS volta online em:
- **URL:** https://sstg-drps.streamlit.app
- **Tempo:** ~5 minutos após execução do SQL

**Próximas etapas:** Resolver D-72 (cadastro mestre único) para evitar duplicação de dados entre SSTG App, DRE-DRPS e SSTG LIP.

---

**Data:** 2026-10-05  
**Versão:** 1.0  
**Status:** 📝 Passo a passo pronto
