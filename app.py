import streamlit as st
import pandas as pd
import os
import glob
import hashlib
import re
import secrets
import string
import base64
from datetime import datetime, date

try:
    from gerar_laudo import gerar_laudo_pdf
    LAUDO_DISPONIVEL = True
except ImportError:
    LAUDO_DISPONIVEL = False

# ── Geração de imagem QR Code embutida (sem módulo externo) ──────────────────
import io as _io
import qrcode as _qrcode
from PIL import Image as _Image, ImageDraw as _ImageDraw, ImageFont as _ImageFont

def _achar_fonte():
    """Retorna o primeiro arquivo TTF encontrado no sistema."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidatos = [
        os.path.join(windir, "Fonts", "arial.ttf"),
        os.path.join(windir, "Fonts", "Arial.ttf"),
        os.path.join(windir, "Fonts", "calibri.ttf"),
        os.path.join(windir, "Fonts", "tahoma.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidatos:
        if p and os.path.isfile(p):
            return p
    return None

_FONTE_PATH = _achar_fonte()

def _f(tamanho):
    """Carrega fonte TTF no tamanho pedido."""
    if _FONTE_PATH:
        try:
            return _ImageFont.truetype(_FONTE_PATH, tamanho)
        except Exception:
            pass
    try:
        return _ImageFont.load_default(size=tamanho)
    except TypeError:
        return _ImageFont.load_default()

def gerar_imagem_compartilhamento_simples(empresa_nome: str, cnpj: str, app_url: str):
    """Gera PNG de compartilhamento com QR Code grande e nome da empresa em destaque."""
    LARGURA    = 1280
    MARGEM     = 50
    QR_TAM     = 600
    H_HEADER   = 120
    H_LINHA    = 100
    H_RODAPE   = 60

    COR_NAVY   = (40, 44, 91)
    COR_VERDE  = (90, 159, 98)
    BRANCO     = (255, 255, 255)
    CZ_CLARO   = (190, 190, 190)
    CZ_MED     = (130, 130, 130)

    f_hdr_sm = _f(20)
    f_hdr_lg = _f(46)
    f_label  = _f(28)
    f_emp    = _f(80)
    f_rod    = _f(20)

    def quebrar(draw_r, texto, fonte_r, max_w):
        palavras = texto.split()
        linhas, atual = [], ""
        for p in palavras:
            c = (atual + " " + p).strip()
            w = draw_r.textbbox((0, 0), c, font=fonte_r)[2]
            if w <= max_w:
                atual = c
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        return linhas or [texto]

    tmp = _Image.new("RGB", (LARGURA, 10))
    drw = _ImageDraw.Draw(tmp)
    linhas = quebrar(drw, empresa_nome, f_emp, LARGURA - 2 * MARGEM)

    y_label   = H_HEADER + 30
    y_emp     = y_label + 44
    y_qr      = y_emp + len(linhas) * H_LINHA + 40
    ALTURA    = y_qr + QR_TAM + 30 + H_RODAPE

    img  = _Image.new("RGB", (LARGURA, ALTURA), BRANCO)
    draw = _ImageDraw.Draw(img)

    # Header
    draw.rectangle([(0, 0), (LARGURA, H_HEADER)], fill=COR_NAVY)
    draw.text((MARGEM, 16),  "SSTG - DRPS  Diagnóstico de Riscos Psicossociais (NR-1)", fill=CZ_CLARO, font=f_hdr_sm)
    draw.text((MARGEM, 50),  "SSTG - DRPS  Diagnóstico de Riscos Psicossociais",        fill=BRANCO,   font=f_hdr_lg)

    # Empresa
    draw.text((MARGEM, y_label), "Empresa:", fill=CZ_MED, font=f_label)
    y_cur = y_emp
    for linha in linhas:
        draw.text((MARGEM, y_cur), linha, fill=COR_VERDE, font=f_emp)
        y_cur += H_LINHA

    # QR Code
    link   = f"{app_url}/?cnpj={cnpj}"
    qr_obj = _qrcode.QRCode(version=1, error_correction=_qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr_obj.add_data(link)
    qr_obj.make(fit=True)
    qr_pil = qr_obj.make_image(fill_color=COR_NAVY, back_color=BRANCO)
    qr_pil = qr_pil.resize((QR_TAM, QR_TAM), _Image.Resampling.LANCZOS)
    img.paste(qr_pil, ((LARGURA - QR_TAM) // 2, y_qr))

    # Rodapé
    draw.rectangle([(0, ALTURA - H_RODAPE), (LARGURA, ALTURA)], fill=(235, 235, 235))
    txt_r = f"Imagem de compartilhamento: {empresa_nome}"
    bx    = draw.textbbox((0, 0), txt_r, font=f_rod)
    draw.text(((LARGURA - (bx[2] - bx[0])) // 2, ALTURA - H_RODAPE + 18), txt_r, fill=CZ_MED, font=f_rod)

    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

COMPARTILHAMENTO_DISPONIVEL = True

# ─── DIRETÓRIO DE DADOS ───────────────────────────────────────────────────────
# DOC_DIR: sempre a pasta onde app.py está (raiz do repo), em qualquer ambiente
DOC_DIR = os.path.dirname(os.path.abspath(__file__))

IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true'

if IS_STREAMLIT_CLOUD:
    DATA_DIR = os.path.join(DOC_DIR, "data")
    APP_URL  = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"
else:
    DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"
    APP_URL  = "http://192.168.77.2:8501"

# URL pública para compartilhamento (sempre usa Streamlit Cloud)
SHARE_URL = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"

def caminho(nome_arquivo: str) -> str:
    """Caminho para arquivos de dados (CSVs, uploads)."""
    if DATA_DIR:
        os.makedirs(DATA_DIR, exist_ok=True)
        return os.path.join(DATA_DIR, nome_arquivo)
    return nome_arquivo

def caminho_doc(nome_arquivo: str) -> str:
    """Caminho para arquivos de documentação (.md, .pdf) — sempre na raiz do repo."""
    return os.path.join(DOC_DIR, nome_arquivo)

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
ARQUIVO_ACESSOS = caminho("db_acessos_autorizados.csv")
SENHA_ADMIN     = "sstg2025"

# ─── FUNÇÕES AUXILIARES ───────────────────────────────────────────────────────

def validar_cpf_formato(cpf: str) -> bool:
    return cpf.isdigit() and len(cpf) == 11

def carregar_dados(arquivo: str) -> pd.DataFrame:
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo, sep=';', dtype=str)
    return pd.DataFrame()

def hash_cpf(cpf: str) -> str:
    return hashlib.sha256(cpf.encode()).hexdigest()

def gerar_senha_rh() -> str:
    """Gera uma senha segura de 8 caracteres para acesso RH"""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

def hash_senha(senha: str) -> str:
    """Faz hash da senha para armazenamento seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

def cpf_ja_respondeu(cnpj: str, cpf: str) -> bool:
    arq = caminho(f"respostas_CNPJ_{cnpj}.csv")
    if os.path.exists(arq):
        df = pd.read_csv(arq, sep=';', dtype=str)
        if 'CPF_Hash' in df.columns:
            return hash_cpf(cpf) in df['CPF_Hash'].values
    return False

def normalizar_status(df: pd.DataFrame) -> pd.DataFrame:
    if 'Status' not in df.columns:
        df['Status'] = 'Ativo'
    else:
        df['Status'] = df['Status'].fillna('Ativo')
    return df

def salvar_cadastro_completo(dados_emp: dict, colaboradores: list):
    """
    dados_emp : {CNPJ, Razão Social, Data_Inicio, Data_Fim}
    colaboradores : list de dicts {CPF, Função, Departamento}
    """
    df_existente = carregar_dados(ARQUIVO_ACESSOS)
    novos, duplicados, invalidos = [], [], []

    for colab in colaboradores:
        cpf_limpo = str(colab.get('CPF', '')).strip().replace(".", "").replace("-", "")
        if not cpf_limpo:
            continue
        if not validar_cpf_formato(cpf_limpo):
            invalidos.append(cpf_limpo)
            continue
        # Duplicidade verifica CPF + CNPJ: mesmo CPF pode responder em empresas diferentes
        cnpj_atual = dados_emp['CNPJ']
        ja_nessa_empresa = (
            not df_existente.empty
            and len(df_existente[(df_existente['CPF'] == cpf_limpo) & (df_existente['CNPJ'] == cnpj_atual)]) > 0
        )
        if ja_nessa_empresa:
            duplicados.append(cpf_limpo)
            continue
        novos.append({
            "CPF":                 cpf_limpo,
            "Empresa":             dados_emp['Razão Social'],
            "CNPJ":                dados_emp['CNPJ'],
            "Função":              colab.get('Função', ''),
            "Departamento":        colab.get('Departamento', ''),
            "Data_Acesso_Liberado": datetime.now().strftime("%d/%m/%Y"),
            "Data_Inicio_Periodo": dados_emp.get('Data_Inicio', ''),
            "Data_Fim_Periodo":    dados_emp.get('Data_Fim', ''),
            "Status":              "Ativo",
            "Data_Movimentacao":   "",
            "Motivo_Movimentacao": ""
        })

    if novos:
        df_novo = pd.DataFrame(novos)
        df_novo.to_csv(
            ARQUIVO_ACESSOS, mode='a', index=False, sep=';',
            header=not os.path.exists(ARQUIVO_ACESSOS), encoding='utf-8-sig'
        )

    return novos, duplicados, invalidos

def atualizar_status_cpf(cpf: str, novo_status: str, motivo: str = "") -> tuple:
    df = carregar_dados(ARQUIVO_ACESSOS)
    if df.empty:
        return False, "Banco de dados vazio."
    df = normalizar_status(df)
    mask = df['CPF'] == cpf
    if not mask.any():
        return False, f"CPF {cpf} não encontrado no sistema."
    df.loc[mask, 'Status']              = novo_status
    df.loc[mask, 'Data_Movimentacao']   = datetime.now().strftime("%d/%m/%Y")
    df.loc[mask, 'Motivo_Movimentacao'] = motivo
    df.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')
    empresa = df.loc[mask, 'Empresa'].iloc[0]
    return True, f"CPF {cpf} ({empresa}) atualizado para **{novo_status}**."

def atualizar_periodo_empresa(cnpj: str, data_inicio: str, data_fim: str) -> tuple:
    df = carregar_dados(ARQUIVO_ACESSOS)
    if df.empty:
        return False, "Banco de dados vazio."
    mask = df['CNPJ'] == cnpj
    if not mask.any():
        return False, f"CNPJ {cnpj} não encontrado."
    df.loc[mask, 'Data_Inicio_Periodo'] = data_inicio
    df.loc[mask, 'Data_Fim_Periodo']    = data_fim
    df.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')
    return True, f"Período atualizado para {data_inicio} → {data_fim}."

def periodo_valido(dados: dict) -> tuple:
    """Retorna (True, "") se dentro do período, ou (False, mensagem_erro)."""
    d_ini = dados.get('Data_Inicio_Periodo', '')
    d_fim = dados.get('Data_Fim_Periodo', '')
    if not d_ini or not d_fim:
        return True, ""
    try:
        hoje     = date.today()
        dt_ini   = datetime.strptime(d_ini, "%d/%m/%Y").date()
        dt_fim   = datetime.strptime(d_fim, "%d/%m/%Y").date()
        if hoje < dt_ini:
            return False, f"⏳ O questionário ainda não foi aberto. Período: **{d_ini}** a **{d_fim}**."
        if hoje > dt_fim:
            return False, f"⛔ O período encerrou em **{d_fim}**. Contate o RH ou a equipe SSTG para reabrir."
        return True, ""
    except Exception:
        return True, ""

# ─── QUESTÕES E DIMENSÕES (COPSOQ III) ────────────────────────────────────────
DEPARA = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "Frequentemente": 3, "Sempre": 4}
OPCOES = list(DEPARA.keys())

DIMENSOES = {
    "📦 Cargo": {
        "q1":  "01. Tenho pleno conhecimento sobre o que se espera do meu trabalho.",
        "q4":  "04. Eu sei como fazer o meu trabalho.",
        "q11": "11. Estão claras as minhas tarefas e responsabilidades.",
        "q13": "13. Os objetivos e metas do meu setor são claros para mim.",
        "q17": "17. Eu vejo como o meu trabalho se encaixa nos objetivos da empresa."
    },
    "🎮 Controle": {
        "q2":  "02. Posso decidir quando fazer uma pausa.",
        "q10": "10. Consideram a minha opinião sobre a velocidade do meu trabalho.",
        "q15": "15. Tenho liberdade de escolha de como fazer meu trabalho.",
        "q19": "19. Tenho liberdade de escolha para decidir o que fazer no meu trabalho.",
        "q25": "25. Minhas sugestões são consideradas sobre como fazer meu trabalho.",
        "q30": "30. O meu horário de trabalho pode ser flexível."
    },
    "⚖️ Demandas": {
        "q3":  "03. As exigências de trabalho são difíceis de combinar.",
        "q6":  "06. Tenho prazos inatingíveis.",
        "q9":  "09. Devo trabalhar muito intensamente.",
        "q12": "12. Deixo tarefas sem fazer por excesso de carga.",
        "q16": "16. Não tenho possibilidade de fazer pausas suficientes.",
        "q18": "18. Recebo pressão para trabalhar em outro horário.",
        "q20": "20. Tenho que fazer meu trabalho com muita rapidez.",
        "q22": "22. As pausas temporárias são impossíveis de cumprir."
    },
    "⚠️ Relacionamentos": {
        "q5":  "05. Falam ou se comportam comigo de forma dura.",
        "q14": "14. Existem conflitos entre os colegas.",
        "q21": "21. Sinto que sou perseguido no trabalho.",
        "q34": "34. As relações no trabalho são tensas."
    },
    "🤝 Apoio dos Colegas": {
        "q7":  "07. Posso contar com ajuda dos colegas.",
        "q24": "24. Meus colegas me dão apoio quando preciso.",
        "q27": "27. Meus colegas demonstram o respeito que mereço.",
        "q31": "31. Os colegas estão disponíveis para escutar meus problemas."
    },
    "👔 Apoio da Chefia": {
        "q8":  "08. Recebo informações e suporte que me ajudam no trabalho.",
        "q23": "23. Posso confiar no meu chefe.",
        "q29": "29. Quando algo me perturba posso falar com meu chefe.",
        "q33": "33. Tenho suportado trabalhos emocionalmente exigentes.",
        "q35": "35. Meu chefe me incentiva no trabalho."
    },
    "📢 Comunicação e Mudanças": {
        "q26": "26. Tenho oportunidades para pedir explicações sobre mudanças.",
        "q28": "28. As pessoas são consultadas sobre mudanças no trabalho.",
        "q32": "32. Quando há mudanças, faço o trabalho com o mesmo carinho."
    }
}

DIMS_INVERTIDAS = {"Demandas", "Relacionamentos"}

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1) — Diagnóstico Psicossocial",
    layout="wide",
    page_icon="🧠"
)

st.markdown("""
    <style translate="no">
    :root{--azul:#282C5B;--verde:#5A9F62;--laranja:#DC3B24;--cinza-e:#6B6966;--cinza-c:#EFEFEF;}
    [data-testid="stSidebar"]{background-color:var(--azul)!important;border-right:3px solid var(--verde);}
    [data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] div{color:#fff!important;}
    [data-testid="stSidebar"] hr{border-color:rgba(255,255,255,0.2);}
    [data-testid="stSidebar"] .stButton>button{background-color:rgba(255,255,255,0.12)!important;color:white!important;border:1px solid rgba(255,255,255,0.3)!important;border-radius:8px!important;}
    [data-testid="stSidebar"] .stButton>button:hover{background-color:rgba(255,255,255,0.22)!important;}
    .stTabs [data-baseweb="tab-list"]{gap:4px;background-color:#fff;border-radius:10px;padding:6px;box-shadow:0 2px 6px rgba(0,0,0,0.06);}
    .stTabs [aria-selected="true"]{background-color:var(--azul)!important;color:white!important;border-radius:7px!important;font-weight:600!important;}
    .stTabs [aria-selected="false"]{color:var(--cinza-e)!important;border-radius:7px!important;}
    .stTabs [aria-selected="false"]:hover{background-color:var(--cinza-c)!important;}
    [data-testid="stButton"]>button[kind="primary"]{background-color:var(--laranja)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:700!important;font-size:1em!important;letter-spacing:.6px;padding:.6em 1.2em!important;box-shadow:0 4px 12px rgba(220,59,36,.30)!important;transition:all .2s ease!important;}
    [data-testid="stButton"]>button[kind="primary"]:hover{background-color:#b52d1a!important;box-shadow:0 6px 18px rgba(220,59,36,.40)!important;transform:translateY(-1px);}
    [data-testid="stButton"]>button[kind="secondary"]{border:2px solid var(--azul)!important;color:var(--azul)!important;border-radius:10px!important;font-weight:600!important;}
    [data-testid="stMetricValue"]{color:var(--azul)!important;font-weight:800!important;font-size:2em!important;}
    [data-testid="stMetricLabel"]{color:var(--cinza-e)!important;}
    h1{color:var(--azul)!important;font-weight:800!important;}
    h2,h3{color:var(--azul)!important;font-weight:700!important;}
    .stProgress>div>div>div{background:linear-gradient(90deg,var(--verde),var(--azul))!important;border-radius:10px!important;}
    [data-testid="stForm"]{background:white;border-radius:14px;padding:28px;border:1px solid #e0e0e0;box-shadow:0 2px 12px rgba(0,0,0,0.06);}
    .hero-sstg{background:linear-gradient(135deg,#282C5B 0%,#1e3a8a 55%,#5A9F62 100%);padding:48px 40px;border-radius:18px;color:white;text-align:center;margin-bottom:32px;box-shadow:0 8px 32px rgba(40,44,91,0.25);}
    .hero-sstg h1{color:white!important;font-size:2em!important;margin-bottom:8px;}
    .hero-sstg p{font-size:1.1em;opacity:.88;margin:0;}
    .trust-row{display:flex;justify-content:center;gap:32px;margin:28px 0 8px 0;}
    .trust-badge{text-align:center;background:rgba(255,255,255,0.12);border-radius:12px;padding:14px 20px;min-width:110px;backdrop-filter:blur(4px);}
    .trust-badge .icon{font-size:1.8em;}
    .trust-badge .label{font-size:.78em;color:rgba(255,255,255,0.85);margin-top:4px;}
    .mensagem-motivadora{font-size:1.05em;color:var(--azul);text-align:justify;padding:22px 28px;border-radius:12px;background-color:rgba(90,159,98,0.08);border-left:5px solid var(--verde);margin-bottom:24px;line-height:1.7;}
    [data-testid="stExpander"]{border:1px solid #e0e0e0;border-radius:10px;}
    hr{border-color:#e8e8e8!important;}
    [data-testid="stDownloadButton"]>button{border:2px solid var(--verde)!important;color:var(--verde)!important;border-radius:10px!important;font-weight:600!important;}
    </style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists("logo_sstg.png"):
        st.image("logo_sstg.png", use_container_width=True)
        st.markdown("""
            <div style="text-align:center; padding: 0 0 10px 0;">
                <span style="font-size:1.1em; font-weight:800; color:white; letter-spacing:1px;">
                    DRPS
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align:center; padding: 10px 0 20px 0;">
                <span style="font-size:1.4em; font-weight:800; color:white; letter-spacing:1px;">
                    SSTG E-SOCIAL
                </span><br>
                <span style="font-size:0.75em; color:rgba(255,255,255,0.65); letter-spacing:2px;">
                    GESTÃO OCUPACIONAL
                </span><br>
                <span style="font-size:1.1em; font-weight:800; color:white; letter-spacing:1px; margin-top:8px; display:block;">
                    DRPS
                </span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    menu = st.radio("Módulo:", ["📋 Questionário Psicossocial", "📊 Gestão das Respostas (RH)", "🔐 Admin SSTG (Gestão)"])
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.7em; opacity:0.5; text-align:center;'>v6.0 — Diagnóstico Psicossocial<br>COPSOQ III</p>",
        unsafe_allow_html=True
    )

# =============================================================================
# MÓDULO ADMINISTRATIVO
# =============================================================================
if menu == "🔐 Admin SSTG (Gestão)":

    if 'admin_logado' not in st.session_state:
        st.session_state.admin_logado = False

    if not st.session_state.admin_logado:
        st.title("🔐 Acesso Restrito — Admin SSTG")
        senha = st.text_input("Senha do administrador:", type="password")
        if st.button("Entrar", use_container_width=True):
            if senha == SENHA_ADMIN:
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        st.stop()

    st.title("🏢 Gestão de Empresas e Acessos")

    if st.sidebar.button("🚪 Sair do Admin"):
        st.session_state.admin_logado = False
        st.rerun()

    # ── MENU DE DOCUMENTAÇÃO ──────────────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.subheader("📚 Documentação")

    with st.sidebar.expander("📖 Guias e Tutoriais", expanded=False):
        col1, col2 = st.columns(2)

        # README
        with col1:
            st.markdown("**Visão Geral**")
            if st.button("📄 README", use_container_width=True, key="btn_readme"):
                st.session_state.doc_view = "readme"
                st.rerun()

        # TUTORIAL
        with col2:
            st.markdown("**Tutorial RH**")
            if st.button("👥 TUTORIAL", use_container_width=True, key="btn_tutorial"):
                st.session_state.doc_view = "tutorial"
                st.rerun()

        st.markdown("---")

        # INSTALAÇÃO
        with col1:
            st.markdown("**Instalação**")
            if st.button("🚀 SETUP", use_container_width=True, key="btn_instalacao"):
                st.session_state.doc_view = "instalacao"
                st.rerun()

        # TÉCNICO
        with col2:
            st.markdown("**Técnico**")
            if st.button("🔧 TÉCNICO", use_container_width=True, key="btn_tecnico"):
                st.session_state.doc_view = "tecnico"
                st.rerun()

        st.markdown("---")

        # CHECKLIST
        st.markdown("**Lançamento**")
        if st.button("✅ CHECKLIST", use_container_width=True, key="btn_checklist"):
            st.session_state.doc_view = "checklist"
            st.rerun()

        st.markdown("---")

        # DOCUMENTAÇÃO DE PUBLICAÇÃO
        st.markdown("**Publicação**")
        if st.button("🚀 PUBLICAÇÃO", use_container_width=True, key="btn_publicacao"):
            st.session_state.doc_view = "publicacao"
            st.rerun()

        st.caption("Clique em um guia para visualizar")

    # ── VISUALIZADOR DE DOCUMENTAÇÃO ──────────────────────────────────────────
    if hasattr(st.session_state, 'doc_view') and st.session_state.doc_view:
        st.sidebar.divider()

        doc_selecionado = {
            "readme": ("README.md", "📄 Visão Geral do Sistema"),
            "tutorial": ("TUTORIAL.md", "👥 Tutorial Operacional"),
            "instalacao": ("GUIA_INSTALACAO.md", "🚀 Guia de Instalação"),
            "tecnico": ("GUIA_TECNICO.md", "🔧 Documentação Técnica"),
            "checklist": ("CHECKLIST_LANCAMENTO.md", "✅ Checklist de Lançamento")
        }

        if st.session_state.doc_view in doc_selecionado:
            arquivo_md, titulo = doc_selecionado[st.session_state.doc_view]
            arquivo_pdf = arquivo_md.replace('.md', '.pdf')
            caminho_md = caminho(arquivo_md)
            caminho_pdf = caminho(arquivo_pdf)

            # Exibir no sidebar
            st.sidebar.info(f"📖 Visualizando: {titulo}")

            # Botão para fechar
            if st.sidebar.button("❌ Fechar Documentação", use_container_width=True):
                st.session_state.doc_view = None
                st.rerun()

            st.sidebar.divider()

            # Downloads
            st.sidebar.markdown("**Baixar:**")
            try:
                # Download PDF
                with open(caminho_pdf, 'rb') as f:
                    st.sidebar.download_button(
                        label="⬇️ PDF",
                        data=f.read(),
                        file_name=arquivo_pdf,
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"btn_pdf_{st.session_state.doc_view}"
                    )

                # Download Markdown
                with open(caminho_md, 'r', encoding='utf-8') as f:
                    st.sidebar.download_button(
                        label="⬇️ Markdown",
                        data=f.read(),
                        file_name=arquivo_md,
                        mime="text/plain",
                        use_container_width=True,
                        key=f"btn_md_{st.session_state.doc_view}"
                    )
            except FileNotFoundError:
                st.sidebar.warning("Arquivo de documentação não encontrado")

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🆕 Cadastro / Inclusão",
        "📋 Conferência e Correção",
        "📊 Resultados",
        "🔄 Movimentação de Pessoal",
        "🔐 Segurança e Acesso RH",
        "📚 Documentação"
    ])

    # ── ABA 1: CADASTRO ───────────────────────────────────────────────────────
    with t1:
        st.subheader("Nova Empresa — Cadastro de Colaboradores")

        tab_manual, tab_csv = st.tabs(["✏️ Entrada Manual", "📊 Importar via CSV"])

        # ── MÉTODO 1: MANUAL ──────────────────────────────────────────────────
        with tab_manual:
            with st.form("form_admin", clear_on_submit=True):
                # Dados da empresa
                col1, col2 = st.columns(2)
                cnpj  = col1.text_input("CNPJ (somente números)", placeholder="00000000000100")
                razao = col2.text_input("Razão Social")

                # Período de aplicação
                st.markdown("**Período de aplicação do questionário**")
                c_ini, c_fim = st.columns(2)
                dt_ini = c_ini.date_input("Data de início", value=date.today(), format="DD/MM/YYYY")
                dt_fim = c_fim.date_input("Data de encerramento", value=date.today(), format="DD/MM/YYYY")

                # Tabela de colaboradores
                st.markdown("**Colaboradores autorizados**")
                st.caption("Preencha CPF, Função e Departamento. Clique em ➕ para adicionar linhas.")

                df_vazio = pd.DataFrame({
                    "CPF":          pd.Series(dtype=str),
                    "Função":       pd.Series(dtype=str),
                    "Departamento": pd.Series(dtype=str),
                })
                df_editado = st.data_editor(
                    df_vazio,
                    num_rows="dynamic",
                    column_config={
                        "CPF":          st.column_config.TextColumn("CPF (11 dígitos)", required=True, max_chars=14),
                        "Função":       st.column_config.TextColumn("Função / Cargo"),
                        "Departamento": st.column_config.TextColumn("Departamento / Setor"),
                    },
                    use_container_width=True,
                    key="tabela_cadastro"
                )

                submitted = st.form_submit_button("✅ SALVAR E LIBERAR ACESSOS", use_container_width=True)
                if submitted:
                    cnpj_limpo = cnpj.strip().replace(".", "").replace("/", "").replace("-", "")
                    if not cnpj_limpo or not razao.strip():
                        st.error("Preencha CNPJ e Razão Social.")
                    elif dt_fim < dt_ini:
                        st.error("A data de encerramento não pode ser anterior à data de início.")
                    else:
                        colaboradores = df_editado.dropna(subset=["CPF"]).to_dict('records')
                        if not colaboradores:
                            st.error("Adicione ao menos um colaborador na tabela.")
                        else:
                            dados_emp = {
                                "CNPJ":        cnpj_limpo,
                                "Razão Social": razao.strip(),
                                "Data_Inicio": dt_ini.strftime("%d/%m/%Y"),
                                "Data_Fim":    dt_fim.strftime("%d/%m/%Y"),
                            }
                            novos, duplicados, invalidos = salvar_cadastro_completo(dados_emp, colaboradores)

                            # Gerar senha de acesso RH
                            if novos:
                                senha_rh = gerar_senha_rh()
                                # Salvar senha hash no arquivo de acessos (em nova coluna)
                                df_acessos = carregar_dados(ARQUIVO_ACESSOS)
                                if 'Senha_RH_Hash' not in df_acessos.columns:
                                    df_acessos['Senha_RH_Hash'] = ''
                                df_acessos.loc[df_acessos['CNPJ'] == cnpj_limpo, 'Senha_RH_Hash'] = hash_senha(senha_rh)
                                df_acessos.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')

                                st.success(f"✅ {len(novos)} colaborador(es) cadastrado(s) com sucesso.")
                                st.session_state.cnpj_registrado = cnpj_limpo
                                st.session_state.razao_registrada = razao.strip()

                                # Exibir informações de acesso RH
                                st.divider()
                                st.subheader("🔐 Credenciais de Acesso RH")
                                st.info(f"Empresa: **{razao.strip()}**\nCNPJ: **{cnpj_limpo}**")
                                st.code(f"Senha de Acesso RH: {senha_rh}", language=None)
                                st.warning("⚠️ **Anote esta senha com segurança!** Esta é a única vez que ela será exibida. Compartilhe com o RH da empresa.")

                            if duplicados:
                                st.warning(f"⚠️ CPF(s) já cadastrados: {', '.join(duplicados)}")
                            if invalidos:
                                st.error(f"❌ CPF(s) inválidos: {', '.join(invalidos)}")

        # ── MÉTODO 2: IMPORTAÇÃO VIA CSV ──────────────────────────────────────
        with tab_csv:
            st.markdown("### Importar Colaboradores via Arquivo CSV")
            st.info("Faça download do template, preencha com os dados dos colaboradores e envie o arquivo.")

            # Template para download
            template_df = pd.DataFrame({
                "CPF": ["12345678901", "98765432109"],
                "Função": ["Desenvolvedor", "Analista"],
                "Departamento": ["TI", "RH"]
            })
            template_csv = template_df.to_csv(index=False, sep=';', encoding='utf-8-sig')

            st.download_button(
                label="⬇️ Baixar Template CSV",
                data=template_csv,
                file_name="template_colaboradores.csv",
                mime="text/csv"
            )

            st.markdown("---")

            # Dados da empresa
            col1, col2 = st.columns(2)
            cnpj_csv = col1.text_input("CNPJ (somente números)", placeholder="00000000000100", key="cnpj_csv")
            razao_csv = col2.text_input("Razão Social", key="razao_csv")

            # Período de aplicação
            st.markdown("**Período de aplicação do questionário**")
            c_ini_csv, c_fim_csv = st.columns(2)
            dt_ini_csv = c_ini_csv.date_input("Data de início", value=date.today(), format="DD/MM/YYYY", key="dt_ini_csv")
            dt_fim_csv = c_fim_csv.date_input("Data de encerramento", value=date.today(), format="DD/MM/YYYY", key="dt_fim_csv")

            st.markdown("---")
            st.markdown("**Selecione o arquivo CSV**")
            uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"], key="upload_csv")

            if uploaded_file:
                try:
                    df_upload = pd.read_csv(uploaded_file, sep=';')

                    # Validações
                    colunas_obrig = {"CPF", "Função", "Departamento"}
                    if not colunas_obrig.issubset(df_upload.columns):
                        st.error(f"❌ O arquivo deve conter as colunas: {', '.join(colunas_obrig)}")
                    else:
                        st.success(f"✅ Arquivo válido: {len(df_upload)} linhas detectadas")
                        st.dataframe(df_upload, use_container_width=True)

                        if st.button("💾 SALVAR COLABORADORES DO CSV", use_container_width=True):
                            cnpj_limpo_csv = cnpj_csv.strip().replace(".", "").replace("/", "").replace("-", "")
                            if not cnpj_limpo_csv or not razao_csv.strip():
                                st.error("Preencha CNPJ e Razão Social.")
                            elif dt_fim_csv < dt_ini_csv:
                                st.error("A data de encerramento não pode ser anterior à data de início.")
                            else:
                                colaboradores_csv = df_upload.dropna(subset=["CPF"]).to_dict('records')
                                if not colaboradores_csv:
                                    st.error("Nenhum colaborador válido encontrado no arquivo.")
                                else:
                                    dados_emp_csv = {
                                        "CNPJ":        cnpj_limpo_csv,
                                        "Razão Social": razao_csv.strip(),
                                        "Data_Inicio": dt_ini_csv.strftime("%d/%m/%Y"),
                                        "Data_Fim":    dt_fim_csv.strftime("%d/%m/%Y"),
                                    }
                                    novos, duplicados, invalidos = salvar_cadastro_completo(dados_emp_csv, colaboradores_csv)

                                    # Gerar senha de acesso RH
                                    if novos:
                                        senha_rh = gerar_senha_rh()
                                        # Salvar senha hash no arquivo de acessos
                                        df_acessos = carregar_dados(ARQUIVO_ACESSOS)
                                        if 'Senha_RH_Hash' not in df_acessos.columns:
                                            df_acessos['Senha_RH_Hash'] = ''
                                        df_acessos.loc[df_acessos['CNPJ'] == cnpj_limpo_csv, 'Senha_RH_Hash'] = hash_senha(senha_rh)
                                        df_acessos.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')

                                        st.success(f"✅ {len(novos)} colaborador(es) cadastrado(s) com sucesso.")
                                        st.session_state.cnpj_registrado = cnpj_limpo_csv
                                        st.session_state.razao_registrada = razao_csv.strip()

                                        # Exibir informações de acesso RH
                                        st.divider()
                                        st.subheader("🔐 Credenciais de Acesso RH")
                                        st.info(f"Empresa: **{razao_csv.strip()}**\nCNPJ: **{cnpj_limpo_csv}**")
                                        st.code(f"Senha de Acesso RH: {senha_rh}", language=None)
                                        st.warning("⚠️ **Anote esta senha com segurança!** Esta é a única vez que ela será exibida. Compartilhe com o RH da empresa.")

                                    if duplicados:
                                        st.warning(f"⚠️ CPF(s) já cadastrados: {', '.join(duplicados)}")
                                    if invalidos:
                                        st.error(f"❌ CPF(s) inválidos: {', '.join(invalidos)}")
                except Exception as e:
                    st.error(f"❌ Erro ao ler arquivo: {str(e)}")

        st.divider()
        st.subheader("🔗 Link do Questionário para Compartilhar")

        df_emp_links = carregar_dados(ARQUIVO_ACESSOS)
        if not df_emp_links.empty:
            empresas_unicas = df_emp_links.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].values
            for _, (empresa, cnpj_emp) in enumerate(empresas_unicas):
                link = f"{SHARE_URL}/?cnpj={cnpj_emp}"
                col_empr, col_link = st.columns([2, 3])
                col_empr.write(f"**{empresa}**")
                col_link.code(link)
            st.caption("Copie e envie o link correspondente ao RH da empresa via WhatsApp, Email ou outro canal.")
        else:
            st.info("Nenhuma empresa registrada ainda.")

    # ── ABA 2: CONFERÊNCIA ────────────────────────────────────────────────────
    with t2:
        st.subheader("Cadastro Geral de Colaboradores Autorizados")
        df_verif = carregar_dados(ARQUIVO_ACESSOS)

        if not df_verif.empty:
            df_verif = normalizar_status(df_verif)
            ativos   = (df_verif['Status'] == 'Ativo').sum()
            inativos = (df_verif['Status'] == 'Inativo').sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total de CPFs", len(df_verif))
            c2.metric("✅ Ativos",  ativos)
            c3.metric("🚫 Inativos", inativos)
            ultimo = df_verif['Data_Acesso_Liberado'].iloc[-1] if 'Data_Acesso_Liberado' in df_verif.columns else "—"
            c4.metric("Último cadastro", ultimo)

            st.divider()

            empresas_lista = ["Todas"] + df_verif['Empresa'].unique().tolist()
            filtro     = st.selectbox("Filtrar por empresa:", empresas_lista, key="filtro_conf")
            df_filtrado = df_verif if filtro == "Todas" else df_verif[df_verif['Empresa'] == filtro]

            # Colunas a exibir (oculta colunas internas)
            cols_show = [c for c in df_filtrado.columns if c not in ('Setores_Base', 'Funções_Base')]
            st.dataframe(df_filtrado[cols_show], use_container_width=True)

            csv_export = df_filtrado[cols_show].to_csv(index=False, sep=';', encoding='utf-8-sig')
            st.download_button("⬇️ Baixar lista filtrada (.csv)", csv_export, "cadastro_cpfs.csv", "text/csv")

            st.divider()

            # Gerenciar período
            with st.expander("📅 Gerenciar Período de Aplicação"):
                st.info("Altere as datas para reabrir ou encerrar o período de um questionário.")
                empresas_per = df_verif.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                    lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                ).tolist()
                emp_per = st.selectbox("Empresa:", empresas_per, key="emp_periodo")
                cnpj_per = emp_per.split("CNPJ: ")[-1]

                # Busca datas atuais
                linha_ref = df_verif[df_verif['CNPJ'] == cnpj_per].iloc[0]
                def parse_date(s, fallback):
                    try:
                        return datetime.strptime(str(s), "%d/%m/%Y").date()
                    except Exception:
                        return fallback

                ini_atual = parse_date(linha_ref.get('Data_Inicio_Periodo', ''), date.today())
                fim_atual = parse_date(linha_ref.get('Data_Fim_Periodo', ''),    date.today())

                cp1, cp2 = st.columns(2)
                novo_ini = cp1.date_input("Nova data de início",      ini_atual, format="DD/MM/YYYY", key="per_ini")
                novo_fim = cp2.date_input("Nova data de encerramento", fim_atual, format="DD/MM/YYYY", key="per_fim")

                if st.button("💾 SALVAR PERÍODO", key="btn_per"):
                    if novo_fim < novo_ini:
                        st.error("Data de encerramento anterior ao início.")
                    else:
                        ok, msg = atualizar_periodo_empresa(
                            cnpj_per,
                            novo_ini.strftime("%d/%m/%Y"),
                            novo_fim.strftime("%d/%m/%Y")
                        )
                        st.success(msg) if ok else st.error(msg)

            with st.expander("⚠️ Zona de Perigo — use com cuidado"):
                st.error("⚠️ As ações abaixo são **irreversíveis**. Confirme com a senha do Admin SSTG antes de prosseguir.")

                zt1, zt2 = st.tabs(["🗑️ Excluir Empresa", "💣 Resetar Tudo"])

                # ── EXCLUIR EMPRESA INDIVIDUAL ────────────────────────────────
                with zt1:
                    st.warning("Remove **todos os acessos** e **todo o histórico de respostas** da empresa selecionada.")
                    df_zona = carregar_dados(ARQUIVO_ACESSOS)
                    if not df_zona.empty:
                        empresas_zona = df_zona.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                            lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                        ).tolist()
                        emp_del = st.selectbox("Empresa a excluir:", empresas_zona, key="zona_emp_del")
                        cnpj_del = emp_del.split("CNPJ: ")[-1]
                        nome_del = emp_del.split(" — CNPJ:")[0].strip()

                        # Contadores para exibir impacto
                        qtd_cpfs  = len(df_zona[df_zona['CNPJ'] == cnpj_del])
                        arq_resp  = caminho(f"respostas_CNPJ_{cnpj_del}.csv")
                        qtd_resp  = len(pd.read_csv(arq_resp, sep=';', dtype=str)) if os.path.exists(arq_resp) else 0

                        col_info1, col_info2 = st.columns(2)
                        col_info1.metric("CPFs que serão removidos", qtd_cpfs)
                        col_info2.metric("Respostas que serão apagadas", qtd_resp)

                        st.divider()
                        st.markdown("**Confirme digitando a senha do Admin SSTG:**")
                        senha_conf_del = st.text_input(
                            "Senha Admin:", type="password", key="senha_conf_emp_del"
                        )

                        if st.button("🗑️ EXCLUIR EMPRESA E TODO O HISTÓRICO", type="primary",
                                     use_container_width=True, key="btn_del_empresa"):
                            if not senha_conf_del:
                                st.error("Digite a senha do Admin para confirmar.")
                            elif senha_conf_del != SENHA_ADMIN:
                                st.error("❌ Senha incorreta. Operação cancelada.")
                            else:
                                # 1. Remove os CPFs da empresa no arquivo de acessos
                                df_zona_upd = df_zona[df_zona['CNPJ'] != cnpj_del]
                                df_zona_upd.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')
                                # 2. Remove arquivo de respostas da empresa
                                if os.path.exists(arq_resp):
                                    os.remove(arq_resp)
                                st.success(f"✅ Empresa **{nome_del}** removida com sucesso. {qtd_cpfs} acesso(s) e {qtd_resp} resposta(s) apagadas.")
                                st.rerun()
                    else:
                        st.info("Nenhuma empresa cadastrada.")

                # ── RESETAR TUDO ──────────────────────────────────────────────
                with zt2:
                    st.warning("Remove **TODOS** os registros de acesso e **TODOS** os históricos de resposta de **todas** as empresas.")
                    senha_conf_all = st.text_input(
                        "Senha Admin para confirmar reset total:", type="password", key="senha_conf_reset_all"
                    )
                    if st.button("💣 RESETAR BANCO DE DADOS COMPLETO", type="primary",
                                 use_container_width=True, key="btn_reset_all"):
                        if not senha_conf_all:
                            st.error("Digite a senha do Admin para confirmar.")
                        elif senha_conf_all != SENHA_ADMIN:
                            st.error("❌ Senha incorreta. Operação cancelada.")
                        else:
                            # Remove arquivo de acessos
                            if os.path.exists(ARQUIVO_ACESSOS):
                                os.remove(ARQUIVO_ACESSOS)
                            # Remove todos os arquivos de respostas por empresa
                            for arq in glob.glob(caminho("respostas_CNPJ_*.csv")):
                                os.remove(arq)
                            st.success("✅ Banco de dados completo resetado.")
                            st.rerun()
        else:
            st.info("Nenhum registro encontrado. Faça o cadastro na aba anterior.")

    # ── ABA 3: RESULTADOS ─────────────────────────────────────────────────────
    with t3:
        st.subheader("Resultados Consolidados por Empresa")
        df_acessos = carregar_dados(ARQUIVO_ACESSOS)

        if not df_acessos.empty:
            opcoes_empresa = df_acessos.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
            ).tolist()
            empresa_sel = st.selectbox("Selecione a empresa:", opcoes_empresa)
            cnpj_cod    = empresa_sel.split("CNPJ: ")[-1]
            nome_res    = caminho(f"respostas_CNPJ_{cnpj_cod}.csv")

            # ── Link individualizado ──────────────────────────────────────────
            with st.expander("🔗 Link do Questionário para esta empresa"):
                link_emp = f"{SHARE_URL}/?cnpj={cnpj_cod}"
                st.code(link_emp, language=None)
                st.caption(
                    "Copie e envie este link para o RH da empresa repassar aos colaboradores. "
                    "Este é o link público que funciona em qualquer dispositivo, conectado à internet."
                )

            # ── Gerar Imagem de Compartilhamento ──────────────────────────────────
            with st.expander("🖼️ Gerar QRCode do Questionário para Compartilhamento"):
                st.info("Gere uma imagem com QR Code para compartilhar nas redes sociais ou enviar por email.")

                if COMPARTILHAMENTO_DISPONIVEL:
                    col_gerar, col_espacador = st.columns([2, 1])

                    with col_gerar:
                        if st.button("🎨 Gerar Imagem com QR Code", use_container_width=True, key="btn_gerar_img"):
                            try:
                                nome_empresa = empresa_sel.split(" — CNPJ:")[0].strip()

                                with st.spinner("Gerando imagem..."):
                                    img_bytes = gerar_imagem_compartilhamento_simples(
                                        empresa_nome=nome_empresa,
                                        cnpj=cnpj_cod,
                                        app_url=SHARE_URL
                                    )

                                st.success("Imagem gerada com sucesso!")

                                # Exibir preview
                                st.image(img_bytes, use_column_width=True, caption=f"Imagem de compartilhamento: {nome_empresa}")

                                # Download button
                                st.download_button(
                                    "⬇️ Baixar Imagem (PNG)",
                                    img_bytes,
                                    f"compartilhamento_{cnpj_cod}.png",
                                    "image/png",
                                    use_container_width=True
                                )

                                # Opções de compartilhamento
                                st.divider()
                                st.subheader("📤 Compartilhar Imagem com RH/Respondentes")

                                col1, col2 = st.columns(2)
                                with col1:
                                    whatsapp_link = f"https://wa.me/?text=Prezado(a)%20RH%2C%0A%0AConvido-o%20a%20participar%20da%20avaliação%20de%20Riscos%20Psicossociais%20(SSTG-DRPS)%20através%20do%20link%3A%20{SHARE_URL}%2F%3Fcnpj%3D{cnpj_cod}%0A%0AEsta%20é%20uma%20ferramenta%20essencial%20para%20diagnóstico%20do%20ambiente%20de%20trabalho%20conforme%20NR-1.%0A%0AObrigado!"
                                    st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📱 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

                                with col2:
                                    email_link = f"mailto:?subject=Avaliação de Riscos Psicossociais - SSTG DRPS&body=Prezado(a) RH,%0A%0AConvido-o a participar da avaliação de Riscos Psicossociais (SSTG-DRPS) conforme NR-1.%0A%0ALink para acesso:%0A{SHARE_URL}/?cnpj={cnpj_cod}%0A%0AEsta avaliação é fundamental para diagnóstico do ambiente de trabalho.%0A%0AObrigado!"
                                    st.markdown(f'<a href="{email_link}"><button style="width:100%; padding:10px; background-color:#0078D4; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📧 Enviar via Email</button></a>', unsafe_allow_html=True)

                                st.caption("💡 Dica: Use esta imagem em emails, WhatsApp, Telegram ou redes sociais para aumentar a adesão ao questionário.")

                            except Exception as e:
                                st.error(f"Erro ao gerar imagem: {e}")
                else:
                    st.warning("Módulo de compartilhamento não disponível. Verifique se `qrcode` e `Pillow` estão instalados.")

            if os.path.exists(nome_res):
                df_res = pd.read_csv(nome_res, sep=';', dtype=str)

                total_auth = len(df_acessos[df_acessos['CNPJ'] == cnpj_cod])
                total_resp = len(df_res)
                pct        = round((total_resp / total_auth) * 100, 1) if total_auth > 0 else 0

                c1, c2, c3 = st.columns(3)
                c1.metric("CPFs Autorizados",   total_auth)
                c2.metric("Respostas Recebidas", total_resp)
                c3.metric("Taxa de Adesão",      f"{pct}%")

                # Gráfico de adesão
                st.subheader("📊 Adesão ao Questionário")
                df_chart = pd.DataFrame({
                    "Questionários": {"Autorizados": total_auth, "Respondidos": total_resp}
                })
                st.bar_chart(df_chart, use_container_width=True, height=280)

                st.divider()

                # Médias por dimensão
                cols_media = [c for c in df_res.columns if c.startswith('Media_') and c != 'Media_Geral']
                if cols_media:
                    st.subheader("Médias por Dimensão (escala 0 a 4)")
                    df_num  = df_res[cols_media].apply(pd.to_numeric, errors='coerce')
                    medias  = df_num.mean()
                    cols_d  = st.columns(len(cols_media))
                    for i, (col_nome, val) in enumerate(medias.items()):
                        nome_exib = col_nome.replace("Media_", "").replace("_", " ")
                        cols_d[i].metric(nome_exib, f"{val:.2f}")

                st.divider()
                st.subheader("Histórico de Respostas")
                colunas_exibir = [c for c in df_res.columns if c != 'CPF_Hash']
                st.dataframe(df_res[colunas_exibir], use_container_width=True)

                csv_res = df_res[colunas_exibir].to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    "⬇️ Baixar resultados (.csv)",
                    csv_res, f"resultados_{cnpj_cod}.csv", "text/csv"
                )

                # ── Gerar Laudo PDF ───────────────────────────────────────────
                st.divider()
                st.subheader("📄 Gerar Laudo de Fatores Psicossociais (PDF)")

                if not LAUDO_DISPONIVEL:
                    st.error("Módulo `gerar_laudo.py` não encontrado na pasta do projeto.")
                elif cols_media:
                    with st.expander("⚙️ Dados complementares para o laudo (opcional)", expanded=True):
                        col_a, col_b = st.columns(2)
                        cnae_laudo  = col_a.text_input("CNAE Principal:", placeholder="Ex: 4711-3/02", key="cnae_laudo")
                        grau_laudo  = col_b.selectbox("Grau de Risco:", ["—", "1", "2", "3", "4"], key="grau_laudo")

                    if st.button("📄 Gerar Laudo PDF", type="primary", use_container_width=True):
                        with st.spinner("Gerando laudo..."):
                            nome_empresa   = empresa_sel.split(" — CNPJ:")[0].strip()
                            df_num_laudo   = df_res[cols_media].apply(pd.to_numeric, errors='coerce')
                            medias_laudo   = df_num_laudo.mean().to_dict()
                            medias_dim     = {}
                            for col, val in medias_laudo.items():
                                nome_dim = col.replace("Media_", "")
                                dim_key  = f"Dim_{nome_dim}"
                                medias_dim[dim_key] = round(4.0 - val, 2) if nome_dim in DIMS_INVERTIDAS else val

                            dados_emp = {
                                "Empresa":    nome_empresa,
                                "CNPJ":       cnpj_cod,
                                "CNAE":       cnae_laudo or "—",
                                "Grau_Risco": grau_laudo if grau_laudo != "—" else "—",
                            }
                            logo_path = "logo_sstg.png" if os.path.exists("logo_sstg.png") else None
                            try:
                                pdf_bytes = gerar_laudo_pdf(
                                    dados_empresa=dados_emp,
                                    medias_por_dim=medias_dim,
                                    total_respondentes=total_resp,
                                    logo_path=logo_path,
                                )
                                st.success("Laudo gerado com sucesso!")
                                st.download_button(
                                    "⬇️ Baixar Laudo PDF",
                                    pdf_bytes,
                                    f"laudo_psicossocial_{cnpj_cod}.pdf",
                                    "application/pdf",
                                    use_container_width=True,
                                )
                            except Exception as e:
                                st.error(f"Erro ao gerar o laudo: {e}")
                else:
                    st.warning("Sem dados de médias por dimensão. Verifique se há respostas registradas.")

            else:
                st.info("Nenhuma resposta registrada ainda para esta empresa.")
        else:
            st.info("Nenhuma empresa cadastrada. Faça o cadastro primeiro.")

    # ── ABA 4: MOVIMENTAÇÃO DE PESSOAL ────────────────────────────────────────
    with t4:
        st.subheader("Movimentação de Pessoal")
        df_mov = carregar_dados(ARQUIVO_ACESSOS)

        if df_mov.empty:
            st.info("Nenhuma empresa cadastrada. Faça o cadastro primeiro.")
        else:
            df_mov = normalizar_status(df_mov)
            m1, m2, m3 = st.tabs(["➕ Admissão", "🚫 Desligamento", "✅ Reativação"])

            # ── ADMISSÃO ─────────────────────────────────────────────────────
            with m1:
                st.markdown("#### Incluir colaborador(es) em empresa já cadastrada")
                empresas_mov = df_mov.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                    lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                ).tolist()
                empresa_adm  = st.selectbox("Empresa:", empresas_mov, key="emp_adm")
                cnpj_adm     = empresa_adm.split("CNPJ: ")[-1]
                ref_adm      = df_mov[df_mov['CNPJ'] == cnpj_adm].iloc[0]

                st.caption("Preencha CPF, Função e Departamento dos novos colaboradores.")
                df_adm_vazio = pd.DataFrame({
                    "CPF":          pd.Series(dtype=str),
                    "Função":       pd.Series(dtype=str),
                    "Departamento": pd.Series(dtype=str),
                })
                df_adm_edit = st.data_editor(
                    df_adm_vazio,
                    num_rows="dynamic",
                    column_config={
                        "CPF":          st.column_config.TextColumn("CPF (11 dígitos)", required=True, max_chars=14),
                        "Função":       st.column_config.TextColumn("Função / Cargo"),
                        "Departamento": st.column_config.TextColumn("Departamento / Setor"),
                    },
                    use_container_width=True,
                    key="tabela_adm"
                )

                if st.button("➕ INCLUIR COLABORADORES", use_container_width=True, key="btn_adm"):
                    colaboradores_adm = df_adm_edit.dropna(subset=["CPF"]).to_dict('records')
                    if not colaboradores_adm:
                        st.error("Adicione ao menos um colaborador na tabela.")
                    else:
                        dados_adm = {
                            "CNPJ":        cnpj_adm,
                            "Razão Social": ref_adm['Empresa'],
                            "Data_Inicio": ref_adm.get('Data_Inicio_Periodo', ''),
                            "Data_Fim":    ref_adm.get('Data_Fim_Periodo', ''),
                        }
                        novos, duplicados, invalidos = salvar_cadastro_completo(dados_adm, colaboradores_adm)
                        if novos:
                            st.success(f"✅ {len(novos)} colaborador(es) incluído(s).")
                        if duplicados:
                            st.warning(f"⚠️ Já cadastrados: {', '.join(duplicados)}")
                        if invalidos:
                            st.error(f"❌ CPFs inválidos: {', '.join(invalidos)}")

            # ── DESLIGAMENTO ─────────────────────────────────────────────────
            with m2:
                st.markdown("#### Inativar colaborador desligado")
                st.info("O CPF ficará bloqueado para responder, mas o histórico é preservado.")

                col1, col2 = st.columns([2, 1])
                cpf_desl    = col1.text_input("CPF (somente números):", max_chars=11, key="cpf_desl")
                motivo_desl = col2.selectbox(
                    "Motivo:", ["Demissão", "Pedido de demissão", "Aposentadoria", "Transferência", "Outro"],
                    key="motivo_desl"
                )

                if cpf_desl and len(cpf_desl) == 11:
                    reg_desl = df_mov[df_mov['CPF'] == cpf_desl]
                    if not reg_desl.empty:
                        r = reg_desl.iloc[0]
                        st.info(f"Colaborador: **{r['Empresa']}** | Função: **{r.get('Função','—')}** | Status: **{r.get('Status','Ativo')}**")
                    else:
                        st.warning("CPF não encontrado no sistema.")

                if st.button("🚫 INATIVAR COLABORADOR", use_container_width=True, key="btn_desl", type="primary"):
                    cpf_d = cpf_desl.strip().replace(".", "").replace("-", "")
                    if not validar_cpf_formato(cpf_d):
                        st.error("CPF inválido.")
                    else:
                        ok, msg = atualizar_status_cpf(cpf_d, "Inativo", motivo_desl)
                        st.success(msg) if ok else st.error(msg)

            # ── REATIVAÇÃO ───────────────────────────────────────────────────
            with m3:
                st.markdown("#### Reativar colaborador")
                df_inativos = df_mov[df_mov['Status'] == 'Inativo']
                if df_inativos.empty:
                    st.info("Não há colaboradores inativos.")
                else:
                    cols_reat = [c for c in ['CPF', 'Empresa', 'Função', 'Departamento', 'Data_Movimentacao', 'Motivo_Movimentacao'] if c in df_inativos.columns]
                    st.dataframe(df_inativos[cols_reat], use_container_width=True)
                    cpf_reat = st.text_input("CPF a reativar (somente números):", max_chars=11, key="cpf_reat")
                    if st.button("✅ REATIVAR COLABORADOR", use_container_width=True, key="btn_reat"):
                        cpf_r = cpf_reat.strip().replace(".", "").replace("-", "")
                        if not validar_cpf_formato(cpf_r):
                            st.error("CPF inválido.")
                        else:
                            ok, msg = atualizar_status_cpf(cpf_r, "Ativo", "Reativação")
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    # ── ABA 5: SEGURANÇA E ACESSO RH ──────────────────────────────────────────
    with t5:
        st.subheader("🔐 Segurança e Acesso RH")
        st.info("Gere ou redefina senhas de acesso para o módulo 'Gestão das Respostas (RH)'")

        df_acessos = carregar_dados(ARQUIVO_ACESSOS)

        if not df_acessos.empty:
            # Seleção de empresa
            empresas_unicas = df_acessos.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
            ).tolist()

            empresa_sel = st.selectbox("Selecione a empresa para gerar nova senha RH:", empresas_unicas, key="seg_empresa_sel")
            cnpj_cod = empresa_sel.split("CNPJ: ")[-1]
            nome_empresa = empresa_sel.split(" — CNPJ:")[0].strip()

            st.divider()

            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Empresa:** {nome_empresa}")
                st.write(f"**CNPJ:** {cnpj_cod}")

            with col2:
                if st.button("🔐 Gerar Nova Senha RH", use_container_width=True, key="btn_gerar_senha"):
                    # Gerar nova senha
                    nova_senha = gerar_senha_rh()

                    # Atualizar arquivo de acessos
                    df_acessos.loc[df_acessos['CNPJ'] == cnpj_cod, 'Senha_RH_Hash'] = hash_senha(nova_senha)
                    df_acessos.to_csv(ARQUIVO_ACESSOS, index=False, sep=';', encoding='utf-8-sig')

                    st.success("✅ Nova senha gerada com sucesso!")
                    st.divider()

                    st.subheader("🔐 Credenciais Atualizadas")
                    st.info(f"Empresa: **{nome_empresa}**\nCNPJ: **{cnpj_cod}**")
                    st.code(f"Nova Senha de Acesso RH: {nova_senha}", language=None)
                    st.warning("⚠️ **Anote esta senha com segurança!** Compartilhe-a com o RH da empresa. Esta é a única vez que ela será exibida.")

        else:
            st.info("Nenhuma empresa cadastrada no sistema.")

    # ── ABA 6: DOCUMENTAÇÃO ───────────────────────────────────────────────────
    with t6:
        st.subheader("📚 Documentação SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)")
        st.info("Acesse os guias e tutoriais disponíveis. Use o menu da barra lateral para selecionar.")

        docs = {
            "readme": ("📄 README.md", "README.pdf", "Visão Geral do Sistema — Índice, características, FAQ e início rápido"),
            "tutorial": ("👥 TUTORIAL.md", "TUTORIAL.pdf", "Tutorial Operacional — Passo a passo completo para usuários RH"),
            "instalacao": ("🚀 GUIA_INSTALACAO.md", "GUIA_INSTALACAO.pdf", "Guia de Instalação — Setup, configuração, Google Drive, deployment"),
            "tecnico": ("🔧 GUIA_TECNICO.md", "GUIA_TECNICO.pdf", "Documentação Técnica — Arquitetura, dados, fluxos, segurança"),
            "checklist": ("✅ CHECKLIST_LANCAMENTO.md", "CHECKLIST_LANCAMENTO.pdf", "Checklist de Lançamento — Validação pré-produção (60+ itens)"),
            "publicacao": ("🚀 DOCUMENTACAO_PUBLICACAO.md", "DOCUMENTACAO_PUBLICACAO.pdf", "Documentação de Publicação — Processo, recursos, arquitetura, troubleshooting"),
            "pop020": ("📱 POP020 Tutorial Telas", "POP020_TUTORIAL_TELAS.pdf", "POP 020 — Tutorial visual tela a tela com capturas de tela do sistema")
        }

        # Exibir 3 colunas com os documentos (layout em linhas de 3)
        docs_list = list(docs.items())
        for row_idx in range(0, len(docs_list), 3):
            cols = st.columns(3)
            for col_idx, (key, (titulo, pdf, descricao)) in enumerate(docs_list[row_idx:row_idx+3]):
                with cols[col_idx]:
                    st.markdown(f"### {titulo.split()[0]}")
                    st.caption(descricao)

                    # Botão para selecionar (visualizar)
                    if st.button(f"Ler {titulo.split()[0]}", use_container_width=True, key=f"sel_{key}"):
                        st.session_state.doc_view = key
                        st.rerun()

                    # Botão para baixar PDF
                    try:
                        pdf_path = caminho_doc(pdf)
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ PDF",
                                data=f.read(),
                                file_name=pdf,
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"dl_pdf_{key}"
                            )
                    except FileNotFoundError:
                        st.warning("PDF não disponível")

        st.divider()

        # Visualizar documento selecionado
        if hasattr(st.session_state, 'doc_view') and st.session_state.doc_view:
            doc_selecionado = {
                "readme": "README.md",
                "tutorial": "TUTORIAL.md",
                "instalacao": "GUIA_INSTALACAO.md",
                "tecnico": "GUIA_TECNICO.md",
                "checklist": "CHECKLIST_LANCAMENTO.md",
                "publicacao": "DOCUMENTACAO_PUBLICACAO.md"
            }

            if st.session_state.doc_view in doc_selecionado:
                arquivo = doc_selecionado[st.session_state.doc_view]
                caminho_arquivo = caminho_doc(arquivo)

                col_ler, col_fechar = st.columns([20, 1])
                with col_ler:
                    st.subheader(f"📖 Visualizando: {arquivo}")
                with col_fechar:
                    if st.button("❌", key="btn_close_doc"):
                        st.session_state.doc_view = None
                        st.rerun()

                st.divider()

                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    st.markdown(conteudo)
                except FileNotFoundError:
                    st.error(f"❌ Arquivo não encontrado: {arquivo}")
                except Exception as e:
                    st.error(f"❌ Erro ao carregar: {str(e)}")

            # ── VISUALIZADOR DE PDF — renderização página a página ────────────
            elif st.session_state.doc_view == "pop020":
                pdf_nome = "POP020_TUTORIAL_TELAS.pdf"
                pdf_path = caminho_doc(pdf_nome)

                col_ler, col_fechar = st.columns([20, 1])
                with col_ler:
                    st.subheader("📱 Visualizando: POP 020 — Tutorial Passo a Passo (Tela a Tela)")
                with col_fechar:
                    if st.button("❌", key="btn_close_doc_pop020"):
                        st.session_state.doc_view = None
                        st.rerun()

                st.divider()

                try:
                    import fitz  # PyMuPDF
                    import io
                    doc_pdf = fitz.open(pdf_path)
                    for num, pagina in enumerate(doc_pdf, start=1):
                        mat = fitz.Matrix(1.8, 1.8)  # zoom 1.8× ≈ 130 dpi
                        pix = pagina.get_pixmap(matrix=mat, alpha=False)
                        img_bytes = pix.tobytes("png")
                        st.image(img_bytes, caption=f"Página {num} de {len(doc_pdf)}", use_container_width=True)
                        if num < len(doc_pdf):
                            st.divider()
                    doc_pdf.close()
                except FileNotFoundError:
                    st.error(f"❌ Arquivo não encontrado: {pdf_nome}")
                except ImportError:
                    st.error("❌ Biblioteca pymupdf não instalada. Aguarde o redeploy ou use o botão ⬇️ PDF.")
                except Exception as e:
                    st.error(f"❌ Erro ao renderizar o PDF: {str(e)}")

# =============================================================================
# MÓDULO GESTÃO DAS RESPOSTAS (RH)
# =============================================================================
elif menu == "📊 Gestão das Respostas (RH)":
    if 'rh_logado' not in st.session_state:
        st.session_state.rh_logado = False
        st.session_state.rh_cnpj = None

    if not st.session_state.rh_logado:
        st.title("🔐 Acesso RH — Gestão de Respostas")
        st.info("Insira o CNPJ e a senha de acesso fornecida pela SSTG Admin.")

        col1, col2 = st.columns(2)
        with col1:
            cnpj_input = st.text_input("CNPJ da Empresa:", placeholder="00.000.000/0000-00")
        with col2:
            senha_input = st.text_input("Senha de Acesso RH:", type="password")

        if st.button("🔓 Acessar", use_container_width=True):
            cnpj_limpo = cnpj_input.strip().replace(".", "").replace("/", "").replace("-", "")

            if not cnpj_limpo or not senha_input:
                st.error("Preencha CNPJ e senha.")
            else:
                df_acessos = carregar_dados(ARQUIVO_ACESSOS)

                # Verificar se CNPJ existe
                empresa_data = df_acessos[df_acessos['CNPJ'] == cnpj_limpo]

                if empresa_data.empty:
                    st.error("❌ CNPJ não encontrado.")
                else:
                    # Verificar senha
                    senha_hash_stored = empresa_data.iloc[0].get('Senha_RH_Hash', '')
                    if senha_hash_stored and hash_senha(senha_input) == senha_hash_stored:
                        st.session_state.rh_logado = True
                        st.session_state.rh_cnpj = cnpj_limpo
                        st.session_state.rh_empresa = empresa_data.iloc[0]['Empresa']
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta.")
        st.stop()

    # ─────────────────────────────────────────────────────────────────────────
    # RH LOGADO - Exibir dados da empresa
    # ─────────────────────────────────────────────────────────────────────────

    st.title(f"📊 Gestão de Respostas — {st.session_state.rh_empresa}")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.rh_logado = False
        st.session_state.rh_cnpj = None
        st.session_state.rh_empresa = None
        st.rerun()

    cnpj_cod = st.session_state.rh_cnpj
    nome_res = caminho(f"respostas_CNPJ_{cnpj_cod}.csv")
    df_acessos = carregar_dados(ARQUIVO_ACESSOS)

    # ── Link do Questionário ───────────────────────────────────────────────
    with st.expander("🔗 Link do Questionário para esta empresa"):
        link_emp = f"{SHARE_URL}/?cnpj={cnpj_cod}"
        st.code(link_emp, language=None)
        st.caption(
            "Copie e envie este link para os colaboradores da empresa. "
            "Este é o link público que funciona em qualquer dispositivo, conectado à internet."
        )

    # ── Gerar Imagem de Compartilhamento ───────────────────────────────────
    with st.expander("🖼️ Gerar QRCode do Questionário para Compartilhamento"):
        st.info("Gere uma imagem com QR Code para compartilhar nas redes sociais ou enviar por email.")

        if COMPARTILHAMENTO_DISPONIVEL:
            col_gerar, col_espacador = st.columns([2, 1])

            with col_gerar:
                if st.button("🎨 Gerar Imagem com QR Code", use_container_width=True, key="btn_gerar_img_rh"):
                    try:
                        nome_empresa = empresa_sel.split(" — CNPJ:")[0].strip()

                        with st.spinner("Gerando imagem..."):
                            img_bytes = gerar_imagem_compartilhamento_simples(
                                empresa_nome=nome_empresa,
                                cnpj=cnpj_cod,
                                app_url=SHARE_URL
                            )

                        st.success("Imagem gerada com sucesso!")

                        # Exibir preview
                        st.image(img_bytes, use_column_width=True, caption=f"Imagem de compartilhamento: {nome_empresa}")

                        # Download button
                        st.download_button(
                            "⬇️ Baixar Imagem (PNG)",
                            img_bytes,
                            f"compartilhamento_{cnpj_cod}.png",
                            "image/png",
                            use_container_width=True
                        )

                        # Opções de compartilhamento
                        st.divider()
                        st.subheader("📤 Compartilhar Imagem com Colaboradores")

                        col1, col2 = st.columns(2)
                        with col1:
                            whatsapp_link = f"https://wa.me/?text=Prezado(a)%20Colaborador(a)%2C%0A%0AConvido-o%20a%20participar%20da%20avaliação%20de%20Riscos%20Psicossociais%20(SSTG-DRPS)%20através%20do%20link%3A%20{SHARE_URL}%2F%3Fcnpj%3D{cnpj_cod}%0A%0AEsta%20é%20uma%20ferramenta%20essencial%20para%20diagnóstico%20do%20ambiente%20de%20trabalho%20conforme%20NR-1.%0A%0AObrigado!"
                            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📱 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

                        with col2:
                            email_link = f"mailto:?subject=Convite - Avaliação de Riscos Psicossociais&body=Prezado(a) Colaborador(a),%0A%0AConvidamos-o a participar da avaliação de Riscos Psicossociais (SSTG-DRPS).%0A%0ALink para acesso:%0A{SHARE_URL}/?cnpj={cnpj_cod}%0A%0AEsta avaliação é fundamental para diagnóstico do ambiente de trabalho conforme NR-1.%0A%0AObrigado!"
                            st.markdown(f'<a href="{email_link}"><button style="width:100%; padding:10px; background-color:#0078D4; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📧 Enviar via Email</button></a>', unsafe_allow_html=True)

                        st.caption("💡 Dica: Use esta imagem em emails, WhatsApp, Telegram ou redes sociais para aumentar a adesão ao questionário.")

                    except Exception as e:
                        st.error(f"Erro ao gerar imagem: {e}")
        else:
            st.warning("Módulo de compartilhamento não disponível. Verifique se `qrcode` e `Pillow` estão instalados.")

    # ── Resultado das Respostas ────────────────────────────────────────────
    st.divider()
    st.subheader("📈 Resultado das Respostas")

    if os.path.exists(nome_res):
        df_res = pd.read_csv(nome_res, sep=';', dtype=str)

        total_auth = len(df_acessos[df_acessos['CNPJ'] == cnpj_cod])
        total_resp = len(df_res)
        pct        = round((total_resp / total_auth) * 100, 1) if total_auth > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Colaboradores Autorizados", total_auth)
        c2.metric("Respostas Recebidas", total_resp)
        c3.metric("Taxa de Resposta", f"{pct}%")

        st.info(f"✅ {total_resp} resposta(s) registrada(s) para esta empresa.")
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("Nenhuma resposta registrada ainda para esta empresa.")

# =============================================================================
# MÓDULO QUESTIONÁRIO PSICOSSOCIAL
# =============================================================================
else:
    if 'passo' not in st.session_state:
        st.session_state.passo = "login"

    # ── TELA DE LOGIN ─────────────────────────────────────────────────────────
    if st.session_state.passo == "login":

        # Detecta CNPJ via query param (link individualizado)
        params    = st.query_params
        cnpj_link = params.get("cnpj", "")

        st.markdown("""
            <div class="hero-sstg">
                <h1>DRPS - Diagnóstico de Riscos Psicossociais</h1>
                <p>Protocolo COPSOQ III — Diagnóstico do Ambiente de Trabalho<br>mensurado com a Escala de Avaliação (Likert)</p>
                <div class="trust-row">
                    <div class="trust-badge">
                        <div class="icon">🔒</div>
                        <div class="label">100% Confidencial</div>
                    </div>
                    <div class="trust-badge">
                        <div class="icon">👤</div>
                        <div class="label">Totalmente Anônimo</div>
                    </div>
                    <div class="trust-badge">
                        <div class="icon">⏱️</div>
                        <div class="label">~10 minutos</div>
                    </div>
                    <div class="trust-badge">
                        <div class="icon">🏆</div>
                        <div class="label">Protocolo Validado</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Exibe empresa se veio pelo link
        if cnpj_link:
            df_link = carregar_dados(ARQUIVO_ACESSOS)
            if not df_link.empty:
                emp_rows = df_link[df_link['CNPJ'] == cnpj_link]
                if not emp_rows.empty:
                    nome_emp_link = emp_rows.iloc[0]['Empresa']
                    st.info(f"🏢 Você está respondendo o questionário de: **{nome_emp_link}**")

        video_path = "video_riscos_psicossociais_FINAL (1).mp4"
        if os.path.exists(video_path):
            st.video(video_path)

        st.markdown("""
            <div class="mensagem-motivadora">
            <b>Participe da nossa pesquisa de fatores psicossociais!</b><br>
            É rápido, totalmente anônima e essencial para que possamos cuidar melhor de quem faz a empresa acontecer: você.<br><br>
            🔒 <b>100% Confidencial:</b> Suas respostas individuais são protegidas e nunca expostas.<br>
            ✨ <b>Foco na Verdade:</b> Seja sincero, sua percepção é o que importa para mudarmos o que for preciso.
            </div>
        """, unsafe_allow_html=True)

        col_cpf, col_btn = st.columns([3, 1])
        cpf_in = col_cpf.text_input(
            "Digite seu CPF (somente os 11 números, sem pontos ou traços):",
            max_chars=11,
            placeholder="00000000000"
        )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            acessar = st.button("ACESSAR ▶", use_container_width=True, type="primary")

        if acessar:
            cpf_limpo = cpf_in.strip().replace(".", "").replace("-", "")
            if not validar_cpf_formato(cpf_limpo):
                st.error("⚠️ CPF inválido. Digite apenas os 11 números.")
            else:
                df_auth = carregar_dados(ARQUIVO_ACESSOS)
                if not df_auth.empty:
                    df_auth = normalizar_status(df_auth)
                    reg = df_auth[df_auth['CPF'] == cpf_limpo]
                    if not reg.empty:
                        dados = reg.iloc[0].to_dict()
                        if dados.get('Status', 'Ativo') == 'Inativo':
                            st.error("❌ Seu acesso está inativo. Procure o RH ou a equipe SSTG.")
                        else:
                            ok_periodo, msg_periodo = periodo_valido(dados)
                            if not ok_periodo:
                                st.error(msg_periodo)
                            elif cpf_ja_respondeu(dados['CNPJ'], cpf_limpo):
                                st.warning("⚠️ Você já participou desta avaliação. Obrigado!")
                            else:
                                st.session_state.dados_sessao = dados
                                st.session_state.passo = "quest"
                                st.rerun()
                    else:
                        st.error("❌ CPF não autorizado. Procure o RH ou a equipe SSTG.")
                else:
                    st.error("Nenhuma empresa cadastrada no sistema. Contate a equipe SSTG.")

    # ── QUESTIONÁRIO (wizard: uma dimensão por vez) ───────────────────────────
    elif st.session_state.passo == "quest":
        dados_s  = st.session_state.dados_sessao
        empresa  = dados_s['Empresa']
        funcao   = dados_s.get('Função', '')
        depto    = dados_s.get('Departamento', '')
        cpf_resp = dados_s['CPF']
        caption  = f"Organização: {empresa}"
        if funcao: caption += f"  |  Função: {funcao}"
        if depto:  caption += f"  |  Departamento: {depto}"

        # Índice da dimensão atual e cache persistente de respostas
        if 'dominio_atual' not in st.session_state:
            st.session_state.dominio_atual = 0
        if 'respostas_salvas' not in st.session_state:
            st.session_state.respostas_salvas = {}

        nomes_dim  = list(DIMENSOES.keys())
        total_dim  = len(nomes_dim)
        idx        = st.session_state.dominio_atual
        nome_atual = nomes_dim[idx]
        qus_atual  = DIMENSOES[nome_atual]

        # ── Funções auxiliares de leitura/escrita de respostas ────────────────
        def salvar_bloco_atual():
            """Persiste as respostas do bloco visível antes de mudar de domínio."""
            for k in qus_atual.keys():
                chave = f"{cpf_resp}_{k}"
                if chave in st.session_state:
                    st.session_state.respostas_salvas[chave] = st.session_state[chave]

        def get_resp(chave):
            """Retorna resposta: primeiro do widget ativo, depois do cache."""
            val = st.session_state.get(chave)
            if val is not None:
                return val
            return st.session_state.respostas_salvas.get(chave)

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        st.title("📋 Avaliação Psicossocial")
        st.caption(caption)
        st.progress(idx / total_dim,
                    text=f"Bloco {idx + 1} de {total_dim} — {nome_atual}")
        st.divider()

        # ── Perguntas do bloco atual ───────────────────────────────────────────
        st.markdown(f"### {nome_atual}")
        st.caption(f"{len(qus_atual)} perguntas neste bloco")
        st.divider()

        for key, txt in qus_atual.items():
            chave = f"{cpf_resp}_{key}"
            # Restaura seleção anterior se o respondente voltar ao bloco
            val_salvo = st.session_state.respostas_salvas.get(chave)
            idx_inicial = OPCOES.index(val_salvo) if val_salvo in OPCOES else None
            st.radio(f"**{txt}**", OPCOES, horizontal=True,
                     key=chave, index=idx_inicial)

        # ── Rodapé de navegação ───────────────────────────────────────────────
        st.divider()

        # Contagem usando get_resp (inclui cache de blocos não visíveis)
        nao_resp_bloco = [k for k in qus_atual.keys()
                          if get_resp(f"{cpf_resp}_{k}") is None]

        total_qst  = sum(len(v) for v in DIMENSOES.values())
        resp_geral = sum(
            1 for nd, qd in DIMENSOES.items()
            for k in qd.keys()
            if get_resp(f"{cpf_resp}_{k}") is not None
        )
        st.progress(resp_geral / total_qst,
                    text=f"Progresso geral: {resp_geral} de {total_qst} perguntas respondidas")

        col_ant, col_prox = st.columns(2)

        with col_ant:
            if idx > 0:
                if st.button("◀ Demanda Anterior", use_container_width=True):
                    salvar_bloco_atual()
                    st.session_state.dominio_atual -= 1
                    st.rerun()

        with col_prox:
            if idx < total_dim - 1:
                if nao_resp_bloco:
                    st.warning(
                        f"⚠️ Responda as {len(nao_resp_bloco)} pergunta(s) acima para avançar.")
                else:
                    if st.button("Próxima Demanda ▶", use_container_width=True,
                                 type="primary"):
                        salvar_bloco_atual()
                        st.session_state.dominio_atual += 1
                        st.rerun()
            else:
                # Último bloco — verifica pendências em todos os blocos
                nao_resp_total = [
                    k for nd, qd in DIMENSOES.items()
                    for k in qd.keys()
                    if get_resp(f"{cpf_resp}_{k}") is None
                ]
                if nao_resp_total:
                    st.warning(
                        f"⚠️ Ainda há {len(nao_resp_total)} pergunta(s) sem resposta. "
                        "Use ◀ para revisar os blocos anteriores.")
                if st.button("✅ FINALIZAR E ENVIAR AVALIAÇÃO",
                             use_container_width=True, type="primary",
                             disabled=bool(nao_resp_total)):
                    salvar_bloco_atual()
                    # Monta dicionário final lendo do cache persistente
                    respostas = {
                        k: get_resp(f"{cpf_resp}_{k}")
                        for nd, qd in DIMENSOES.items()
                        for k in qd.keys()
                    }
                    dados_salvar = {
                        "Data":         datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Função":       funcao,
                        "Departamento": depto,
                        "CPF_Hash":     hash_cpf(cpf_resp)
                    }
                    for nome_dim, qus_dim in DIMENSOES.items():
                        nome_col = ("Media_" + nome_dim.split(" ", 1)[1]
                                    .replace("/", "_").replace(" ", "_"))
                        valores  = [DEPARA[respostas[k]] for k in qus_dim.keys()]
                        dados_salvar[nome_col] = round(sum(valores) / len(valores), 2)

                    dados_salvar["Media_Geral"] = round(
                        sum(DEPARA[v] for v in respostas.values()) / len(respostas), 2
                    )
                    nome_res = caminho(f"respostas_CNPJ_{dados_s['CNPJ']}.csv")
                    pd.DataFrame([dados_salvar]).to_csv(
                        nome_res, mode='a', index=False, sep=';',
                        header=not os.path.exists(nome_res), encoding='utf-8-sig'
                    )
                    # Limpa estado do wizard
                    st.session_state.dominio_atual = 0
                    st.session_state.respostas_salvas = {}
                    st.session_state.passo = "fim"
                    st.rerun()

    # ── TELA FINAL ────────────────────────────────────────────────────────────
    elif st.session_state.passo == "fim":
        st.title("✅ Avaliação Concluída!")
        st.balloons()
        st.success("Sua avaliação foi enviada com sucesso!")
        st.markdown("""
            <div class="mensagem-motivadora">
            <b>Muito obrigado pela sua participação!</b><br><br>
            Suas respostas contribuirão para a construção de um ambiente de trabalho mais saudável e seguro.
            Os dados coletados serão analisados de forma <b>agregada e completamente anônima</b> pela equipe SSTG.
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Voltar ao Início", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
