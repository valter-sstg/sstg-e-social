# 🚀 Guia de Instalação e Publicação — DRE - DRPS

**Versão:** 8.0
**Atualizado:** 14/07/2026
**Público:** Equipe SSTG (publicação) | Equipe Técnica (desenvolvimento local)

---

## 📋 Índice

1. [Como o Sistema Está Publicado Hoje](#como-o-sistema-está-publicado-hoje)
2. [Atualizar o Sistema (Fluxo de Publicação)](#atualizar-o-sistema-fluxo-de-publicação)
3. [Configuração de Secrets (Supabase)](#configuração-de-secrets-supabase)
4. [Executar Localmente (Opcional)](#executar-localmente-opcional)
5. [Backup e Recuperação de Dados](#backup-e-recuperação-de-dados)
6. [Gerenciamento de Usuários e Senhas](#gerenciamento-de-usuários-e-senhas)
7. [Troubleshooting de Publicação](#troubleshooting-de-publicação)

---

## ☁️ Como o Sistema Está Publicado Hoje

O DRE - DRPS já está em produção — **não é necessário instalar nada** para
o uso diário. A estrutura atual é:

| Componente | Onde está |
|------------|-----------|
| **Código-fonte** | GitHub — repositório `valter-sstg/sstg-e-social`, branch `main` |
| **Hospedagem do app** | Streamlit Cloud (plano gratuito), app `sstg-e-social`, arquivo principal `app.py` |
| **Banco de dados** | Supabase (PostgreSQL), plano gratuito |
| **Páginas de questionário/e-books** | GitHub Pages (`valter-sstg.github.io/sstg-e-social/`) |
| **Documentação** | Dentro do próprio app, módulo 📚 Documentação |

Este guia descreve como **atualizar** essa estrutura e, opcionalmente, como
**rodar uma cópia local** para testar alterações antes de publicar.

---

## 🔄 Atualizar o Sistema (Fluxo de Publicação)

Sempre que um arquivo do sistema é alterado (ex.: `app.py`, `db.py`,
`gerar_laudo.py`, `gerar_laudo_aep.py`, ou os próprios documentos `.md`/`.pdf`
deste módulo), o processo de publicação é:

### Passo 1: Preparar os arquivos

As versões atualizadas ficam reunidas em
`C:\Users\valte\Claude\upload_temp\` — esta pasta espelha o que precisa
estar no repositório GitHub.

### Passo 2: Subir para o GitHub

1. Acesse: `https://github.com/valter-sstg/sstg-e-social/upload/main`
2. Arraste os arquivos atualizados de `upload_temp\` para a área de upload
   (substituindo os arquivos existentes com o mesmo nome).
3. Role até o final da página e confirme o **commit** direto na branch `main`.

### Passo 3: Reiniciar o app no Streamlit Cloud

> ⚠️ O Streamlit Cloud **não reinicia automaticamente** ao detectar um novo
> commit — o reinício manual é obrigatório.

1. Acesse `https://share.streamlit.io` e localize o app `sstg-e-social`.
2. Clique no menu **"⋮"** → **"Reboot app"**.
3. Aguarde 1-2 minutos até o app voltar a responder.

### Passo 4: Validar

1. Abra a URL pública do app.
2. Confirme que o menu lateral mostra a versão esperada (rodapé "v8.0 — DRE
   - DRPS").
3. Teste rapidamente os módulos alterados (ex.: se atualizou a
   Documentação, abra **📚 Documentação** e confira os novos textos).

---

## 🔑 Configuração de Secrets (Supabase)

O app se conecta ao banco de dados Supabase usando duas credenciais,
configuradas como **Secrets** no Streamlit Cloud (não ficam no código):

1. Acesse `https://share.streamlit.io` → app `sstg-e-social` → **"⋮"** →
   **Settings** → **Secrets**.
2. Devem existir as chaves:

```toml
SUPABASE_URL = "https://xxxxxxxx.supabase.co"
SUPABASE_KEY = "chave-do-projeto-supabase"
```

> 🔒 Essas chaves dão acesso ao banco de dados de produção — trate-as como
> senha. Só altere se estiver migrando para um novo projeto Supabase.

---

## 💻 Executar Localmente (Opcional)

Útil para testar alterações **antes** de publicar (passo 2 do fluxo
acima).

### Pré-requisitos

- Python 3.9+ (`py --version`)
- Pasta do projeto: `C:\Users\valte\Claude`

### Passo 1: Instalar dependências

```bash
cd C:\Users\valte\Claude
py -m pip install --upgrade pip
py -m pip install streamlit pandas reportlab plotly supabase qrcode pillow
```

### Passo 2: Configurar acesso ao Supabase localmente

Crie o arquivo `C:\Users\valte\Claude\.streamlit\secrets.toml` (não é
versionado no Git) com as mesmas credenciais usadas em produção — ou de um
projeto Supabase de teste, se preferir não testar contra dados reais:

```toml
SUPABASE_URL = "https://xxxxxxxx.supabase.co"
SUPABASE_KEY = "chave-do-projeto-supabase"
```

### Passo 3: Rodar o app

```bash
py -m streamlit run app.py
```

O navegador abrirá em `http://localhost:8501`.

> ⚠️ Se estiver usando as **mesmas credenciais de produção**, qualquer
> alteração feita localmente (cadastro, respostas, laudos) afeta os dados
> reais. Para testes destrutivos, use um projeto Supabase separado.

---

## 💾 Backup e Recuperação de Dados

Diferente das versões antigas (CSV local), **todos os dados ficam no
Supabase** — não há arquivos locais para copiar.

### Backup manual (recomendado periodicamente)

1. No app, acesse **🔐 Admin SSTG (Gestão)** → aba **📋 Conferência e
   Correção**.
2. Abra o expander **💾 Backup**.
3. Baixe o arquivo ZIP gerado (contém um CSV por tabela: `acessos`,
   `respostas`, `respostas_aep`, `usuarios`, `laudos`).
4. Guarde o ZIP em um local seguro (ex.: Google Drive, OneDrive).

### Recuperação

Não há um botão de "restaurar" automático — em caso de perda de dados,
contate a equipe técnica para reimportar os CSVs do backup diretamente no
Supabase (SQL Editor ou importação de tabela).

### Hibernação do banco (plano gratuito)

O Supabase free tier "hiberna" o banco após ~7 dias sem uso. O app chama
`db.ping()` automaticamente ao iniciar para reativá-lo — a primeira
requisição após a hibernação pode demorar alguns segundos extra.

---

## 👥 Gerenciamento de Usuários e Senhas

| O quê | Onde |
|-------|------|
| Alterar a senha do administrador | Módulo Admin → opção "Alterar Senha" |
| Criar/gerenciar usuários operacionais da equipe SSTG | Módulo Admin → aba **👥 Usuários** (apenas administrador) |
| Gerar/redefinir senha de acesso do RH de uma empresa | Módulo Admin → aba **🔐 Segurança e Acesso RH** |

---

## 🆘 Troubleshooting de Publicação

### O app não atualizou depois do upload no GitHub

**Causa:** falta o reinício manual.

**Solução:** `share.streamlit.io` → app `sstg-e-social` → **"⋮"** →
**"Reboot app"**.

---

### Erro `ModuleNotFoundError` após o deploy

**Causa:** uma dependência usada no código não está listada no
`requirements.txt` do repositório.

**Solução:**
1. Adicione a dependência faltante ao `requirements.txt` (veja a lista
   completa em **🔧 GUIA_TECNICO.md**, seção "Dependências").
2. Suba o arquivo atualizado (Passo 2 do fluxo de publicação) e reinicie o app.

---

### Módulo "📚 Documentação" mostra "Arquivo não encontrado" / "PDF não disponível"

**Causa:** o arquivo `.md` ou `.pdf` correspondente não foi enviado junto
com `app.py` para o repositório — `DOC_DIR` é a mesma pasta do app, então
todos os documentos precisam estar lá.

**Solução:** confirme que os arquivos `.md` e `.pdf` estão em
`upload_temp\` antes do Passo 2 do fluxo de publicação.

---

### Erro de conexão com o banco (Supabase)

**Causa mais comum:** Secrets `SUPABASE_URL`/`SUPABASE_KEY` ausentes ou
incorretos, ou o projeto Supabase foi pausado/excluído.

**Solução:**
1. Verifique os Secrets do app (seção "Configuração de Secrets" acima).
2. Acesse o painel do Supabase e confirme que o projeto está ativo.

---

### Ver logs de erro do app publicado

1. `share.streamlit.io` → app `sstg-e-social` → **"⋮"** → **"Manage app"**.
2. O painel de logs mostra erros do Python em tempo real — útil para
   diagnosticar falhas após um deploy.

---

## 📞 Suporte Pós-Instalação

Para problemas técnicos, consulte **🔧 GUIA_TECNICO.md** (arquitetura,
banco de dados, troubleshooting técnico) ou contate a equipe responsável
pela manutenção do sistema.

---

**Guia de Instalação — DRE - DRPS v8.0**
