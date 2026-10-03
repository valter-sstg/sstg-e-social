# 🗄️ Plano de Migração — CSV → Supabase

**Versão:** 1.0  
**Data:** 08/05/2026  
**Status:** 📋 Planejado (próxima fase)  
**Prioridade:** Alta — elimina perda de dados em redeploys

---

## 🎯 Objetivo

Substituir o armazenamento em arquivos CSV (efêmeros no Streamlit Cloud) por um banco de dados **PostgreSQL na nuvem via Supabase**, garantindo persistência total dos dados independente de redeploys.

---

## ❓ Por que Supabase?

| Critério | CSV atual | Supabase |
|---|---|---|
| Sobrevive a redeploy | ❌ | ✅ |
| Acesso simultâneo seguro | ⚠️ filelock | ✅ nativo |
| Backup automático | ❌ manual | ✅ diário |
| Interface visual dos dados | ❌ | ✅ dashboard web |
| Custo | Grátis | Grátis (free tier) |
| Limite free tier | — | 500 MB, 50k linhas |
| Velocidade de leitura | Muito rápida (local) | Rápida (~50ms) |

---

## 📐 Mapeamento de Tabelas

| Arquivo CSV atual | Tabela Supabase | Descrição |
|---|---|---|
| `db_acessos_autorizados.csv` | `acessos` | Colaboradores autorizados + senha RH |
| `respostas_CNPJ_*.csv` | `respostas` | Respostas do questionário (todas as empresas numa só tabela) |
| `db_usuarios_operacionais.csv` | `usuarios` | Usuários operacionais do sistema |
| `db_admin_config.csv` | `config` | Configurações do admin (senha hash) |

### Tabela `acessos`
```sql
CREATE TABLE acessos (
    id              BIGSERIAL PRIMARY KEY,
    cpf             TEXT NOT NULL,
    empresa         TEXT,
    cnpj            TEXT NOT NULL,
    funcao          TEXT,
    departamento    TEXT,
    data_acesso_liberado TEXT,
    data_inicio_periodo  TEXT,
    data_fim_periodo     TEXT,
    status          TEXT DEFAULT 'Ativo',
    data_movimentacao    TEXT,
    motivo_movimentacao  TEXT,
    senha_rh_hash   TEXT,
    UNIQUE (cpf, cnpj)
);
```

### Tabela `respostas`
```sql
CREATE TABLE respostas (
    id          BIGSERIAL PRIMARY KEY,
    cpf_hash    TEXT NOT NULL,
    cnpj        TEXT NOT NULL,
    empresa     TEXT,
    funcao      TEXT,
    departamento TEXT,
    timestamp   TEXT,
    -- q1 a q40 + médias por dimensão
    -- (colunas geradas dinamicamente na migração)
    UNIQUE (cpf_hash, cnpj)
);
```

---

## 🔧 Dependências a adicionar

```
supabase>=2.0.0
```

---

## 📋 Etapas da Migração

### Fase 1 — Preparação (≈ 1h)
- [ ] Criar conta gratuita em https://supabase.com
- [ ] Criar novo projeto: `sstg-drps`
- [ ] Copiar `SUPABASE_URL` e `SUPABASE_KEY` (anon key)
- [ ] Criar as 4 tabelas via SQL Editor do Supabase
- [ ] Configurar secrets no Streamlit Cloud:
  ```toml
  # .streamlit/secrets.toml (local) e Streamlit Cloud Secrets
  SUPABASE_URL = "https://xxxx.supabase.co"
  SUPABASE_KEY = "eyJhbGci..."
  ```

### Fase 2 — Camada de acesso (≈ 3h)
- [ ] Criar `db.py` com funções que substituem CSV:
  ```python
  from supabase import create_client
  import streamlit as st

  @st.cache_resource
  def get_supabase():
      return create_client(
          st.secrets["SUPABASE_URL"],
          st.secrets["SUPABASE_KEY"]
      )

  def carregar_acessos() -> pd.DataFrame:
      sb = get_supabase()
      res = sb.table("acessos").select("*").execute()
      return pd.DataFrame(res.data) if res.data else pd.DataFrame()

  def salvar_acesso(registro: dict):
      sb = get_supabase()
      sb.table("acessos").upsert(registro).execute()
  ```
- [ ] Substituir `carregar_dados(ARQUIVO_ACESSOS)` por `carregar_acessos()`
- [ ] Substituir `df.to_csv(ARQUIVO_ACESSOS, ...)` por `salvar_acesso(...)`
- [ ] Repetir para todas as tabelas
- [ ] Remover `filelock` das operações (Supabase é thread-safe nativamente)

### Fase 3 — Migração dos dados existentes (≈ 30min)
- [ ] Exportar backup ZIP via botão "💾 Backup Completo"
- [ ] Importar CSVs para as tabelas Supabase via dashboard web
- [ ] Verificar contagem de registros antes e depois

### Fase 4 — Testes (≈ 2h)
- [ ] Testar todos os módulos localmente com Supabase
- [ ] Testar cadastro, resposta de questionário, geração de laudo
- [ ] Testar acesso simultâneo (2+ usuários)
- [ ] Deploy no Streamlit Cloud e teste final

### Fase 5 — Go-live
- [ ] Confirmar que todos os dados estão no Supabase
- [ ] Remover código CSV legado
- [ ] Atualizar documentação

---

## ⚠️ Pontos de atenção

### Segurança
- `SUPABASE_KEY` nunca vai para o GitHub — somente em `secrets.toml` (local) e Streamlit Cloud Secrets
- Habilitar **Row Level Security (RLS)** no Supabase para proteção extra
- Manter hashes de CPF e senhas — nenhuma mudança na política de privacidade

### Rollback
- Manter o código CSV como fallback durante a transição
- Testar em branch separado antes de merge no main
- Só remover código CSV após 30 dias de Supabase estável

### Free tier Supabase — limites
| Recurso | Limite free | Nossa necessidade estimada |
|---|---|---|
| Armazenamento | 500 MB | < 10 MB |
| Linhas por tabela | Ilimitado | < 10.000 |
| API requests | 500k/mês | < 50k/mês |
| Projetos ativos | 2 | 1 |
| Pausa após inatividade | 7 dias sem uso | App em uso regular |

> ⚠️ O projeto Supabase hiberna após 7 dias sem uso no free tier. O primeiro acesso após hibernação leva ~30s para reativar. Considere fazer uma requisição de "ping" no startup do app para acordar o banco.

---

## 🕐 Estimativa de esforço

| Fase | Tempo estimado |
|---|---|
| Preparação e criação de tabelas | 1 hora |
| Desenvolvimento da camada de acesso | 3 horas |
| Migração dos dados | 30 minutos |
| Testes e ajustes | 2 horas |
| **Total** | **~7 horas** |

---

## 📅 Quando fazer?

**Pré-requisito:** Ter dados cadastrados que valham a pena migrar (evitar migrar base vazia).

**Sequência recomendada:**
1. Recadastrar as empresas e colaboradores no sistema atual (CSV)
2. Usar o sistema normalmente por alguns dias
3. Quando houver dados relevantes → agendar sessão de migração Supabase
4. Fazer backup ZIP antes de iniciar a migração

---

**Documento criado em:** 08/05/2026  
**Próxima revisão:** antes de iniciar a Fase 1
