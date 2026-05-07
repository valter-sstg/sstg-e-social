# 🚀 Guia de Instalação e Setup — SSTG - DRPS

**Versão:** 6.2  
**Data:** 07/05/2026  
**Público:** Administradores de Sistema | Instaladores Técnicos

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Inicial](#instalação-inicial)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Publicação no Streamlit Cloud](#publicação-no-streamlit-cloud)
5. [Integração com Google Drive](#integração-com-google-drive)
6. [Backup e Recuperação](#backup-e-recuperação)
7. [Manutenção Periódica](#manutenção-periódica)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Pré-requisitos

### Hardware Mínimo

- **Processador:** Intel i3 ou equivalente
- **RAM:** 4 GB
- **Disco:** 500 MB livres
- **Conexão:** Internet (para Streamlit Cloud e dependências)

### Software Necessário

- **Python:** 3.9 ou superior (recomendado 3.11+)
- **Git:** Recomendado para versionamento e deploy
- **Navegador:** Chrome, Firefox, Edge, Safari (HTML5)

### Verificar Python

```bash
py --version
# ou
python --version
```

Se não tiver Python, instale de: https://www.python.org/downloads/

---

## 📥 Instalação Inicial

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/valter-contador/sstg-e-social.git
cd sstg-e-social
```

**Ou instalar manualmente — copie os arquivos para uma pasta local:**

```
app.py
gerar_laudo.py
gerar_compartilhamento.py
gerar_pdf_publicacao.py
requirements.txt
.streamlit/config.toml
README.md
TUTORIAL.md
GUIA_INSTALACAO.md
GUIA_TECNICO.md
CHECKLIST_LANCAMENTO.md
DOCUMENTACAO_PUBLICACAO.md
```

### Passo 2: Criar Pasta de Configuração

```bash
mkdir .streamlit
```

### Passo 3: Criar Arquivo de Configuração

Crie `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#5A9F62"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#282C5B"
font = "sans serif"

[server]
maxUploadSize = 10
```

### Passo 4: Instalar Dependências

```bash
pip install -r requirements.txt
```

**Conteúdo do `requirements.txt`:**

```
streamlit>=1.28.0
pandas>=2.0.0
reportlab>=4.0.0
pillow>=10.0.0
qrcode[pil]>=7.4.2
pymupdf>=1.23.0
```

> ⚠️ **Importante:** `pillow` e `qrcode[pil]` são necessários para a geração de imagens QR Code. `pymupdf` é necessário para o visualizador de PDF embutido na Aba Documentação (POP 020). Sem ele, o botão de Ler o POP 020 não exibirá o conteúdo.

### Passo 5: Iniciar o App

```bash
streamlit run app.py
```

Acesse em: `http://localhost:8501`

---

## ⚙️ Configuração do Ambiente

### Variáveis Principais em app.py

Abra `app.py` e ajuste conforme seu ambiente:

```python
# Senha do administrador — altere antes de produção!
SENHA_ADMIN = "sstg2025"

# URL pública para links de compartilhamento (Streamlit Cloud)
SHARE_URL = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"
```

### Detecção Automática de Ambiente

O sistema detecta automaticamente se está rodando localmente ou no Streamlit Cloud:

```python
IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true'

if IS_STREAMLIT_CLOUD:
    DATA_DIR = os.path.join(DOC_DIR, "data")   # ./data/ no Cloud
    APP_URL  = "https://..."
else:
    DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"   # Pasta local
    APP_URL  = "http://192.168.77.2:8501"
```

Ajuste `DATA_DIR` local e `APP_URL` conforme sua configuração.

### Localização dos Arquivos de Dados

| Ambiente | DATA_DIR (dados) | DOC_DIR (documentação) |
|----------|-----------------|------------------------|
| Streamlit Cloud | `./data/` | Raiz do repo (via `__file__`) |
| Local | Pasta configurada | Mesma pasta do `app.py` |

---

## ☁️ Publicação no Streamlit Cloud

### Pré-requisitos

- Conta no [GitHub](https://github.com)
- Conta no [Streamlit Cloud](https://share.streamlit.io) (gratuita)

### Passo 1: Preparar Repositório GitHub

```bash
git init
git add .
git commit -m "Deploy inicial SSTG v6.1"
git branch -M main
git remote add origin https://github.com/seu-usuario/sstg-e-social.git
git push -u origin main
```

### Passo 2: Criar App no Streamlit Cloud

1. Acesse https://share.streamlit.io
2. Clique em **"New app"**
3. Selecione o repositório GitHub
4. Defina **"Main file path"**: `app.py`
5. Clique em **"Deploy"**

### Passo 3: Aguardar Deploy

O deploy leva ~3-5 minutos. A URL será:
```
https://seu-app-name.streamlit.app
```

### Passo 4: Atualizar SHARE_URL

Após obter a URL pública, atualize em `app.py`:

```python
SHARE_URL = "https://seu-app-name.streamlit.app"
```

Commit e push para aplicar:

```bash
git add app.py
git commit -m "Atualiza SHARE_URL com URL de produção"
git push
```

### Passo 5: Manutenção da Pasta de Dados

No Streamlit Cloud, a pasta `./data/` é criada automaticamente pelo app. Os dados **persistem entre sessões** enquanto o app estiver ativo, mas podem ser resetados em redeploys.

> **Recomendação:** Para produção, faça backups periódicos via **Admin → Conferência → ⬇️ Baixar lista filtrada**.

---

## 💾 Integração com Google Drive

Para usar o Google Drive como armazenamento local:

### Passo 1: Instalar Google Drive Desktop

Baixe e instale o Google Drive Desktop.  
Após login, o Drive aparece como unidade `G:\Meu Drive\`

### Passo 2: Ajustar DATA_DIR em app.py

```python
else:
    DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"
    APP_URL  = "http://192.168.77.2:8501"
```

### Passo 3: Criar a Pasta

```bash
mkdir "G:\Meu Drive\SSTG-E-Social"
```

### Benefícios

- ✅ Backup automático na nuvem
- ✅ Acessível de qualquer computador com login Google
- ✅ Histórico de versões dos arquivos CSV

---

## 🔄 Backup e Recuperação

### Backup Manual

Os dados ficam em arquivos CSV. Para backup:

1. Acesse **Admin → Aba Conferência**
2. Clique em **⬇️ Baixar lista filtrada (.csv)**
3. Na **Aba Resultados**, baixe o CSV de respostas de cada empresa

### Backup via Git

Se o repositório estiver no GitHub:

```bash
# Adiciona os dados ao git (se não estiverem no .gitignore)
git add data/
git commit -m "Backup dados $(date +%Y%m%d)"
git push
```

> ⚠️ **Atenção:** Dados de colaboradores são sensíveis (LGPD). Não versione CPFs se o repositório for público.

### Recuperação

Para restaurar dados:

1. Copie os arquivos `.csv` de backup para a pasta `DATA_DIR`
2. Reinicie o app
3. Os dados serão carregados automaticamente

---

## 🛠️ Manutenção Periódica

### Mensal

- [ ] Verificar espaço em disco (dados CSV)
- [ ] Exportar backup dos CSVs
- [ ] Revisar colaboradores inativos
- [ ] Verificar se há empresas com período expirado

### Semestral

- [ ] Atualizar dependências Python: `pip install --upgrade -r requirements.txt`
- [ ] Revisar senha do Admin SSTG
- [ ] Revisar senhas RH das empresas ativas
- [ ] Verificar URL do Streamlit Cloud (pode mudar após inatividade)

### Anual

- [ ] Revisar conformidade LGPD
- [ ] Arquivar dados antigos (>12 meses)
- [ ] Atualizar documentação

---

## 🔍 Troubleshooting

### App não inicia

```bash
# Verificar Python
py --version

# Verificar dependências
pip list | findstr streamlit

# Reinstalar dependências
pip install -r requirements.txt

# Iniciar com log detalhado
streamlit run app.py --logger.level=debug
```

### Erro "ModuleNotFoundError: qrcode"

```bash
pip install "qrcode[pil]"
```

### Erro "ModuleNotFoundError: PIL"

```bash
pip install pillow
```

### Porta 8501 ocupada

```bash
streamlit run app.py --server.port 8502
```

### Dados não aparecem no app

Verifique se `DATA_DIR` aponta para a pasta correta:

```python
# No app.py, adicione temporariamente para debug:
st.write(f"DATA_DIR: {DATA_DIR}")
st.write(f"ARQUIVO_ACESSOS: {ARQUIVO_ACESSOS}")
```

### Documentação mostra "Arquivo não encontrado"

Verifique se os `.md` estão na raiz do projeto (mesma pasta do `app.py`). A partir da v6.1, o caminho é resolvido via `__file__` automaticamente.

### Links compartilhados não funcionam

Verifique se `SHARE_URL` em `app.py` aponta para a URL pública correta do Streamlit Cloud (não para localhost).

### App lento no Streamlit Cloud

- O app "hiberna" após inatividade — o primeiro acesso pode levar 30-60s
- Após o primeiro carregamento, a velocidade normaliza

---

**Última atualização:** 07/05/2026  
**Versão do sistema:** 6.2
