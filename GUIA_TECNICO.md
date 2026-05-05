# 🔧 Guia Técnico SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)

**Versão:** 6.1  
**Data:** 05/05/2026  
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
- `gerar_imagem_compartilhamento_simples()` — gera imagem 1280×720 px
- Composição com PIL/Pillow: header, conteúdo, QR Code, footer
- Retorna `io.BytesIO` pronto para download ou exibição

#### 4. **config.toml** (Configuração Visual)
- Tema SSTG (cores, fontes)
- Configurações do servidor Streamlit

---

## 📁 Estrutura de Arquivos

```
sstg-e-social/
├── app.py                          # Aplicação principal
├── gerar_laudo.py                  # Gerador de laudos PDF
├── gerar_compartilhamento.py       # Gerador de imagens QR Code
├── gerar_pdf_publicacao.py         # Converte .md para PDF
├── requirements.txt                # Dependências Python
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
Login (CPF) → Validação → Questionário (8 abas) → Envio → Confirmação
```

**Sessão:**
- `st.session_state.passo`: `"login"` → `"quest"` → `"fim"`
- `st.session_state.dados_sessao`: dados do respondente

**Keys de radio únicos por respondente:**
```python
# Chave inclui CPF para evitar contaminação entre respondentes
chave_unica = f"{cpf_respondente}_{key}"
respostas[key] = st.radio(..., key=chave_unica, index=None)
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
| t6 | Documentação | Leitura de `.md` via `caminho_doc()` |

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
Preenche 40 questões em 8 blocos
Navegação: botão "Próxima Demanda" ao final de cada bloco
        ↓
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

---

## 🛠️ Troubleshooting Técnico

### "Arquivo não encontrado" na Documentação

**Causa:** Versões anteriores usavam `caminho()` que aponta para `./data/`, mas os `.md` estão na raiz do repo.

**Solução atual (v6.1):** `caminho_doc()` usa `os.path.dirname(os.path.abspath(__file__))` para localizar sempre a pasta do `app.py`.

### Respostas pré-preenchidas para outro respondente

**Causa:** Keys de `st.radio` sem prefixo por respondente.

**Solução (v6.1):** Keys incluem o CPF: `f"{cpf_respondente}_{key}"`.

### Links de compartilhamento não funcionam externamente

**Causa:** `APP_URL` aponta para IP local.

**Solução:** Use `SHARE_URL` para todos os links compartilhados. `SHARE_URL` sempre aponta para o Streamlit Cloud.

### Mesmo CPF bloqueado em empresa diferente

**Causa:** Versões anteriores verificavam CPF globalmente.

**Solução (v6.1):** Verificação por CPF + CNPJ:
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

---

**Última atualização:** 05/05/2026  
**Versão do sistema:** 6.1
