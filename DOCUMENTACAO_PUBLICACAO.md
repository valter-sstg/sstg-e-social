# 📚 Documentação de Publicação — SSTG - DRPS v6.2

**Versão:** 2.1  
**Data:** 07/05/2026  
**Status:** ✅ Publicado e Operacional  
**URL:** https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app

---

## 📋 Índice

1. [Resumo Executivo](#resumo-executivo)
2. [Novidades da Versão 6.2](#novidades-da-versão-62)
3. [Recursos e Sistemas Utilizados](#recursos-e-sistemas-utilizados)
4. [Arquitetura da Publicação](#arquitetura-da-publicação)
5. [Processo de Deploy](#processo-de-deploy)
6. [Configurações Realizadas](#configurações-realizadas)
7. [Verificação e Validação](#verificação-e-validação)
8. [Troubleshooting](#troubleshooting)
9. [Manutenção e Atualizações](#manutenção-e-atualizações)
10. [Histórico de Versões](#histórico-de-versões)

---

## 📌 Resumo Executivo

O SSTG - DRPS v6.2 está publicado na plataforma **Streamlit Cloud**, acessível online de qualquer dispositivo com internet. O sistema oferece três módulos integrados: questionário para colaboradores, gestão para RH e painel administrativo completo.

### Dados da Publicação

| Campo | Valor |
|-------|-------|
| **Plataforma** | Streamlit Cloud (PaaS) |
| **Repositório** | GitHub — valter-sstg/sstg-e-social |
| **URL Pública** | https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app |
| **Versão** | 6.2 |
| **Protocolo** | COPSOQ III — 40 questões / 8 dimensões |
| **Status** | Operacional e testado |
| **SSL/HTTPS** | Ativo (automático pelo Streamlit Cloud) |
| **Custo** | Gratuito (tier community) |

---

## 🆕 Novidades da Versão 6.2

### Melhorias no Questionário

| # | Item | Descrição |
|---|------|-----------|
| 1 | **Wizard de Navegação** | Substituição de `st.tabs` por fluxo guiado — uma demanda por vez |
| 2 | **Botão "Próxima Demanda ▶"** | Só avança se todas as perguntas do bloco atual estão respondidas |
| 3 | **Botão "◀ Demanda Anterior"** | Retorna ao bloco anterior restaurando as respostas já dadas |
| 4 | **Cache `respostas_salvas`** | Persiste respostas no `session_state` ao navegar entre blocos (corrige perda de respostas) |
| 5 | **Progresso por bloco** | Barra no topo indicando "Bloco X de 8 — Nome da Demanda" |
| 6 | **Progresso geral** | Barra no rodapé indicando "X de 40 perguntas respondidas" |
| 7 | **Anti-contaminação** | Keys de `st.radio` prefixadas com CPF — impede interferência entre respondentes |

### Documentação e QR Code

| # | Item | Descrição |
|---|------|-----------|
| 1 | **POP 020 na Aba Documentação** | Tutorial visual tela a tela disponível para leitura e download |
| 2 | **Visualizador PDF embutido** | PyMuPDF renderiza páginas como imagem — compatível com todos os browsers |
| 3 | **QR Code ampliado** | Tamanho aumentado 150% (200 → 500 px) |
| 4 | **Fonte do nome da empresa** | Aumentada para 72pt com quebra automática de linha para nomes longos |
| 5 | **Imagem dinâmica** | Altura calculada automaticamente conforme número de linhas do nome |

### Novidades da Versão 6.1 (referência)

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 1 | **Módulo RH** | Login com CNPJ + senha, dashboard de respostas, QR Code |
| 2 | **Senhas de Acesso RH** | Geradas automaticamente no cadastro com `secrets` module |
| 3 | **Aba Segurança e Acesso RH** | Admin pode redefinir senha de qualquer empresa |
| 4 | **Zona de Perigo expandida** | Exclusão individual de empresa com contadores e confirmação |
| 5 | **QR Code profissional** | Imagem com WhatsApp e E-mail integrados |
| 6 | **SHARE_URL** | URL pública separada de APP_URL para compartilhamento externo |
| 7 | **6 abas no Admin** | Abas de Segurança RH e Documentação adicionadas |

---

## 🔧 Recursos e Sistemas Utilizados

### 1. Streamlit Cloud

| Aspecto | Detalhe |
|--------|---------|
| **Tipo** | Platform as a Service (PaaS) |
| **Custo** | Gratuito (tier community) |
| **Uptime** | 99.9% SLA |
| **SSL/TLS** | Incluído automaticamente |
| **Deploy** | Automático via push no GitHub |
| **Dados** | Persistidos em `./data/` |

### 2. GitHub

| Aspecto | Detalhe |
|--------|---------|
| **Repositório** | valter-sstg/sstg-e-social |
| **Visibilidade** | Público (dados sensíveis não versionados) |
| **Branch principal** | `main` |
| **Deploy trigger** | Push automático → Streamlit Cloud redeploy |

### 3. Dependências Python

| Biblioteca | Versão | Uso |
|-----------|--------|-----|
| streamlit | ≥1.28.0 | Interface web |
| pandas | ≥2.0.0 | Manipulação de dados CSV |
| reportlab | ≥4.0.0 | Geração de laudos PDF |
| pillow | ≥10.0.0 | Composição de imagens |
| qrcode[pil] | ≥7.4.2 | Geração de QR Codes |
| pymupdf | ≥1.23.0 | Visualizador PDF página a página (POP 020) |

---

## 🏗️ Arquitetura da Publicação

```
┌─────────────────────────────────────────────────────────────┐
│                   USUÁRIOS                                  │
│  Colaboradores │ RH das Empresas │ Admin SSTG              │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS (qualquer dispositivo)
┌────────────────▼────────────────────────────────────────────┐
│                STREAMLIT CLOUD                              │
│  URL: sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Python 3.11 + app.py (3 módulos)                  │   │
│  │  • 📋 Questionário Psicossocial                     │   │
│  │  • 📊 Gestão das Respostas (RH)                    │   │
│  │  • 🔐 Admin SSTG (Gestão) — 6 abas                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Armazenamento ./data/                              │   │
│  │  • db_acessos_autorizados.csv                       │   │
│  │  • respostas_CNPJ_*.csv                             │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────┘
                 │ Deploy automático (push)
┌────────────────▼────────────────────────────────────────────┐
│                   GITHUB                                    │
│  Repositório: valter-sstg/sstg-e-social                 │
│  Branch: main                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Processo de Deploy

### Deploy Inicial

```bash
# 1. Clonar repositório
git clone https://github.com/valter-sstg/sstg-e-social.git
cd sstg-e-social

# 2. Conectar no Streamlit Cloud (via interface web)
# → share.streamlit.io → New App → selecionar repo → app.py → Deploy

# 3. Atualizar SHARE_URL com a URL gerada
# Editar app.py → SHARE_URL = "https://url-gerada.streamlit.app"
git add app.py
git commit -m "Configura SHARE_URL de produção"
git push
```

### Atualizações (Manutenção)

```bash
# 1. Fazer alterações locais
# 2. Testar localmente: streamlit run app.py
# 3. Commit e push
git add .
git commit -m "Descrição da alteração"
git push origin main
# → Streamlit Cloud redeploy automático em ~2-3 minutos
```

---

## ⚙️ Configurações Realizadas

### app.py — Variáveis Principais

```python
# Raiz do projeto (automático, não editar)
DOC_DIR = os.path.dirname(os.path.abspath(__file__))

# Detecção de ambiente
IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true'

# URL de compartilhamento (sempre Streamlit Cloud)
SHARE_URL = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"

# Senha admin
SENHA_ADMIN = "sstg2025"  # ← Alterar em produção
```

### requirements.txt

```
streamlit>=1.28.0
pandas>=2.0.0
reportlab>=4.0.0
pillow>=9.0.0
qrcode[pil]>=7.4.2
```

### .streamlit/config.toml

```toml
[theme]
primaryColor = "#5A9F62"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#282C5B"
font = "sans serif"
```

---

## ✅ Verificação e Validação

### Checklist Pós-Deploy

- [ ] URL pública acessível
- [ ] App carrega sem erros
- [ ] Login admin funciona
- [ ] Cadastro de empresa gera senha RH
- [ ] Login RH funciona com CNPJ + senha
- [ ] Questionário acessível via link com `?cnpj=`
- [ ] QR Code gerado é escaneável
- [ ] Links WhatsApp e E-mail funcionam
- [ ] Documentação carrega sem "Arquivo não encontrado"
- [ ] Zona de Perigo requer senha admin
- [ ] Exclusão de empresa remove dados corretamente

### Testes de Segurança

- [ ] RH não consegue ver dados de outra empresa
- [ ] Senha incorreta bloqueia acesso RH
- [ ] Senha incorreta bloqueia Zona de Perigo
- [ ] CPF hash nas respostas (não texto puro)
- [ ] Senha RH armazenada como hash

---

## 🔍 Troubleshooting

### App não carrega (Streamlit Cloud)

1. Verificar logs no painel do Streamlit Cloud
2. Verificar se `requirements.txt` inclui todas as dependências
3. Verificar se `app.py` não tem erros de sintaxe
4. Forçar redeploy: **Manage app → Reboot app**

### Dados não persistem após redeploy

O Streamlit Cloud **não garante persistência** de dados entre reboots em planos gratuitos. Para produção com dados críticos:
- Usar Google Drive Desktop localmente
- Ou exportar dados periodicamente via CSV

### Link de compartilhamento não funciona

Verificar se `SHARE_URL` em `app.py` está correto e foi commitado.

### "Arquivo não encontrado" na documentação

Verificar se os `.md` estão na **raiz do repositório** (não em subpastas). O sistema resolve o caminho via `__file__` automaticamente.

### QR Code não gera

Verificar se `pillow` e `qrcode[pil]` estão em `requirements.txt` e foram instalados no Cloud.

---

## 🔄 Manutenção e Atualizações

### Fluxo de Atualização

```
Desenvolvimento local
       ↓
Teste: streamlit run app.py
       ↓
git commit + git push
       ↓
Streamlit Cloud redeploy automático (~3 min)
       ↓
Validar na URL de produção
```

### Backup de Dados

1. Admin → Conferência → **⬇️ Baixar lista filtrada (.csv)**
2. Admin → Resultados → selecionar empresa → **⬇️ Baixar resultados (.csv)**
3. Repetir para cada empresa

### Comunicação de Atualizações

Ao publicar versão com mudanças significativas:
1. Atualizar documentação (`.md` na raiz)
2. Comunicar ao RH das empresas se houver mudança de fluxo
3. Gerar novas senhas RH se necessário (Aba Segurança)

---

## 📜 Histórico de Versões

### v6.2 — 07/05/2026
- ✨ Novo: Wizard de navegação no questionário — uma demanda por vez
- ✨ Novo: Botão "Próxima Demanda ▶" com validação por bloco
- ✨ Novo: Botão "◀ Demanda Anterior" com restauração de respostas
- ✨ Novo: Cache `respostas_salvas` — elimina perda de respostas ao navegar entre blocos
- ✨ Novo: Barras de progresso por bloco (topo) e geral X/40 (rodapé)
- ✨ Novo: POP 020 — Tutorial visual tela a tela na Aba Documentação
- ✨ Novo: Visualizador PDF embutido via PyMuPDF (renderização como imagem)
- ✨ Novo: QR Code ampliado para 500 px (+150%)
- ✨ Novo: Fonte do nome da empresa em 72pt com quebra automática de linha
- ✅ Corrigido: Botão ENVIAR desabilitado enquanto há perguntas sem resposta

### v6.1 — 05/05/2026
- ✅ Correção: respostas pré-preenchidas entre respondentes (keys únicas por CPF)
- ✅ Correção: mesmo CPF liberado em empresas diferentes
- ✅ Correção: documentação "Arquivo não encontrado" (caminho via `__file__`)
- ✨ Novo: Módulo "📊 Gestão das Respostas (RH)" com login CNPJ + senha
- ✨ Novo: Aba "🔐 Segurança e Acesso RH" no Admin
- ✨ Novo: Senhas RH geradas automaticamente no cadastro
- ✨ Novo: Zona de Perigo com exclusão individual de empresa
- ✨ Novo: QR Code profissional com WhatsApp/E-mail integrados
- ✨ Novo: SHARE_URL separada de APP_URL para compartilhamento externo
- ✨ Novo: Admin expandido para 6 abas

### v6.0 — 30/04/2026
- Publicação inicial no Streamlit Cloud
- Questionário COPSOQ III com 40 questões / 8 dimensões
- Admin com cadastro manual e via CSV
- Geração de laudo PDF
- Geração de imagem QR Code

---

**Última atualização:** 07/05/2026  
**Versão:** 6.2  
**Responsável:** SSTG Gestão Ocupacional
