# 🔧 Guia Técnico SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)

**Versão:** 7.7  
**Data:** 07/05/2026  
**Público:** Administradores de Sistema | Desenvolvedores

---

## 📋 Índice

1. [Arquitetura do Sistema](#arquitetura)
2. [Estrutura de Arquivos](#estrutura-de-arquivos)
3. [Variáveis de Configuração](#variáveis-de-configuração)
4. [Funções Principais](#funções-principais)
5. [Módulos da Aplicação](#módulos-da-aplicação)
6. [Estrutura de Dados (CSV)](#estrutura-de-dados)
7. [Fluxo de Dados](#fluxo-de-dados)
8. [Segurança](#segurança)
9. [Troubleshooting Técnico](#troubleshooting-técnico)

---

## 🏗️ Arquitetura

### Stack Tecnológico

```
┌──────────────────────────────────────────────────────┐
│                   Frontend (Navegador)               │
│         HTML5 + JavaScript (Streamlit)               │
└────────────────────┬─────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼─────────────────────────────────┐
│          Aplicação (Streamlit - Python)              │
│  • app.py              — Lógica principal (3 módulos)│
│  • gerar_laudo.py      — Geração de PDFs             │
│  • gerar_compartilhamento.py — QR Code + imagens     │
│  • .streamlit/config.toml   — Configuração visual    │
└────────────────────┬─────────────────────────────────┘
                     │ I/O
┌────────────────────▼─────────────────────────────────┐
│            Armazenamento (CSV)                       │
│  • db_acessos_autorizados.csv  (acessos + senhas RH) │
│  • respostas_CNPJ_XXXXX.csv    (respostas por empresa│
└──────────────────────────────────────────────────────┘
```

### Componentes Principais

#### 1. **app.py** (Núcleo)
- Interface Streamlit com **3 módulos** (sidebar radio)
- Gerenciamento de sessão com `st.session_state`
- Validações, fluxos de autenticação, persistência em CSV

#### 2. **gerar_laudo.py** (Geração de Laudo PDF)
- Cálculo de dimensões COPSOQ III
- Classificação de risco
- Geração de PDF com ReportLab

#### 3. **gerar_compartilhamento.py** (QR Code e Imagem)
- `gerar_imagem_compartilhamento_simples()` — gera imagem 1280×(altura dinâmica) px
- QR Code ampliado para **500 px** (+150%), fonte do nome em **72pt** com quebra automática de linha
- Altura da imagem calculada dinamicamente conforme número de linhas do nome da empresa
- Composição com PIL/Pillow: header, conteúdo, QR Code, footer
- Retorna `io.BytesIO` pronto para download ou exibição

#### 4. **config.toml** (Configuração Visual)
- Tema SSTG (cores, fontes)
- Configurações do servidor Streamlit

### Dependências Python

| Biblioteca | Versão mínima | Uso |
|-----------|--------------|-----|
| `streamlit` | ≥1.28.0 | Interface web |
| `pandas` | ≥2.0.0 | Manipulação de dados CSV |
| `reportlab` | ≥4.0.0 | Geração de laudos PDF (capa, cabeçalho, dashboard, assinaturas) |
| `pillow` | ≥10.0.0 | Composição de imagens QR Code e logo no laudo |
| `qrcode[pil]` | ≥7.4.2 | Geração de QR Codes |
| `pymupdf` | ≥1.23.0 | Visualizador PDF (POP 020) — renderiza páginas como PNG |
| `plotly` | ≥5.18.0 | Gráficos interativos nos dashboards |
| `matplotlib` | ≥3.7.0 | Dashboard do laudo PDF (gridspec, barras) |
| `filelock` | ≥3.12.0 | Bloqueio de arquivo — integridade CSV em acesso simultâneo |

---

## 📁 Estrutura de Arquivos

```
sstg-e-social/
├── app.py                          # Aplicação principal
├── gerar_laudo.py                  # Gerador de laudos PDF
├── gerar_compartilhamento.py       # Gerador de imagens QR Code
├── gerar_pdf_publicacao.py         # Converte .md para PDF
├── requirements.txt                # Dependências Python
├── POP020_TUTORIAL_TELAS.pdf       # Tutorial visual tela a tela (v6.2)
├── .streamlit/
│   └── config.toml                 # Tema e configurações
├── data/                           # Dados (Streamlit Cloud)
│   ├── db_acessos_autorizados.csv
│   └── respostas_CNPJ_*.csv
├── README.md
├── TUTORIAL.md
├── GUIA_INSTALACAO.md
├── GUIA_TECNICO.md
├── CHECKLIST_LANCAMENTO.md
└── DOCUMENTACAO_PUBLICACAO.md
```

> **Nota:** No Streamlit Cloud, os dados ficam em `./data/`. Localmente, o `DATA_DIR` aponta para a pasta configurada (ex: Google Drive).

---

## ⚙️ Variáveis de Configuração

Definidas no início de `app.py`:

```python
# Diretório da raiz do projeto (usado para documentação)
DOC_DIR = os.path.dirname(os.path.abspath(__file__))

# Detecção de ambiente
IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true'

if IS_STREAMLIT_CLOUD:
    DATA_DIR = os.path.join(DOC_DIR, "data")   # ./data/ no Cloud
    APP_URL  = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"
else:
    DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"   # Google Drive local
    APP_URL  = "http://192.168.77.2:8501"

# URL pública — sempre Streamlit Cloud, usada em links compartilhados
SHARE_URL = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"

# Senha do admin (alterar antes de produção)
SENHA_ADMIN = "sstg2025"

# Arquivo de acessos
ARQUIVO_ACESSOS = caminho("db_acessos_autorizados.csv")
```

### Diferença entre APP_URL e SHARE_URL

| Variável | Uso | Valor |
|----------|-----|-------|
| `APP_URL` | URL base da instância em execução | Local: IP da rede / Cloud: URL pública |
| `SHARE_URL` | Links compartilhados externamente | **Sempre** a URL do Streamlit Cloud |

`SHARE_URL` garante que links enviados por WhatsApp/e-mail funcionem fora da rede local.

---

## 🔧 Funções Principais

### Funções de Caminho

```python
def caminho(nome_arquivo: str) -> str:
    """Caminho para arquivos de dados (CSVs) — aponta para DATA_DIR."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, nome_arquivo)

def caminho_doc(nome_arquivo: str) -> str:
    """Caminho para documentação (.md, .pdf) — sempre na raiz do repo via __file__."""
    return os.path.join(DOC_DIR, nome_arquivo)
```

> `caminho_doc()` usa `__file__` para localizar os arquivos de documentação de forma absoluta, independente do working directory ou ambiente.

### Funções de Segurança

```python
def gerar_senha_rh() -> str:
    """
    Gera senha segura de 8 caracteres (A-Z + 0-9).
    Usa secrets module — criptograficamente seguro.
    Ex: A7K9M2P5
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

def hash_senha(senha: str) -> str:
    """Hash SHA-256 para armazenamento. Não reversível."""
    return hashlib.sha256(senha.encode()).hexdigest()

def hash_cpf(cpf: str) -> str:
    """Hash SHA-256 do CPF para anonimização nas respostas."""
    return hashlib.sha256(cpf.encode()).hexdigest()
```

### Funções de Validação

```python
def validar_cpf_formato(cpf: str) -> bool:
    """Verifica se CPF tem exatamente 11 dígitos numéricos."""
    return cpf.isdigit() and len(cpf) == 11

def cpf_ja_respondeu(cnpj: str, cpf: str) -> bool:
    """
    Verifica se CPF já respondeu para um CNPJ específico.
    Consulta o arquivo respostas_CNPJ_{cnpj}.csv.
    Cada empresa tem seu próprio arquivo — mesmo CPF pode 
    responder em empresas diferentes.
    """
    arq = caminho(f"respostas_CNPJ_{cnpj}.csv")
    if os.path.exists(arq):
        df = pd.read_csv(arq, sep=';', dtype=str)
        if 'CPF_Hash' in df.columns:
            return hash_cpf(cpf) in df['CPF_Hash'].values
    return False

def periodo_valido(dados: dict) -> tuple:
    """Retorna (True, '') se dentro do período, ou (False, mensagem)."""
    ...
```

### Funções de Cadastro

```python
def salvar_cadastro_completo(dados_emp: dict, colaboradores: list):
    """
    Salva colaboradores no db_acessos_autorizados.csv.
    Duplicidade verificada por CPF + CNPJ (não CPF global):
    mesmo CPF pode existir em empresas diferentes.
    """
    ...
    # Verificação correta:
    ja_nessa_empresa = (
        not df_existente.empty
        and len(df_existente[
            (df_existente['CPF'] == cpf_limpo) & 
            (df_existente['CNPJ'] == cnpj_atual)
        ]) > 0
    )
```

---

## 🗂️ Módulos da Aplicação

### Módulo 1: 📋 Questionário Psicossocial

**Fluxo:**
```
Login (CPF) → Validação → Wizard (8 blocos, um por vez) → Envio → Confirmação
```

**Sessão:**
- `st.session_state.passo`: `"login"` → `"quest"` → `"fim"`
- `st.session_state.dados_sessao`: dados do respondente
- `st.session_state.dominio_atual`: índice 0–7 do bloco exibido no momento
- `st.session_state.respostas_salvas`: cache persistente de respostas entre reruns

#### Padrão Wizard de Navegação (v6.2)

O questionário exibe **um bloco (demanda) por vez**, controlado por `dominio_atual`. O padrão substitui o `st.tabs` anterior, que não tinha API de controle programático.

**Problema resolvido:** O Streamlit apaga do `session_state` os valores de widgets que não estão renderizados na tela. Ao navegar entre blocos, as respostas do bloco anterior eram perdidas.

**Solução — dupla camada de persistência:**

```python
# Inicialização
if 'dominio_atual' not in st.session_state:
    st.session_state.dominio_atual = 0
if 'respostas_salvas' not in st.session_state:
    st.session_state.respostas_salvas = {}

# Salvar respostas do bloco atual antes de avançar/voltar
def salvar_bloco_atual():
    for k in qus_atual.keys():
        chave = f"{cpf_resp}_{k}"
        if chave in st.session_state:
            st.session_state.respostas_salvas[chave] = st.session_state[chave]

# Ler resposta: widget state → cache → None
def get_resp(chave):
    val = st.session_state.get(chave)
    if val is not None:
        return val
    return st.session_state.respostas_salvas.get(chave)

# Radio com restauração do valor salvo
val_salvo = st.session_state.respostas_salvas.get(chave)
idx_inicial = OPCOES.index(val_salvo) if val_salvo in OPCOES else None
st.radio(f"**{txt}**", OPCOES, horizontal=True, key=chave, index=idx_inicial)

# Botão avançar — salva antes de rerun
if st.button("Próxima Demanda ▶", ...):
    salvar_bloco_atual()
    st.session_state.dominio_atual += 1
    st.rerun()

# Botão voltar
if st.button("◀ Demanda Anterior", ...):
    salvar_bloco_atual()
    st.session_state.dominio_atual -= 1
    st.rerun()
```

**Barras de progresso:**
- **Topo:** `st.progress()` + caption "Bloco X de 8 — Nome da Demanda"
- **Rodapé:** Contagem de perguntas respondidas via `get_resp()` → "X de 40 perguntas respondidas"

**Validação de bloco:** O botão "Próxima Demanda" fica desabilitado se há perguntas sem resposta no bloco atual. O botão ENVIAR fica desabilitado enquanto `total_respondidas < 40`.

**Keys de radio únicos por respondente:**
```python
# Chave inclui CPF para evitar contaminação entre respondentes
chave_unica = f"{cpf_respondente}_{key}"  # ex: "12345678901_q1"
```

**Dimensões (40 questões, 8 blocos):**

| Dimensão | Questões | Escala Invertida |
|----------|----------|-----------------|
| 📦 Cargo | 5 | Não |
| 🎮 Controle | 6 | Não |
| ⚖️ Demandas | 8 | ✅ Sim |
| ⚠️ Relacionamentos | 4 | ✅ Sim |
| 🤝 Apoio Colegas | 4 | Não |
| 👔 Apoio Chefia | 5 | Não |
| 📢 Comunicação | 3 | Não |
| 🔄 Mudanças | 5 | Não |

### Módulo 2: 📊 Gestão das Respostas (RH)

**Autenticação:**
```python
# Verificação: hash(senha_digitada) == hash armazenado no CSV
if hash_senha(senha_rh) == row['Senha_RH_Hash']:
    st.session_state.rh_logado = True
    st.session_state.rh_cnpj = cnpj
```

**Funcionalidades após login:**
- Link público do questionário
- Geração de QR Code com WhatsApp/E-mail
- Dashboard de respostas (métricas e gráfico)

**Isolamento:** Cada RH acessa apenas dados da própria empresa (filtro por CNPJ logado).

### Módulo 3: 🔐 Admin SSTG (Gestão) — 6 Abas

| Aba | Código | Principais ações |
|-----|--------|-----------------|
| t1 | Cadastro / Inclusão | Manual + CSV, gera senha RH automaticamente |
| t2 | Conferência | Visualização, período, Zona de Perigo |
| t3 | Resultados | Médias, laudo PDF, QR Code |
| t4 | Movimentação | Admissão, desligamento, reativação |
| t5 | Segurança RH | Gerar/redefinir senha RH por empresa |
| t6 | Documentação | Leitura de `.md` via `caminho_doc()` + visualizador PDF (POP 020) via PyMuPDF |

---

## 🗄️ Estrutura de Dados (CSV)

### db_acessos_autorizados.csv

```
CPF;Empresa;CNPJ;Função;Departamento;Data_Acesso_Liberado;
Data_Inicio_Periodo;Data_Fim_Periodo;Status;
Data_Movimentacao;Motivo_Movimentacao;Senha_RH_Hash
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `CPF` | str | CPF em texto puro (11 dígitos) |
| `Empresa` | str | Razão social |
| `CNPJ` | str | CNPJ sem formatação |
| `Função` | str | Cargo do colaborador |
| `Departamento` | str | Setor |
| `Status` | str | `Ativo` ou `Inativo` |
| `Senha_RH_Hash` | str | SHA-256 da senha RH (por CNPJ) |

> **Segurança:** `Senha_RH_Hash` contém apenas o hash — a senha nunca é armazenada em texto puro.

### respostas_CNPJ_{cnpj}.csv

```
CPF_Hash;Empresa;Função;Departamento;Timestamp;
q1;q2;...;q40;Media_Cargo;Media_Controle;...;Media_Geral
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `CPF_Hash` | str | SHA-256 do CPF (anonimização) |
| `q1`..`q40` | int | Valor bruto da resposta (0-4) |
| `Media_*` | float | Média por dimensão |
| `Media_Geral` | float | Média geral |

> **Um arquivo por empresa** — isolamento total de dados.

---

## 🔄 Fluxo de Dados

### Cadastro e Acesso RH

```
Admin cadastra empresa + colaboradores
        ↓
Sistema gera senha RH (secrets module)
        ↓
Hash da senha salvo em Senha_RH_Hash
        ↓
Senha exibida uma única vez ao Admin
        ↓
Admin repassa senha ao RH da empresa
        ↓
RH loga com CNPJ + Senha
        ↓
hash(senha digitada) == Senha_RH_Hash? → Acesso liberado
```

### Respondente

```
Colaborador acessa link/?cnpj=XXXX
        ↓
Digite CPF → Validações (CPF autorizado? Período ativo? Já respondeu?)
        ↓
Wizard: exibe Bloco 1 de 8
  → Responde questões do bloco
  → "Próxima Demanda ▶" (só habilita se bloco completo)
  → salvar_bloco_atual() → respostas_salvas → rerun
  → Bloco 2... até Bloco 8
        ↓
Botão ENVIAR habilitado apenas com 40/40 respondidas
Envio: hash(CPF) + respostas + médias → respostas_CNPJ_XXXX.csv
```

### Exclusão de Empresa

```
Admin → Zona de Perigo → Excluir Empresa
        ↓
Seleciona empresa, vê contadores de impacto
        ↓
Digita senha admin → Confirmação
        ↓
Remove linhas do CNPJ em db_acessos_autorizados.csv
Remove arquivo respostas_CNPJ_{cnpj}.csv
```

---

## 🔒 Segurança

### Camadas de Proteção

| Camada | Mecanismo |
|--------|-----------|
| **CPF anonimizado** | SHA-256 nas respostas (não reversível) |
| **Senha Admin** | Comparação direta (configurável) |
| **Senha RH** | SHA-256 no CSV — nunca texto puro |
| **Geração de senha** | `secrets.choice()` — criptograficamente seguro |
| **Isolamento de dados** | Um CSV por empresa — RH não cruza dados |
| **Período de acesso** | Data início/fim — fora do período, bloqueado |
| **Status do CPF** | Ativo/Inativo — inativados perdem acesso |
| **Exclusão controlada** | Requer senha admin + confirmação explícita |

### Session State por Respondente

As chaves do Streamlit `session_state` para as respostas do questionário são prefixadas com o CPF do respondente:

```python
key = f"{cpf_respondente}_{pergunta_id}"  # ex: "12345678901_q1"
```

Isso evita que respostas de um respondente apareçam pré-selecionadas para o próximo, mesmo no mesmo navegador/dispositivo.

### Suporte a Múltiplos Usuários (v7.7)

O sistema suporta múltiplos usuários simultâneos. Cada conexão WebSocket tem seu próprio `st.session_state` completamente isolado.

**Mecanismo de proteção de arquivo — `_csv_lock()` (v7.7):**

```python
try:
    from filelock import FileLock as _FileLock
    def _csv_lock(arquivo: str):
        return _FileLock(arquivo + ".lock", timeout=10)
except ImportError:
    def _csv_lock(arquivo: str):
        return contextlib.nullcontext()
```

Todas as operações de escrita em CSV são protegidas com `with _csv_lock(arquivo):`, garantindo que dois usuários simultâneos não corrompam os dados.

**Operações protegidas:**

| Função | Arquivo | Escopo do lock |
|--------|---------|----------------|
| `criar_usuario_operacional()` | usuarios.csv | read + write |
| `desativar_usuario_operacional()` | usuarios.csv | read + write |
| `reativar_usuario_operacional()` | usuarios.csv | read + write |
| `redefinir_senha_operacional()` | usuarios.csv | read + write |
| `set_senha_admin()` | config.csv | read + write |
| `atualizar_status_cpf()` | acessos.csv | read + write |
| `atualizar_periodo_empresa()` | acessos.csv | read + write |
| `salvar_cadastro_completo()` | acessos.csv | write (append) |
| Senha RH no cadastro (manual/CSV) | acessos.csv | read + write |
| Excluir empresa | acessos.csv | write |
| Gerar nova senha RH | acessos.csv | write |
| Salvar resposta do questionário | respostas_CNPJ_*.csv | write (append) |

**Fallback automático:** Se `filelock` não estiver instalado, `_csv_lock()` retorna `contextlib.nullcontext()` — o app funciona normalmente sem trava (sem erro).

---

## 📄 Laudo PDF — Arquitetura v7.7

O laudo é gerado por `gerar_laudo.py` usando **ReportLab** (Platypus + canvas).

### Estrutura do PDF

| Página | Seção | Conteúdo |
|--------|-------|---------|
| 1 | Capa | Logo SSTG no hero banner, DADOS DA EMPRESA, RESPONSÁVEIS TÉCNICOS (único Table, borda a borda) |
| 2 | Seção 1 | Identificação, objetivo, base legal |
| 3 | Seção 2 | Metodologia COPSOQ III |
| 4–5 | Seção 3 | Análise — inclui dashboard Matplotlib (métricas + adesão + médias por dimensão) |
| 6 | Seção 4 | Classificação de riscos |
| 7 | Seção 5 | Recomendações |
| 8 | Seção 6 | Conclusão |
| 9 | Última | Assinaturas (3 colunas) + nota legal no rodapé |

### Cabeçalho (páginas 2–9)

Desenhado via callback `onLaterPages` no nível do canvas (não do Platypus), garantindo que apareça em todas as páginas internas:

```python
def _header_footer(canvas_obj, doc, empresa="", logo_path=None):
    canvas_obj.saveState()
    w, h = A4
    # Faixa navy
    canvas_obj.setFillColor(C_AZUL)
    canvas_obj.rect(0, h - 1.4*cm, w, 1.4*cm, fill=1, stroke=0)
    # Logo SSTG (se disponível)
    if logo_path and os.path.exists(logo_path):
        logo_h = 1.1*cm
        logo_w = logo_h * 2.3
        logo_y = h - 1.4*cm + (1.4*cm - logo_h) / 2
        canvas_obj.drawImage(logo_path, 0.3*cm, logo_y,
                             width=logo_w, height=logo_h,
                             preserveAspectRatio=True, mask='auto')
    # Texto + número de página
    canvas_obj.drawString(...)
    canvas_obj.drawRightString(...)
    canvas_obj.restoreState()
```

### Dashboard (Seção 3.5)

Gerado com **Matplotlib + GridSpec** em 3 linhas:

```
Row 0 (0.18): 3 caixas métricas — CPFs autorizados / Respostas / Taxa de Adesão
Row 1 (1.0):  Barras verticais de Adesão (navy/verde) | Painel Taxa de Adesão
Row 2 (1.6):  Barras coloridas de Médias por Dimensão (CORES_DIMS palette)
```

### Tabela RESPONSÁVEIS TÉCNICOS (Capa)

Implementada como um único `Table` ReportLab com SPAN no cabeçalho:

```python
t_resp = Table(
    [
        [Paragraph("RESPONSÁVEIS TÉCNICOS", ...), "", ""],  # SPAN linha 0
        [rt1_subtable, "", rt2_subtable],                   # sub-tabelas lado a lado
    ],
    colWidths=[9*cm, 0.5*cm, 9*cm]   # = 18.5 cm total (igual a t_emp)
)
```

O SPAN garante que o cabeçalho sempre ocupa exatamente a mesma largura que as sub-tabelas, sem desalinhamento.

---

## 🛠️ Troubleshooting Técnico

### "Arquivo não encontrado" na Documentação

**Causa:** Versões anteriores usavam `caminho()` que aponta para `./data/`, mas os `.md` estão na raiz do repo.

**Solução atual (v6.1+):** `caminho_doc()` usa `os.path.dirname(os.path.abspath(__file__))` para localizar sempre a pasta do `app.py`.

### Respostas pré-preenchidas para outro respondente

**Causa:** Keys de `st.radio` sem prefixo por respondente.

**Solução (v6.1+):** Keys incluem o CPF: `f"{cpf_respondente}_{key}"`.

### Respostas perdidas ao navegar entre blocos do questionário

**Causa:** O Streamlit apaga do `session_state` os valores de widgets não renderizados. Ao trocar de bloco, os radios do bloco anterior saem da tela e seus valores são removidos.

**Solução (v6.2):** Cache `respostas_salvas` + função `salvar_bloco_atual()` chamada **antes de todo `st.rerun()`**:
```python
def salvar_bloco_atual():
    for k in qus_atual.keys():
        chave = f"{cpf_resp}_{k}"
        if chave in st.session_state:
            st.session_state.respostas_salvas[chave] = st.session_state[chave]
```

### Visualizador PDF (POP 020) mostra quadro em branco

**Causa:** Browsers modernos bloqueiam `data:application/pdf;base64,...` em `<iframe>` por CSP (Content Security Policy). O Streamlit usa essa abordagem por padrão.

**Solução (v6.2):** Renderização via **PyMuPDF** (`fitz`) — cada página do PDF é convertida para imagem PNG e exibida com `st.image()`:
```python
import fitz  # pymupdf
doc_pdf = fitz.open(pdf_path)
for num, pagina in enumerate(doc_pdf, start=1):
    mat = fitz.Matrix(1.8, 1.8)   # escala 180% para melhor legibilidade
    pix = pagina.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    st.image(img_bytes, caption=f"Página {num} de {len(doc_pdf)}", use_container_width=True)
doc_pdf.close()
```

**Dependência necessária:** `pymupdf>=1.23.0` em `requirements.txt`.

### Links de compartilhamento não funcionam externamente

**Causa:** `APP_URL` aponta para IP local.

**Solução:** Use `SHARE_URL` para todos os links compartilhados. `SHARE_URL` sempre aponta para o Streamlit Cloud.

### Mesmo CPF bloqueado em empresa diferente

**Causa:** Versões anteriores verificavam CPF globalmente.

**Solução (v6.1+):** Verificação por CPF + CNPJ:
```python
ja_nessa_empresa = len(df[
    (df['CPF'] == cpf) & (df['CNPJ'] == cnpj)
]) > 0
```

### Erro ao gerar QR Code

**Causa:** Dependências `qrcode` ou `pillow` não instaladas.

**Solução:**
```bash
pip install "qrcode[pil]" pillow
```

### Nome da empresa cortado na imagem de compartilhamento

**Causa:** Nomes longos ultrapassam a largura da imagem em fonte 72pt.

**Solução (v6.2):** Função `quebrar_linhas()` em `gerar_compartilhamento.py` divide o nome em múltiplas linhas que cabem dentro de `largura - 2*margem`. A altura da imagem é calculada dinamicamente:
```python
altura_linha_empresa = 88   # pixels por linha de texto
altura_bloco_empresa = len(linhas_empresa) * altura_linha_empresa
# altura total recalculada conforme número de linhas
```

---

### Corrupção de CSV com múltiplos usuários simultâneos

**Causa (v6.x):** Duas sessões fazem `read_csv` → modificam → `to_csv` ao mesmo tempo, causando uma sobrescrever a outra.

**Solução (v7.7):** `_csv_lock()` com `filelock`. Instalar: `pip install filelock`.

**Diagnóstico:** Se aparecer CSV com menos linhas do que esperado após uso simultâneo, verifique se `filelock` está instalado: `py -m pip show filelock`.

---

**Última atualização:** 07/05/2026 — v7.7  
**Versão do sistema:** 6.2
