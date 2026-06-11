import streamlit as st
import pandas as pd
import os
import hashlib
import re
import secrets
import string
import base64
from datetime import datetime, date
import db


try:
    from gerar_laudo import gerar_laudo_pdf
    LAUDO_DISPONIVEL = True
except ImportError:
    LAUDO_DISPONIVEL = False

try:
    from gerar_laudo_aep import gerar_laudo_aep_pdf
    LAUDO_AEP_DISPONIVEL = True
except ImportError:
    LAUDO_AEP_DISPONIVEL = False

# ── Geração de imagem QR Code embutida (sem módulo externo) ──────────────────
import io as _io
import qrcode as _qrcode
from PIL import Image as _Image, ImageDraw as _ImageDraw, ImageFont as _ImageFont

def _achar_fonte():
    """Retorna o primeiro arquivo TTF encontrado no sistema."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidatos = [
        os.path.join(windir, "Fonts", "seguiemj.ttf"),   # Segoe UI Emoji — Unicode completo
        os.path.join(windir, "Fonts", "segoeui.ttf"),    # Segoe UI
        os.path.join(windir, "Fonts", "segoeuil.ttf"),   # Segoe UI Light
        os.path.join(windir, "Fonts", "arialuni.ttf"),   # Arial Unicode MS
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
    draw.text((MARGEM, 16),  "SSTG - DRPS AEP  Diagn" + chr(243) + "stico de Riscos Psicossociais e Ergon" + chr(244) + "micos (NR-1 / NR-17)", fill=CZ_CLARO, font=f_hdr_sm)
    draw.text((MARGEM, 50),  "SSTG - DRPS AEP  Diagn" + chr(243) + "stico de Riscos Psicossociais",        fill=BRANCO,   font=f_hdr_lg)

    # Empresa
    draw.text((MARGEM, y_label), "Empresa:", fill=CZ_MED, font=f_label)
    y_cur = y_emp
    for linha in linhas:
        draw.text((MARGEM, y_cur), linha, fill=COR_VERDE, font=f_emp)
        y_cur += H_LINHA

    # QR Code
    sep  = "&" if "?" in app_url else "?"
    link = f"{app_url}{sep}cnpj={cnpj}"
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

# ─── DIRETÓRIO E CONFIGURAÇÕES ──────────────────────────────────────────────
DOC_DIR   = os.path.dirname(os.path.abspath(__file__))
APP_URL   = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"
SHARE_URL = "https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app"
EBOOK_URL = "https://valter-contador.github.io/sstg-e-social/ebook_psicossocial.html"
EBOOK_AEP_URL = "https://valter-contador.github.io/sstg-e-social/ebook_aep.html"
QUEST_PSICOSSOCIAL_URL = "https://valter-contador.github.io/sstg-e-social/questionario_psicossocial.html"
QUEST_AEP_URL = "https://valter-contador.github.io/sstg-e-social/questionario_aep.html"
SENHA_ADMIN = "Valter@sstg230914"

def caminho_doc(nome_arquivo: str) -> str:
    return os.path.join(DOC_DIR, nome_arquivo)

def gerar_backup_zip() -> bytes:
    """Exporta todos os dados do Supabase como CSVs em ZIP."""
    return db.exportar_backup_zip()

def validar_cpf_formato(cpf: str) -> bool:
    return cpf.isdigit() and len(cpf) == 11

def hash_cpf(cpf: str) -> str:
    return hashlib.sha256(cpf.encode()).hexdigest()

def gerar_senha_rh() -> str:
    """Gera uma senha segura de 8 caracteres para acesso RH"""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

def hash_senha(senha: str) -> str:
    """Faz hash da senha para armazenamento seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

# ─── USUÁRIOS OPERACIONAIS ───────────────────────────────────────────────────

def carregar_usuarios() -> pd.DataFrame:
    return db.carregar_usuarios()

def verificar_usuario_operacional(usuario: str, senha: str) -> bool:
    df = carregar_usuarios()
    if df.empty:
        return False
    mask = (df['Usuario'] == usuario) & (df['Status'] == 'Ativo')
    if not mask.any():
        return False
    return df.loc[mask, 'Senha_Hash'].iloc[0] == hash_senha(senha)

def criar_usuario_operacional(usuario: str, nome: str, senha: str) -> tuple:
    df = carregar_usuarios()
    if not df.empty and usuario in df['Usuario'].values:
        return False, f"Usuário '{usuario}' já existe."
    db.salvar_usuario({
        "Usuario":      usuario.strip().lower(),
        "Nome":         nome.strip(),
        "Senha_Hash":   hash_senha(senha),
        "Status":       "Ativo",
        "Data_Criacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    return True, f"Usuário '{usuario}' criado com sucesso."

def desativar_usuario_operacional(usuario: str) -> tuple:
    df = carregar_usuarios()
    if df.empty or usuario not in df['Usuario'].values:
        return False, f"Usuário '{usuario}' não encontrado."
    db.atualizar_usuario_campos(usuario, {"Status": "Inativo"})
    return True, f"Usuário '{usuario}' desativado."

def reativar_usuario_operacional(usuario: str) -> tuple:
    df = carregar_usuarios()
    if df.empty or usuario not in df['Usuario'].values:
        return False, f"Usuário '{usuario}' não encontrado."
    db.atualizar_usuario_campos(usuario, {"Status": "Ativo"})
    return True, f"Usuário '{usuario}' reativado."

def get_senha_admin_hash() -> str:
    h = db.get_config("senha_admin_hash")
    return h if h else hash_senha(SENHA_ADMIN)

def set_senha_admin(nova_senha: str):
    db.set_config("senha_admin_hash", hash_senha(nova_senha))

def redefinir_senha_operacional(usuario: str, nova_senha: str) -> tuple:
    df = carregar_usuarios()
    if df.empty or usuario not in df['Usuario'].values:
        return False, f"Usuário '{usuario}' não encontrado."
    db.atualizar_usuario_campos(usuario, {"Senha_Hash": hash_senha(nova_senha)})
    return True, f"Senha do usuário '{usuario}' redefinida com sucesso."

def cpf_ja_respondeu(cnpj: str, cpf: str) -> bool:
    return db.cpf_respondeu(cnpj, hash_cpf(cpf))

def cpf_ja_respondeu_aep(cnpj: str, cpf: str) -> bool:
    return db.cpf_respondeu_aep(cnpj, hash_cpf(cpf))

def normalizar_status(df: pd.DataFrame) -> pd.DataFrame:
    if 'Status' not in df.columns:
        df['Status'] = 'Ativo'
    else:
        df['Status'] = df['Status'].fillna('Ativo')
    return df

def salvar_cadastro_completo(dados_emp: dict, colaboradores: list):
    df_existente = db.carregar_acessos()
    novos, duplicados, invalidos = [], [], []
    for colab in colaboradores:
        cpf_limpo = str(colab.get('CPF', '')).strip().replace(".", "").replace("-", "")
        if not cpf_limpo:
            continue
        if not validar_cpf_formato(cpf_limpo):
            invalidos.append(cpf_limpo)
            continue
        cnpj_atual = dados_emp['CNPJ']
        ja_nessa_empresa = (
            not df_existente.empty
            and len(df_existente[
                (df_existente['CPF'] == cpf_limpo) &
                (df_existente['CNPJ'] == cnpj_atual)
            ]) > 0
        )
        if ja_nessa_empresa:
            duplicados.append(cpf_limpo)
            continue
        novos.append({
            "CPF":                  cpf_limpo,
            "Empresa":              dados_emp['Razão Social'],
            "CNPJ":                 dados_emp['CNPJ'],
            "Funcao":               colab.get('Função', colab.get('Funcao', '')),
            "Departamento":         colab.get('Departamento', ''),
            "Data_Acesso_Liberado": datetime.now().strftime("%d/%m/%Y"),
            "Data_Inicio_Periodo":  dados_emp.get('Data_Inicio', ''),
            "Data_Fim_Periodo":     dados_emp.get('Data_Fim', ''),
            "Status":               "Ativo",
            "Data_Movimentacao":    "",
            "Motivo_Movimentacao":  "",
            "CNAE":                 dados_emp.get('CNAE', ''),
            "Grau_Risco":           dados_emp.get('Grau_Risco', ''),
        })
    if novos:
        db.salvar_acessos_em_lote(novos)
    return novos, duplicados, invalidos

def atualizar_status_cpf(cpf: str, novo_status: str, motivo: str = "") -> tuple:
    df = db.carregar_acessos()
    if df.empty:
        return False, "Banco de dados vazio."
    df = normalizar_status(df)
    mask = df['CPF'] == cpf
    if not mask.any():
        return False, f"CPF {cpf} não encontrado no sistema."
    empresa = df.loc[mask, 'Empresa'].iloc[0]
    cnpj    = df.loc[mask, 'CNPJ'].iloc[0]
    db.atualizar_acesso_campos(cpf, cnpj, {
        'Status':              novo_status,
        'Data_Movimentacao':   datetime.now().strftime("%d/%m/%Y"),
        'Motivo_Movimentacao': motivo,
    })
    return True, f"CPF {cpf} ({empresa}) atualizado para **{novo_status}**."

def atualizar_periodo_empresa(cnpj: str, data_inicio: str, data_fim: str) -> tuple:
    df = db.carregar_acessos()
    if df.empty:
        return False, "Banco de dados vazio."
    if cnpj not in df['CNPJ'].values:
        return False, f"CNPJ {cnpj} não encontrado."
    db.atualizar_acessos_por_cnpj(cnpj, {
        'Data_Inicio_Periodo': data_inicio,
        'Data_Fim_Periodo':    data_fim,
    })
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
        "q11": "02. Estão claras as minhas tarefas e responsabilidades.",
        "q13": "03. Os objetivos e metas do meu setor são claros para mim.",
    },
    "🎮 Controle": {
        "q15": "04. Tenho liberdade de escolha de como fazer meu trabalho.",
        "q19": "05. Tenho liberdade de escolha para decidir o que fazer no meu trabalho.",
        "q25": "06. Minhas sugestões são consideradas sobre como fazer meu trabalho.",
    },
    "⚖️ Demandas": {
        "q9":  "07. Devo trabalhar muito intensamente.",
        "q12": "08. Deixo tarefas sem fazer por excesso de carga.",
        "q20": "09. Tenho que fazer meu trabalho com muita rapidez.",
    },
    "⚠️ Relacionamentos": {
        "q5":  "10. Falam ou se comportam comigo de forma dura.",
        "q21": "11. Sinto que sou perseguido no trabalho.",
        "q14": "12. Existem conflitos entre os colegas.",
    },
    "🤝 Apoio dos Colegas": {
        "q7":  "13. Posso contar com ajuda dos colegas.",
        "q27": "14. Meus colegas demonstram o respeito que mereço.",
        "q31": "15. Os colegas estão disponíveis para escutar meus problemas.",
    },
    "👔 Apoio da Chefia": {
        "q23": "16. Posso confiar no meu chefe.",
        "q29": "17. Quando algo me perturba posso falar com meu chefe.",
        "q35": "18. Meu chefe me incentiva no trabalho.",
    },
    "📢 Comunicação e Mudanças": {
        "q26": "19. Tenho oportunidades para pedir explicações sobre mudanças.",
        "q28": "20. As pessoas são consultadas sobre mudanças no trabalho.",
        "q32": "21. Quando há mudanças, faço o trabalho com o mesmo carinho.",
    },
    "🚨 Comportamentos Ofensivos": {
        "q36": "22. Fui submetido(a) a ameaças, agressões verbais graves ou violência física no meu ambiente de trabalho.",
        "q37": "23. Fui exposto(a) a situações de assédio sexual ou condutas de natureza sexual não desejadas no trabalho.",
    }
}

DIMS_INVERTIDAS = {"Demandas", "Relacionamentos", "Comportamentos_Ofensivos"}
# versão lowercase (usada para comparar com nomes vindos do banco)
_DIMS_INV_LOWER = {d.lower() for d in DIMS_INVERTIDAS}

# ── Metadados de exibição por dimensão ───────────────────────────────────────
import unicodedata as _uc

# Cor específica por dimensão (chave = slug normalizado sem acento)
_CORES_DIMS_NAMED = {
    "cargo":                    "#5A9F62",   # verde
    "controle":                 "#282C5B",   # azul escuro
    "demandas":                 "#DC3B24",   # vermelho
    "relacionamentos":          "#F4A236",   # laranja
    "apoio_dos_colegas":        "#4A90D9",   # azul
    "apoio_da_chefia":          "#9B59B6",   # roxo
    "comunicacao_e_mudancas":   "#1ABC9C",   # verde-água
    "comportamentos_ofensivos": "#C0392B",   # vermelho escuro (risco/alerta)
}

# _COL_INFO: "media_cargo" → {label, invertida, cor}
_COL_INFO: dict = {}
for _nd in DIMENSOES:
    _suffix_nd = _nd.split(" ", 1)[1]
    _chave_nd  = _suffix_nd.replace(" ", "_").lower()
    _nfkd_nd   = "".join(
        c for c in _uc.normalize("NFKD", _chave_nd) if not _uc.combining(c)
    )
    _COL_INFO["media_" + _nfkd_nd] = {
        "label":     _suffix_nd,
        "invertida": _chave_nd in _DIMS_INV_LOWER,
        "cor":       _CORES_DIMS_NAMED.get(_nfkd_nd, "#888888"),
    }


# ─── QUESTÕES — AVALIAÇÃO ERGONÔMICA PRELIMINAR (AEP / NR-17) ────────────────
AEP_OPCOES = ["Sim", "Não", "Parcial", "N/A"]

# Perguntas em que a resposta "Sim" indica condição ADEQUADA (sem risco) —
# para estas, "Não" indica risco. As demais são "diretas" ("Sim" = risco).
AEP_INVERTIDAS = {6, 7, 8, 9, 10, 11, 12, 14, 17}

AEP_SECOES = {
    "A. Postura e Movimentos": {
        "q1": {
            "texto": "Você fica muito tempo na mesma posição durante o trabalho (sentado ou em pé)? "
                     "Exemplo: mais de 1 hora seguida sem poder mudar de posição.",
            "severidade": 2,
            "risco": "Fadiga muscular estática / Dor lombar / Varizes",
        },
        "q2": {
            "texto": "Você precisa dobrar ou girar o corpo, o pescoço ou a cabeça para realizar a tarefa? "
                     "Exemplo: torcer o tronco para pegar materiais ao lado, olhar constantemente para baixo ou de lado.",
            "severidade": 2,
            "risco": "Sobrecarga cervical e lombar / LER-DORT",
        },
        "q3": {
            "texto": "Você levanta, carrega ou descarrega peso manualmente durante o trabalho? "
                     "Exemplo: caixas, sacos, peças, equipamentos, documentos empilhados.",
            "severidade": 3,
            "risco": "Lombalgias agudas e crônicas / Hérnia de disco",
        },
        "q4": {
            "texto": "Você faz os mesmos movimentos repetidas vezes com os braços, mãos ou pernas? "
                     "Exemplo: digitar, embalar, apertar, cortar, girar sempre com o mesmo gesto.",
            "severidade": 3,
            "risco": "LER/DORT / Tendinite / Síndrome do túnel do carpo",
        },
        "q5": {
            "texto": "Você precisa fazer força intensa para realizar alguma parte do trabalho? "
                     "Exemplo: apertar, puxar, empurrar ou sustentar algo pesado ou com resistência.",
            "severidade": 3,
            "risco": "Fadiga muscular / Lesão tendínea / Lombalgias",
        },
    },
    "B. Mobiliário e Equipamentos": {
        "q6": {
            "texto": "A mesa ou bancada onde você trabalha tem altura confortável para o seu tamanho e tipo de tarefa? "
                     "Você não precisa se curvar nem levantar demais os braços para trabalhar.",
            "severidade": 2,
            "risco": "Postura compensatória / Sobrecarga em ombros e coluna",
        },
        "q7": {
            "texto": "A cadeira que você usa tem regulagem de altura e encosto adequados à sua estatura e à tarefa? "
                     "Você consegue apoiar os pés no chão e manter as costas apoiadas.",
            "severidade": 2,
            "risco": "Compressão de raiz nervosa / Dor lombar / Fadiga postural",
        },
        "q8": {
            "texto": "O computador, teclado e mouse (quando usados) estão em uma posição confortável para você? "
                     "A tela está na altura dos olhos e o teclado/mouse permitem que os cotovelos fiquem próximos ao corpo.",
            "severidade": 2,
            "risco": "Síndrome cervicobraquial / Lesão por digitação / Fadiga visual",
        },
        "q9": {
            "texto": "As ferramentas e equipamentos que você usa se adaptam bem ao tamanho da sua mão e ao jeito de trabalhar? "
                     "Você não precisa forçar o punho ou apertar forte para segurar.",
            "severidade": 2,
            "risco": "Sobrecarga de punho e dedos / Síndrome de De Quervain",
        },
    },
    "C. Condições Ambientais": {
        "q10": {
            "texto": "A iluminação do seu local de trabalho é adequada, sem reflexos nem sombras que atrapalhem a visão? "
                     "Você consegue enxergar bem o que faz sem esforçar os olhos ou usar luz extra.",
            "severidade": 1,
            "risco": "Fadiga visual / Cefaleia / Postura compensatória",
        },
        "q11": {
            "texto": "O nível de barulho no trabalho é suportável e não te atrapalha? "
                     "Você consegue se concentrar, conversar e trabalhar sem incômodo frequente.",
            "severidade": 2,
            "risco": "Estresse / Dificuldade de concentração / Perda auditiva",
        },
        "q12": {
            "texto": "A temperatura e a ventilação do local são confortáveis durante a jornada? "
                     "Você não sente muito calor, muito frio nem abafamento enquanto trabalha.",
            "severidade": 1,
            "risco": "Fadiga por calor / Desconforto / Queda de rendimento",
        },
    },
    "D. Organização do Trabalho": {
        "q13": {
            "texto": "O ritmo do seu trabalho é controlado por uma máquina, esteira ou meta que não permite pausas? "
                     "Você tem liberdade de trabalhar no próprio ritmo ou é a máquina/sistema que define o tempo?",
            "severidade": 2,
            "risco": "Estresse psicossocial / Fadiga acelerada / Erros operacionais",
        },
        "q14": {
            "texto": "Você tem pausas suficientes durante o dia para descansar e se recuperar do cansaço? "
                     "Exemplo: intervalos para sentar, esticar o corpo, relaxar os olhos ou tomar água.",
            "severidade": 3,
            "risco": "Fadiga acumulada / LER-DORT / Diminuição da atenção",
        },
        "q15": {
            "texto": "Você sente pressão excessiva por metas ou prazos que dificultam trabalhar com tranquilidade? "
                     "Cobranças que geram estresse, medo de errar ou sensação de que o tempo nunca é suficiente.",
            "severidade": 3,
            "risco": "Síndrome de Burnout / Ansiedade / Erro humano",
        },
        "q16": {
            "texto": "Sua tarefa exige atenção e concentração intensa e contínua por longos períodos? "
                     "Você precisa ficar 100% focado por muito tempo sem poder relaxar a atenção.",
            "severidade": 2,
            "risco": "Fadiga cognitiva / Cefaleia / Erros críticos",
        },
        "q17": {
            "texto": "Você recebeu treinamento adequado para realizar a sua função com segurança? "
                     "Alguém te ensinou como fazer o trabalho corretamente, inclusive os cuidados com a saúde?",
            "severidade": 3,
            "risco": "Risco de acidente / Posturas incorretas / Baixa eficiência",
        },
    },
}

# Severidades pré-preenchidas {"q1": 2, "q2": 2, ...} — usadas como default ao gravar a resposta
AEP_SEVERIDADES_DEFAULT = {
    qid: dados["severidade"]
    for secao in AEP_SECOES.values()
    for qid, dados in secao.items()
}

# Severidades pré-calibradas pelo responsável técnico em função do grau de risco da
# atividade econômica da organização (NR-4, campo Grau_Risco do cadastro da empresa):
# cada pergunta tem (severidade para empresas de GR 1-2, severidade para empresas de GR 3-4)
AEP_SEVERIDADES_RT = {
    "q1":  (2, 2), "q2":  (2, 3), "q3":  (3, 4), "q4":  (3, 3), "q5":  (3, 4),
    "q6":  (2, 2), "q7":  (2, 2), "q8":  (2, 2), "q9":  (2, 3),
    "q10": (1, 1), "q11": (2, 3), "q12": (1, 2),
    "q13": (2, 3), "q14": (3, 3), "q15": (3, 3), "q16": (2, 3), "q17": (3, 4),
}

# Setores com menos respondentes que este mínimo são agrupados em um único conjunto
# no cálculo da média por setor (representatividade estatística e anonimato)
MIN_RESPONDENTES_SETOR = 3


def _severidades_por_grau_empresa(grau_risco) -> tuple:
    """Retorna ({qid: severidade}, faixa) conforme o grau de risco da atividade econômica
    (NR-4) informado no cadastro da empresa. Sem grau cadastrado, usa a coluna GR 1-2."""
    try:
        col = 1 if int(str(grau_risco).strip()) >= 3 else 0
    except (ValueError, TypeError):
        col = 0
    faixa = "3-4" if col == 1 else "1-2"
    return {qid: vals[col] for qid, vals in AEP_SEVERIDADES_RT.items()}, faixa

# Cores por seção (para gráficos)
AEP_CORES_SECOES = {
    "A. Postura e Movimentos":      "#DC3B24",
    "B. Mobiliário e Equipamentos": "#F4A236",
    "C. Condições Ambientais":      "#4A90D9",
    "D. Organização do Trabalho":   "#9B59B6",
}


def _classificar_gr(gr: float, pct_risco: float = 0.0) -> tuple:
    """Retorna (classificação, cor) para um Grau de Risco (Severidade x Probabilidade contínua).

    A classificação "Crítico" é reservada exclusivamente para os casos em que a média de
    respostas indicadoras de risco (entre os setores avaliados) ultrapassar 98%, dada a
    quase unanimidade da percepção de risco pelos trabalhadores — independentemente do GR
    calculado. Faixas do GR contínuo (1,0 a 16,0): Baixo <= 4,0 | Médio > 4,0 a 8,0 |
    Alto > 8,0. Regra de piso: % de risco >= 70% nunca classifica abaixo de "Médio"."""
    if pct_risco > 0.98:
        return "Crítico", "#C0392B"
    if gr > 8:
        return "Alto", "#F4A236"
    if gr > 4 or pct_risco >= 0.70:
        return "Médio", "#F1C40F"
    return "Baixo", "#5A9F62"


def _calcular_inventario_aep(df_aep: pd.DataFrame, severidades: dict) -> list:
    """Consolida as respostas AEP em um inventário de riscos: para cada pergunta calcula
    o percentual de respostas indicadoras de risco ("Parcial" pondera 0,5), a Probabilidade
    contínua decorrente (Prob = 1 + 3 x %risco, de 1,00 a 4,00), a Severidade pré-calibrada
    pelo responsável técnico e o Grau de Risco (GR = Severidade x Probabilidade, 1,0 a 16,0).

    Quando há informação de setor/departamento, o percentual de risco de cada pergunta é
    calculado pela MÉDIA dos percentuais de cada setor (não pelo total bruto de respostas),
    de modo que setores menores tenham o mesmo peso que setores maiores na faixa de risco.
    Setores com menos de MIN_RESPONDENTES_SETOR respondentes são agrupados em um único
    conjunto no cálculo, preservando representatividade estatística e anonimato."""
    inventario = []
    numero = 0

    col_setor = "departamento" if "departamento" in df_aep.columns else None
    grupos = []  # DataFrames que atuam como "setores" na média (pequenos são agregados)
    if col_setor:
        setores = sorted({
            s for s in df_aep[col_setor].astype(str).str.strip().tolist()
            if s and s.lower() != "nan"
        })
        pequenos = []
        for setor in setores:
            df_setor = df_aep[df_aep[col_setor].astype(str).str.strip() == setor]
            if len(df_setor) >= MIN_RESPONDENTES_SETOR:
                grupos.append(df_setor)
            else:
                pequenos.append(df_setor)
        if pequenos:
            grupos.append(pd.concat(pequenos))

    def _pct_risco_subset(df_sub, col, resposta_risco):
        respostas = df_sub[col].dropna()
        respostas = respostas[respostas.str.upper() != "N/A"]
        total = len(respostas)
        if total == 0:
            return None
        n_risco   = (respostas == resposta_risco).sum()
        n_parcial = (respostas == "Parcial").sum()
        return (n_risco + 0.5 * n_parcial) / total

    for secao, perguntas in AEP_SECOES.items():
        for qid, dados in perguntas.items():
            numero += 1
            col = qid
            invertida = int(qid[1:]) in AEP_INVERTIDAS
            if col not in df_aep.columns:
                continue
            resposta_risco = "Não" if invertida else "Sim"

            if grupos:
                pcts = []
                for df_grupo in grupos:
                    p = _pct_risco_subset(df_grupo, col, resposta_risco)
                    if p is not None:
                        pcts.append(p)
                if not pcts:
                    continue
                pct_risco = sum(pcts) / len(pcts)
            else:
                pct_risco = _pct_risco_subset(df_aep, col, resposta_risco)
                if pct_risco is None:
                    continue

            prob = round(1 + 3 * pct_risco, 2)
            sev  = int(severidades.get(qid, dados["severidade"]))
            gr   = round(sev * prob, 1)
            classif, cor = _classificar_gr(gr, pct_risco)

            inventario.append({
                "Nº":           numero,
                "Seção":        secao,
                "Pergunta":     dados["texto"],
                "Risco Identificado": dados["risco"],
                "% Risco":      round(pct_risco * 100, 1),
                "Severidade":   sev,
                "Probabilidade": prob,
                "GR":           gr,
                "Classificação": classif,
                "Plano?":       "SIM" if classif in ("Alto", "Crítico") else "NÃO",
                "Cor":          cor,
            })
    return inventario


def _chart_info(col_nome: str) -> dict:
    """Retorna metadados de exibição para uma coluna Media_*."""
    return _COL_INFO.get(col_nome.lower(), {
        "label":     col_nome.replace("Media_", "").replace("_", " ").title(),
        "invertida": False,
        "cor":       "#888888",
    })

def _calcular_medias_dimensao(df_res, cols_media):
    """Calcula médias por dimensão (já com inversão aplicada) e seus metadados de exibição."""
    df_num = df_res[cols_media].apply(pd.to_numeric, errors='coerce')
    medias = df_num.mean()
    infos  = [_chart_info(c) for c in medias.index]
    labels = [inf["label"] for inf in infos]
    values = [
        round(4.0 - v, 2) if inf["invertida"] else round(v, 2)
        for inf, v in zip(infos, medias.values)
    ]
    cores  = [inf["cor"] for inf in infos]
    return labels, values, cores

def _renderizar_grafico_medias(labels, values, cores, key):
    """Renderiza o gráfico de barras de médias por dimensão."""
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(
            x=labels,
            y=values,
            marker_color=cores,
            text=[f"{v:.2f}" for v in values],
            textposition="outside",
            width=0.6,
        ))
        fig.update_layout(
            yaxis=dict(
                title="Média (0–4)  ·  ↑ mais favorável",
                range=[0, 4.6],
                tickvals=[0, 1, 2, 3, 4],
                gridcolor="#EEEEEE",
            ),
            xaxis=dict(title="", tickangle=-20),
            plot_bgcolor="white",
            margin=dict(t=30, b=80, l=50, r=30),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, key=key)
    except ImportError:
        cols_d = st.columns(len(labels))
        for i, (label, val) in enumerate(zip(labels, values)):
            cols_d[i].metric(label, f"{val:.2f}")

def _bloco_grafico_dimensoes(df_res, cols_media, key_prefix):
    """Exibe o gráfico de médias por dimensão (geral) e, opcionalmente, estratificado por Setor."""
    st.subheader("📈 Média por Dimensão Geral (Escala Likert 0 a 4)")
    st.caption("⚠️ Demandas, Relacionamentos e Comportamentos Ofensivos exibem valor invertido (4 − média) — barra mais alta = condição mais favorável.")
    labels, values, cores = _calcular_medias_dimensao(df_res, cols_media)
    _renderizar_grafico_medias(labels, values, cores, key=f"{key_prefix}_geral")

    if 'Departamento' in df_res.columns:
        setores = sorted(
            s for s in df_res['Departamento'].dropna().astype(str).str.strip().unique() if s
        )
        if setores:
            setor_sel = st.selectbox(
                "📂 Avaliação estratificada por Setor (opcional)",
                ["Todos os setores"] + setores,
                key=f"{key_prefix}_setor_sel"
            )
            if setor_sel != "Todos os setores":
                df_setor = df_res[df_res['Departamento'].astype(str).str.strip() == setor_sel]
                if not df_setor.empty:
                    st.markdown(f"**Médias por Dimensão — Setor: {setor_sel}** ({len(df_setor)} resposta(s))")
                    labels_s, values_s, cores_s = _calcular_medias_dimensao(df_setor, cols_media)
                    _renderizar_grafico_medias(labels_s, values_s, cores_s, key=f"{key_prefix}_setor_{setor_sel}")
                else:
                    st.info("Nenhuma resposta encontrada para este setor.")


def _renderizar_grafico_secoes_aep(inventario, key):
    """Gráfico de barras com o % médio de respostas de risco por seção (A-D)."""
    secoes = list(AEP_SECOES.keys())
    valores, cores = [], []
    for secao in secoes:
        itens = [it["% Risco"] for it in inventario if it["Seção"] == secao]
        valores.append(round(sum(itens) / len(itens), 1) if itens else 0.0)
        cores.append(AEP_CORES_SECOES.get(secao, "#888888"))
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(
            x=secoes, y=valores, marker_color=cores,
            text=[f"{v:.1f}%" for v in valores],
            textposition="outside", width=0.6,
        ))
        fig.update_layout(
            yaxis=dict(title="% de respostas indicando risco", range=[0, 100], gridcolor="#EEEEEE"),
            xaxis=dict(title="", tickangle=-10),
            plot_bgcolor="white",
            margin=dict(t=30, b=80, l=50, r=30),
            height=380, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, key=key)
    except ImportError:
        cols_d = st.columns(len(secoes))
        for i, (label, val) in enumerate(zip(secoes, valores)):
            cols_d[i].metric(label, f"{val:.1f}%")


def _bloco_resultados_aep(cnpj_cod, total_auth, key_prefix, empresa_nome, mostrar_laudo=False):
    """Exibe os resultados consolidados da Avaliação Ergonômica (AEP/NR-17): adesão,
    gráfico por seção, inventário de riscos com severidades pré-calibradas pelo
    responsável técnico (conforme o grau de risco da empresa) e, opcionalmente,
    geração do Laudo AEP em PDF."""
    df_aep = db.carregar_respostas_aep(cnpj_cod)
    if df_aep.empty:
        st.info("Nenhuma resposta da Avaliação Ergonômica (AEP) registrada ainda para esta empresa.")
        return

    total_resp_aep = len(df_aep)
    pct_aep = round((total_resp_aep / total_auth) * 100, 1) if total_auth > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("CPFs Autorizados",        total_auth)
    c2.metric("Respostas AEP Recebidas", total_resp_aep)
    c3.metric("Taxa de Adesão (AEP)",    f"{pct_aep}%")

    # Severidades pré-calibradas conforme o grau de risco da atividade (cadastro da empresa)
    df_acessos_aep = db.carregar_acessos()
    grau_risco_emp = ""
    if not df_acessos_aep.empty:
        _emp_aep = df_acessos_aep[df_acessos_aep['CNPJ'] == cnpj_cod]
        if not _emp_aep.empty:
            grau_risco_emp = str(_emp_aep.iloc[0].get('Grau_Risco', '')).strip()
    severidades, faixa_sev = _severidades_por_grau_empresa(grau_risco_emp)

    inventario = _calcular_inventario_aep(df_aep, severidades)

    st.subheader("📊 Percentual de Respostas de Risco por Seção")
    _renderizar_grafico_secoes_aep(inventario, key=f"{key_prefix}_aep_secoes")

    st.divider()
    st.subheader("📋 Inventário de Riscos Ergonômicos")
    st.caption(f"Grau de risco da empresa (NR-4): **{grau_risco_emp or '—'}** — severidades pré-calibradas "
               f"pelo responsável técnico para empresas de grau de risco {faixa_sev} "
               "(1=Leve, 2=Moderada, 3=Grave, 4=Crítica). "
               "Probabilidade contínua = 1 + 3 × %risco. GR = Severidade × Probabilidade. "
               "Plano? = SIM (classificação Alto ou Crítico) indica destaque no Plano de Ação do laudo.")

    df_inv = pd.DataFrame(inventario)
    if not df_inv.empty:
        st.dataframe(
            df_inv[["Nº", "Seção", "Risco Identificado", "% Risco", "Severidade", "Probabilidade", "GR", "Classificação", "Plano?"]],
            hide_index=True, use_container_width=True,
        )

    st.divider()
    colunas_exibir_aep = [c for c in df_aep.columns if c not in ("cpf_hash", "severidades", "id")]
    csv_aep = df_aep[colunas_exibir_aep].to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button("⬇️ Baixar respostas AEP (.csv)", csv_aep, f"respostas_aep_{cnpj_cod}.csv", "text/csv",
                        key=f"{key_prefix}_aep_csv")

    if mostrar_laudo:
        st.divider()
        st.subheader("📄 Gerar Laudo DRE em PDF")
        if not LAUDO_AEP_DISPONIVEL:
            st.error("Módulo `gerar_laudo_aep.py` não encontrado na pasta do projeto.")
        elif st.button("📄 Gerar Laudo DRE em PDF", type="primary", use_container_width=True, key=f"{key_prefix}_btn_laudo_aep"):
            with st.spinner("Gerando laudo..."):
                dados_emp = {"Empresa": empresa_nome, "CNPJ": cnpj_cod, "Grau_Risco": grau_risco_emp or "—"}
                logo_path = "logo_sstg.png" if os.path.exists("logo_sstg.png") else None
                relatos = []
                for col in ("relato_dor", "relato_dificuldades", "relato_sugestoes"):
                    if col in df_aep.columns:
                        relatos.extend([r for r in df_aep[col].dropna().tolist() if str(r).strip()])
                try:
                    pdf_bytes = gerar_laudo_aep_pdf(
                        dados_empresa=dados_emp,
                        inventario=inventario,
                        total_respondentes=total_resp_aep,
                        total_autorizados=total_auth,
                        relatos=relatos,
                        logo_path=logo_path,
                    )
                    db.registrar_laudo(cnpj_cod, "DRE")
                    st.success("Laudo DRE gerado com sucesso!")
                    st.download_button(
                        "⬇️ Baixar Laudo DRE PDF",
                        pdf_bytes,
                        f"Laudo_DRE_{cnpj_cod}_{datetime.now().strftime('%d-%m-%Y')}.pdf",
                        "application/pdf",
                        use_container_width=True,
                        key=f"{key_prefix}_download_laudo_aep",
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar o laudo: {e}")


# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
db.ping()  # acorda o banco apos hibernacao (free tier)

st.set_page_config(
    page_title="DRE - DRPS | Gestão integrada de riscos ergonômicos e psicossociais (NR-1 / NR-17)",
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
    .hero-sstg{background:#282C5B;padding:48px 40px;border-radius:18px;color:white;text-align:center;margin-bottom:32px;box-shadow:0 8px 32px rgba(40,44,91,0.25);}
    .hero-sstg h1{color:white!important;font-size:2.4em!important;margin-bottom:10px;letter-spacing:2px;}
    .hero-sstg p{font-size:1.1em;opacity:.88;margin:0;}
    .hero-sstg .hero-nr{color:#9FD8A5;font-weight:600;opacity:1;margin-top:6px;}
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
                    DRE - DRPS
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
                    DRE - DRPS
                </span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    _opcoes_menu = [
        "🏠 Início",
        "📝 Questionários DRE-DRPS",
        "📊 Gestão das Respostas (RH)",
        "🔐 Admin SSTG (Gestão)"
    ]
    # Links dos questionários chegam com ?modulo=aep (DRE) ou ?cnpj=... (DRPS):
    # nesses casos o app abre direto no módulo de questionários, não na tela inicial.
    _param_modulo = st.query_params.get("modulo", "")
    _param_cnpj   = st.query_params.get("cnpj", "")
    _idx_menu = 1 if (_param_modulo == "aep" or _param_cnpj) else 0
    menu = st.radio("Módulo:", _opcoes_menu, index=_idx_menu)
    if menu == "📝 Questionários DRE-DRPS":
        _sub_quest = st.radio(
            "Questionário:",
            ["📋 Psicossocial (DRPS)", "🦴 Ergonômico (DRE)"],
            index=1 if _param_modulo == "aep" else 0,
        )
        # Mantém os valores internos antigos para o despacho dos módulos abaixo
        menu = ("🦴 Questionário Ergonômico (AEP)" if "(DRE)" in _sub_quest
                else "📋 Questionário Psicossocial")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.7em; opacity:0.5; text-align:center;'>v8.0 — DRE - DRPS<br>COPSOQ III + NR-17</p>",
        unsafe_allow_html=True
    )

# =============================================================================
# MÓDULO INÍCIO (TELA DE ABERTURA / DASHBOARD)
# =============================================================================
if menu == "🏠 Início":
    st.markdown("""
        <div class="hero-sstg" style="margin-bottom:8px;">
            <h1>DRE - DRPS</h1>
            <p>Gestão integrada de riscos ergonômicos e psicossociais, do questionário ao PGR</p>
            <p class="hero-nr">Em atendimento à NR-01 e à NR-17</p>
        </div>
        <div style="height:6px; background:#5A9F62; border-radius:3px; margin-bottom:30px;"></div>
    """, unsafe_allow_html=True)

    # ── Indicadores acumulados ────────────────────────────────────────────────
    df_ini = db.carregar_acessos()
    n_cnpjs = df_ini['CNPJ'].nunique() if not df_ini.empty else 0
    n_cpfs  = len(df_ini)
    _datas_rp  = db.datas_respostas()
    _datas_aep = db.datas_respostas_aep()
    n_quest = len(_datas_rp) + len(_datas_aep)
    _laudos = db.contar_laudos()
    n_laudos = sum(_laudos.values())

    def _card_kpi(col, cor, icone, valor, rotulo):
        col.markdown(f"""
            <div style="background:white; border-top:5px solid {cor}; border-radius:0 0 12px 12px;
                        padding:16px 18px; box-shadow:0 2px 10px rgba(0,0,0,0.07); text-align:center;">
                <div style="font-size:1.7em;">{icone}</div>
                <div style="font-size:2.1em; font-weight:800; color:{cor}; line-height:1.2;">{valor}</div>
                <div style="font-size:0.85em; color:#6B6966;">{rotulo}</div>
            </div>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    _card_kpi(k1, "#282C5B", "🏢", n_cnpjs,  "CNPJs cadastrados")
    _card_kpi(k2, "#4A90D9", "👥", n_cpfs,   "CPFs cadastrados")
    _card_kpi(k3, "#5A9F62", "📋", n_quest,  "Questionários respondidos")
    _card_kpi(k4, "#DC3B24", "📄", n_laudos, "Laudos gerados")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Gráficos (acumulados) ─────────────────────────────────────────────────
    import plotly.graph_objects as go

    g1, g2 = st.columns([3, 2])

    with g1:
        st.markdown("##### 📈 Evolução acumulada — questionários respondidos")
        # Datas no banco em dois formatos: "dd/mm/aaaa HH:MM" (DRPS) e "aaaa-mm-dd" (DRE)
        _s_raw = pd.Series(_datas_rp + _datas_aep, dtype="object").astype(str)
        _d_brh = pd.to_datetime(_s_raw, format="%d/%m/%Y %H:%M", errors="coerce")
        _d_br  = pd.to_datetime(_s_raw, format="%d/%m/%Y", errors="coerce")
        _d_iso = pd.to_datetime(_s_raw, format="%Y-%m-%d", errors="coerce")
        _serie_datas = _d_brh.fillna(_d_br).fillna(_d_iso).dropna()
        if _serie_datas.empty:
            st.info("Ainda não há respostas registradas.")
        else:
            _por_mes = _serie_datas.dt.to_period("M").value_counts().sort_index()
            _acum = _por_mes.cumsum()
            _labels = [p.strftime("%m/%Y") for p in _acum.index]
            fig_acum = go.Figure(go.Bar(
                x=_labels, y=_acum.values,
                marker_color="#5A9F62",
                text=_acum.values, textposition="outside",
            ))
            fig_acum.update_layout(
                height=320, margin=dict(l=10, r=10, t=20, b=10),
                yaxis_title=None, xaxis_title=None,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(rangemode="tozero"),
            )
            st.plotly_chart(fig_acum, use_container_width=True, key="ini_graf_acum")

    with g2:
        st.markdown("##### 📄 Laudos gerados")
        _qt_drps = _laudos.get("DRPS", 0)
        _qt_dre  = _laudos.get("DRE", 0)
        if _qt_drps + _qt_dre == 0:
            st.info("Nenhum laudo registrado ainda. A contagem inicia a partir desta versão.")
        else:
            fig_laudos = go.Figure(go.Bar(
                y=["DRPS", "DRE"], x=[_qt_drps, _qt_dre],
                orientation="h",
                marker_color=["#282C5B", "#DC3B24"],
                text=[_qt_drps, _qt_dre], textposition="outside",
            ))
            fig_laudos.update_layout(
                height=320, margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title=None, yaxis_title=None,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(rangemode="tozero"),
            )
            st.plotly_chart(fig_laudos, use_container_width=True, key="ini_graf_laudos")

    st.caption("Indicadores acumulados desde o início da operação do sistema. "
               "Selecione um módulo no menu lateral para começar.")

# =============================================================================
# MÓDULO ADMINISTRATIVO
# =============================================================================
elif menu == "🔐 Admin SSTG (Gestão)":

    if 'admin_logado' not in st.session_state:
        st.session_state.admin_logado = False
    if 'admin_perfil' not in st.session_state:
        st.session_state.admin_perfil = None   # "admin" ou "operacional"
    if 'admin_usuario' not in st.session_state:
        st.session_state.admin_usuario = None

    if not st.session_state.admin_logado:
        st.title("🔐 Acesso Restrito — Admin SSTG")
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            tab_login, tab_alterar = st.tabs(["🔑 Entrar", "🔄 Alterar Senha"])

            # ── ABA ENTRAR ────────────────────────────────────────────────────
            with tab_login:
                st.markdown("##### Identificação")

                # ── Seletor de usuários operacionais ──────────────────────────
                _df_ops = carregar_usuarios()
                _ops_ativos = (
                    _df_ops[_df_ops['Status'] == 'Ativo']
                    if not _df_ops.empty else pd.DataFrame()
                )
                _MANUAL = "✏️  Administrador / digitar manualmente"
                _opcoes = [_MANUAL]
                _mapa   = {}   # label → login
                if not _ops_ativos.empty:
                    for _, _row in _ops_ativos.iterrows():
                        _label = f"👤  {_row['Nome']}  ({_row['Usuario']})"
                        _opcoes.append(_label)
                        _mapa[_label] = _row['Usuario']

                _sel = st.selectbox(
                    "Selecione o usuário:",
                    _opcoes,
                    key="login_sel_usuario"
                )

                if _sel == _MANUAL:
                    usuario_in = st.text_input(
                        "Usuário:", placeholder="admin", key="login_usuario_manual"
                    )
                else:
                    usuario_in = _mapa[_sel]
                    st.caption(f"Login selecionado: **{usuario_in}**")

                senha_in = st.text_input("Senha:", type="password", key="login_senha")
                if st.button("Entrar", use_container_width=True, type="primary", key="btn_entrar"):
                    u = usuario_in.strip().lower()
                    if u == "admin" and hash_senha(senha_in) == get_senha_admin_hash():
                        st.session_state.admin_logado  = True
                        st.session_state.admin_perfil  = "admin"
                        st.session_state.admin_usuario = "admin"
                        st.rerun()
                    elif verificar_usuario_operacional(u, senha_in):
                        st.session_state.admin_logado  = True
                        st.session_state.admin_perfil  = "operacional"
                        st.session_state.admin_usuario = u
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos.")

            # ── ABA ALTERAR SENHA ─────────────────────────────────────────────
            with tab_alterar:
                st.markdown("##### Redefinir Senha")
                tipo_reset = st.radio(
                    "Tipo de acesso:",
                    ["👤 Administrador", "👥 Usuário Operacional"],
                    horizontal=True,
                    key="reset_tipo"
                )

                if tipo_reset == "👤 Administrador":
                    st.caption("Informe a senha atual para autorizar a troca.")
                    with st.form("form_reset_admin", clear_on_submit=True):
                        senha_atual_adm = st.text_input("Senha atual:", type="password")
                        nova_senha_adm  = st.text_input("Nova senha:", type="password")
                        conf_senha_adm  = st.text_input("Confirmar nova senha:", type="password")
                        subm_adm = st.form_submit_button(
                            "💾 Alterar Senha do Admin", use_container_width=True, type="primary"
                        )
                    if subm_adm:
                        if not senha_atual_adm or not nova_senha_adm:
                            st.error("Preencha todos os campos.")
                        elif hash_senha(senha_atual_adm) != get_senha_admin_hash():
                            st.error("❌ Senha atual incorreta.")
                        elif nova_senha_adm != conf_senha_adm:
                            st.error("As novas senhas não coincidem.")
                        elif len(nova_senha_adm) < 6:
                            st.error("A nova senha deve ter no mínimo 6 caracteres.")
                        else:
                            set_senha_admin(nova_senha_adm)
                            st.success("✅ Senha do administrador alterada com sucesso!")

                else:
                    st.caption("Requer a senha do Admin para autorizar a redefinição.")
                    with st.form("form_reset_op", clear_on_submit=True):
                        login_op      = st.text_input("Login do usuário:", placeholder="ex: joao.silva")
                        senha_adm_op  = st.text_input("Senha do Admin (autorização):", type="password")
                        nova_senha_op = st.text_input("Nova senha:", type="password")
                        conf_senha_op = st.text_input("Confirmar nova senha:", type="password")
                        subm_op = st.form_submit_button(
                            "💾 Redefinir Senha do Usuário", use_container_width=True, type="primary"
                        )
                    if subm_op:
                        if not login_op or not senha_adm_op or not nova_senha_op:
                            st.error("Preencha todos os campos.")
                        elif hash_senha(senha_adm_op) != get_senha_admin_hash():
                            st.error("❌ Senha do Admin incorreta. Operação não autorizada.")
                        elif nova_senha_op != conf_senha_op:
                            st.error("As novas senhas não coincidem.")
                        elif len(nova_senha_op) < 6:
                            st.error("A nova senha deve ter no mínimo 6 caracteres.")
                        else:
                            ok, msg = redefinir_senha_operacional(login_op.strip().lower(), nova_senha_op)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
        st.stop()

    st.title("🏢 Gestão de Empresas e Acessos")

    _perfil_logado = st.session_state.get('admin_perfil', 'admin')
    _usuario_logado = st.session_state.get('admin_usuario', 'admin')
    st.sidebar.caption(f"👤 {_usuario_logado} ({_perfil_logado})")
    if st.sidebar.button("🚪 Sair do Admin"):
        st.session_state.admin_logado  = False
        st.session_state.admin_perfil  = None
        st.session_state.admin_usuario = None
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

    t1, t2, t3, t8, t4, t5, t6, t7 = st.tabs([
        "🆕 Cadastro / Inclusão",
        "📋 Conferência e Correção",
        "📊 Resultados DRPS",
        "🦴 Resultados DRE",
        "🔄 Movimentação de Pessoal",
        "🔐 Segurança e Acesso RH",
        "📚 Documentação",
        "👥 Usuários"
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

                # CNAE e Grau de Risco
                st.markdown("**Dados para o Laudo AEP-RP**")
                c_cnae, c_grau = st.columns(2)
                cnae_manual  = c_cnae.text_input("CNAE Principal: *", placeholder="Ex: 4711-3/02", key="cnae_manual")
                grau_manual  = c_grau.selectbox("Grau de Risco: *", ["—", "1", "2", "3", "4"], key="grau_manual")

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
                    elif not cnae_manual.strip() or grau_manual == "—":
                        st.error("Preencha o CNAE Principal e o Grau de Risco (campos obrigatórios para o Laudo).")
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
                                "CNAE":        cnae_manual.strip(),
                                "Grau_Risco":  grau_manual,
                            }
                            novos, duplicados, invalidos = salvar_cadastro_completo(dados_emp, colaboradores)

                            # Gerar senha de acesso RH
                            if novos:
                                senha_rh = gerar_senha_rh()
                                db.atualizar_acessos_por_cnpj(cnpj_limpo, {"Senha_RH_Hash": hash_senha(senha_rh)})

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
            st.session_state.setdefault("csv_reset_id", 0)
            _csv_key = st.session_state.csv_reset_id

            if st.session_state.get("csv_sucesso_msg"):
                st.success(st.session_state.pop("csv_sucesso_msg"))

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
            cnpj_csv = col1.text_input("CNPJ (somente números)", placeholder="00000000000100", key=f"cnpj_csv_{_csv_key}")
            razao_csv = col2.text_input("Razão Social", key=f"razao_csv_{_csv_key}")

            # Período de aplicação
            st.markdown("**Período de aplicação do questionário**")
            c_ini_csv, c_fim_csv = st.columns(2)
            dt_ini_csv = c_ini_csv.date_input("Data de início", value=date.today(), format="DD/MM/YYYY", key=f"dt_ini_csv_{_csv_key}")
            dt_fim_csv = c_fim_csv.date_input("Data de encerramento", value=date.today(), format="DD/MM/YYYY", key=f"dt_fim_csv_{_csv_key}")

            # CNAE e Grau de Risco
            st.markdown("**Dados para o Laudo AEP-RP**")
            c_cnae_csv, c_grau_csv = st.columns(2)
            cnae_csv_val = c_cnae_csv.text_input("CNAE Principal: *", placeholder="Ex: 4711-3/02", key=f"cnae_csv_val_{_csv_key}")
            grau_csv_val = c_grau_csv.selectbox("Grau de Risco: *", ["—", "1", "2", "3", "4"], key=f"grau_csv_val_{_csv_key}")

            st.markdown("---")
            st.markdown("**Selecione o arquivo CSV**")
            uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"], key=f"upload_csv_{_csv_key}")

            if uploaded_file:
                try:
                    import unicodedata as _ud

                    def _fix_double_enc(s):
                        """Reverte dupla codificação: Excel abre UTF-8 como latin-1 e re-salva.
                        Ex: 'FunÃ§Ã£o'.encode('latin-1').decode('utf-8') → 'Função'"""
                        try:
                            return str(s).encode('latin-1').decode('utf-8')
                        except Exception:
                            return str(s)

                    def _norm_col(s):
                        """Remove acentos, BOM e espaços para comparação flexível."""
                        s = str(s).strip().lstrip('﻿').lstrip('﻿')
                        return ''.join(
                            c for c in _ud.normalize('NFKD', s)
                            if not _ud.combining(c)
                        ).lower()

                    def _tentar_ler(f, sep, enc):
                        f.seek(0)
                        return pd.read_csv(f, sep=sep, encoding=enc, dtype=str)

                    # Tenta todas as combinações de separador × encoding
                    df_upload = None
                    for _sep in (';', ',', '\t'):
                        for _enc in ('utf-8-sig', 'utf-8', 'latin-1', 'cp1252'):
                            try:
                                _df = _tentar_ler(uploaded_file, _sep, _enc)
                                # Aceita só se tiver ≥ 2 colunas (evita falso positivo)
                                if len(_df.columns) >= 2:
                                    df_upload = _df
                                    break
                            except Exception:
                                continue
                        if df_upload is not None:
                            break

                    if df_upload is None:
                        raise ValueError("Não foi possível ler o arquivo CSV.")

                    # Normaliza nomes de colunas — resolve dupla codificação e acentos
                    # 1º reverte dupla-codificação (FunÃ§Ã£o → Função)
                    # 2º remove acentos para comparação (funcao → cpf/funcao/departamento)
                    _mapa = {'cpf': 'CPF', 'funcao': 'Função', 'departamento': 'Departamento'}
                    df_upload.columns = [
                        _mapa.get(_norm_col(_fix_double_enc(c)), c) for c in df_upload.columns
                    ]

                    # Corrige CPF em notação científica (ex: 7,73E+09 → 07730000000)
                    if 'CPF' in df_upload.columns:
                        def _fix_cpf(v):
                            try:
                                return str(int(float(str(v).replace(',', '.')))).zfill(11)
                            except Exception:
                                return str(v).strip()
                        df_upload['CPF'] = df_upload['CPF'].apply(_fix_cpf)

                    # Validações
                    colunas_obrig = {"CPF", "Função", "Departamento"}
                    if not colunas_obrig.issubset(df_upload.columns):
                        cols_encontradas = ', '.join(df_upload.columns.tolist())
                        st.error(f"❌ Colunas obrigatórias não encontradas.\n\n"
                                 f"**Esperado:** CPF, Função, Departamento\n\n"
                                 f"**Encontrado no arquivo:** {cols_encontradas}")
                    else:
                        st.success(f"✅ Arquivo válido: {len(df_upload)} linhas detectadas")
                        st.dataframe(df_upload, use_container_width=True)

                        if st.button("💾 SALVAR COLABORADORES DO CSV", use_container_width=True):
                            cnpj_limpo_csv = cnpj_csv.strip().replace(".", "").replace("/", "").replace("-", "")
                            if not cnpj_limpo_csv or not razao_csv.strip():
                                st.error("Preencha CNPJ e Razão Social.")
                            elif not cnae_csv_val.strip() or grau_csv_val == "—":
                                st.error("Preencha o CNAE Principal e o Grau de Risco (campos obrigatórios para o Laudo).")
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
                                        "CNAE":        cnae_csv_val.strip(),
                                        "Grau_Risco":  grau_csv_val,
                                    }
                                    novos, duplicados, invalidos = salvar_cadastro_completo(dados_emp_csv, colaboradores_csv)

                                    # Gerar senha de acesso RH
                                    if novos:
                                        senha_rh = gerar_senha_rh()
                                        db.atualizar_acessos_por_cnpj(cnpj_limpo_csv, {"Senha_RH_Hash": hash_senha(senha_rh)})

                                        st.session_state.cnpj_registrado = cnpj_limpo_csv
                                        st.session_state.razao_registrada = razao_csv.strip()
                                        st.session_state.csv_sucesso_msg = (
                                            f"✅ {len(novos)} colaborador(es) cadastrado(s) com sucesso.\n\n"
                                            f"🔐 Credenciais de Acesso RH\n\n"
                                            f"Empresa: {razao_csv.strip()}  |  CNPJ: {cnpj_limpo_csv}\n\n"
                                            f"Senha de Acesso RH: {senha_rh}\n\n"
                                            "⚠️ Anote esta senha com segurança! Esta é a única vez que ela será exibida. "
                                            "Compartilhe com o RH da empresa."
                                        )

                                        # Limpa os campos do formulário para permitir novo cadastro
                                        st.session_state.csv_reset_id += 1
                                        st.rerun()

                                    if duplicados:
                                        st.warning(f"⚠️ CPF(s) já cadastrados: {', '.join(duplicados)}")
                                    if invalidos:
                                        st.error(f"❌ CPF(s) inválidos: {', '.join(invalidos)}")
                except Exception as e:
                    st.error(f"❌ Erro ao ler arquivo: {str(e)}")

        st.divider()
        st.subheader("🔗 Link do Questionário para Compartilhar")

        df_emp_links = db.carregar_acessos()
        if not df_emp_links.empty:
            empresas_unicas = df_emp_links.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].values
            for _, (empresa, cnpj_emp) in enumerate(empresas_unicas):
                link = f"{QUEST_PSICOSSOCIAL_URL}?cnpj={cnpj_emp}"
                col_empr, col_link = st.columns([2, 3])
                col_empr.write(f"**{empresa}**")
                col_link.code(link)
            st.caption("Copie e envie o link correspondente ao RH da empresa via WhatsApp, Email ou outro canal.")
        else:
            st.info("Nenhuma empresa registrada ainda.")

    # ── ABA 2: CONFERÊNCIA ────────────────────────────────────────────────────
    with t2:
        # ── Backup Completo ───────────────────────────────────────────────────
        with st.expander("💾 Backup — Exportar todos os dados antes de atualizar o sistema", expanded=False):
            st.warning(
                "⚠️ **ATENÇÃO:** O Streamlit Cloud apaga os dados a cada atualização do sistema (redeploy). "
                "**Sempre faça o backup antes de qualquer atualização.**"
            )
            zip_bytes = gerar_backup_zip()
            nome_zip  = f"backup_SSTG_DRPS_AEP_{datetime.now().strftime('%d-%m-%Y_%H%M')}.zip"
            st.download_button(
                label="📦 Baixar Backup Completo (ZIP)",
                data=zip_bytes,
                file_name=nome_zip,
                mime="application/zip",
                use_container_width=True,
                type="primary",
            )
            st.caption(f"Inclui: cadastros, usuários, configurações e todas as respostas. Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.divider()

        st.subheader("Cadastro Geral de Colaboradores Autorizados")
        df_verif = db.carregar_acessos()

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
            filtro     = st.selectbox("Filtrar por empresa:", empresas_lista, key="filtro_conf", index=None, placeholder="Digite o nome da empresa (em branco = todas)...")
            df_filtrado = df_verif if filtro in (None, "Todas") else df_verif[df_verif['Empresa'] == filtro]

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
                emp_per = st.selectbox("Empresa:", empresas_per, key="emp_periodo", index=None, placeholder="Digite o nome da empresa...")
                if not emp_per:
                    st.info("👆 Digite ou selecione a empresa para continuar.")
                else:
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
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

            if st.session_state.get('admin_perfil') == 'admin':
                with st.expander("⚠️ Zona de Perigo — use com cuidado"):
                    st.error("⚠️ As ações abaixo são **irreversíveis**. Confirme com a senha do Admin SSTG antes de prosseguir.")

                    zt1, zt2, zt3 = st.tabs(["🗑️ Excluir Empresa", "📊 Excluir Respostas", "💣 Resetar Tudo"])

                    # ── EXCLUIR EMPRESA INDIVIDUAL ────────────────────────────
                    with zt1:
                        st.warning("Remove **todos os acessos** e **todo o histórico de respostas** da empresa selecionada.")
                        df_zona = db.carregar_acessos()
                        if not df_zona.empty:
                            empresas_zona = df_zona.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                            ).tolist()
                            emp_del = st.selectbox("Empresa a excluir:", empresas_zona, key="zona_emp_del", index=None, placeholder="Digite o nome da empresa...")
                            if not emp_del:
                                st.info("👆 Digite ou selecione a empresa para continuar.")
                            else:
                                cnpj_del = emp_del.split("CNPJ: ")[-1]
                                nome_del = emp_del.split(" — CNPJ:")[0].strip()

                                # Contadores para exibir impacto
                                qtd_cpfs  = len(df_zona[df_zona['CNPJ'] == cnpj_del])
                                qtd_resp  = len(db.carregar_respostas(cnpj_del))

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
                                        db.deletar_acessos_empresa(cnpj_del)
                                        db.deletar_respostas_empresa(cnpj_del)
                                        st.success(f"✅ Empresa **{nome_del}** removida com sucesso. {qtd_cpfs} acesso(s) e {qtd_resp} resposta(s) apagadas.")
                                        st.rerun()
                        else:
                            st.info("Nenhuma empresa cadastrada.")

                    # ── EXCLUIR RESPOSTAS DA EMPRESA ─────────────────────────
                    with zt2:
                        st.warning("Remove **apenas as respostas** da empresa selecionada. O cadastro de colaboradores é preservado — eles poderão responder novamente.")
                        df_zona_r = db.carregar_acessos()
                        if not df_zona_r.empty:
                            empresas_zona_r = df_zona_r.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                            ).tolist()
                            emp_del_r  = st.selectbox("Empresa:", empresas_zona_r, key="zona_emp_del_r", index=None, placeholder="Digite o nome da empresa...")
                            if not emp_del_r:
                                st.info("👆 Digite ou selecione a empresa para continuar.")
                            else:
                                cnpj_del_r = emp_del_r.split("CNPJ: ")[-1]
                                nome_del_r = emp_del_r.split(" — CNPJ:")[0].strip()

                                qtd_resp_r = len(db.carregar_respostas(cnpj_del_r))
                                st.metric("Respostas que serão apagadas", qtd_resp_r)

                                if qtd_resp_r == 0:
                                    st.info("Esta empresa não possui respostas registradas.")
                                else:
                                    st.divider()
                                    st.markdown("**Confirme digitando a senha do Admin SSTG:**")
                                    senha_conf_r = st.text_input(
                                        "Senha Admin:", type="password", key="senha_conf_del_resp"
                                    )
                                    if st.button("📊 EXCLUIR RESPOSTAS DA EMPRESA", type="primary",
                                                 use_container_width=True, key="btn_del_respostas"):
                                        if not senha_conf_r:
                                            st.error("Digite a senha do Admin para confirmar.")
                                        elif senha_conf_r != SENHA_ADMIN:
                                            st.error("❌ Senha incorreta. Operação cancelada.")
                                        else:
                                            db.deletar_respostas_empresa(cnpj_del_r)
                                            st.success(f"✅ {qtd_resp_r} resposta(s) da empresa **{nome_del_r}** apagadas. Cadastro preservado.")
                                            st.rerun()
                        else:
                            st.info("Nenhuma empresa cadastrada.")

                    # ── RESETAR TUDO ──────────────────────────────────────────
                    with zt3:
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
                                db.deletar_todos_acessos()
                                db.deletar_todas_respostas()
                                st.success("✅ Banco de dados completo resetado.")
                                st.rerun()
        else:
            st.info("Nenhum registro encontrado. Faça o cadastro na aba anterior.")

    # ── ABA 3: RESULTADOS ─────────────────────────────────────────────────────
    with t3:
        st.subheader("Resultados Consolidados por Empresa")
        df_acessos = db.carregar_acessos()

        if not df_acessos.empty:
            opcoes_empresa = df_acessos.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
            ).tolist()
            empresa_sel = st.selectbox("Selecione a empresa:", opcoes_empresa, index=None, placeholder="Digite o nome da empresa...")
            if not empresa_sel:
                st.info("👆 Digite ou selecione a empresa para continuar.")
            else:
                cnpj_cod    = empresa_sel.split("CNPJ: ")[-1]

                # ── Link individualizado ──────────────────────────────────────────
                with st.expander("🔗 Link do Questionário para esta empresa"):
                    link_emp = f"{QUEST_PSICOSSOCIAL_URL}?cnpj={cnpj_cod}"
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
                                            app_url=QUEST_PSICOSSOCIAL_URL
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
                                        whatsapp_link = f"https://wa.me/?text=Prezado(a)%20RH%2C%0A%0AConvido-o%20a%20participar%20da%20avaliação%20de%20Riscos%20Psicossociais%20(SSTG-DRPS%20AEP-RP)%20através%20do%20link%3A%20{QUEST_PSICOSSOCIAL_URL}%3Fcnpj%3D{cnpj_cod}%0A%0AEsta%20é%20uma%20ferramenta%20essencial%20para%20diagnóstico%20do%20ambiente%20de%20trabalho%20conforme%20NR-1.%0A%0AObrigado!"
                                        st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📱 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

                                    with col2:
                                        email_link = f"mailto:?subject=Avaliação de Riscos Psicossociais - SSTG DRPS AEP-RP&body=Prezado(a) RH,%0A%0AConvido-o a participar da avaliação de Riscos Psicossociais (SSTG-DRPS AEP-RP) conforme NR-1.%0A%0ALink para acesso:%0A{QUEST_PSICOSSOCIAL_URL}?cnpj={cnpj_cod}%0A%0AEsta avaliação é fundamental para diagnóstico do ambiente de trabalho.%0A%0AObrigado!"
                                        st.markdown(f'<a href="{email_link}"><button style="width:100%; padding:10px; background-color:#0078D4; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📧 Enviar via Email</button></a>', unsafe_allow_html=True)

                                    st.caption("💡 Dica: Use esta imagem em emails, WhatsApp, Telegram ou redes sociais para aumentar a adesão ao questionário.")

                                except Exception as e:
                                    st.error(f"Erro ao gerar imagem: {e}")
                    else:
                        st.warning("Módulo de compartilhamento não disponível. Verifique se `qrcode` e `Pillow` estão instalados.")

                df_res = db.carregar_respostas(cnpj_cod)
                if not df_res.empty:

                    total_auth = len(df_acessos[df_acessos['CNPJ'] == cnpj_cod])
                    total_resp = len(df_res)
                    pct        = round((total_resp / total_auth) * 100, 1) if total_auth > 0 else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("CPFs Autorizados",   total_auth)
                    c2.metric("Respostas Recebidas", total_resp)
                    c3.metric("Taxa de Adesão",      f"{pct}%")

                    # Gráfico de adesão
                    st.subheader("📊 Adesão ao Questionário")
                    try:
                        import plotly.graph_objects as go
                        fig_ades = go.Figure(go.Bar(
                            x=["Autorizados", "Respondidos"],
                            y=[total_auth, total_resp],
                            marker_color=["#282C5B", "#5A9F62"],
                            text=[str(total_auth), str(total_resp)],
                            textposition="outside",
                            width=0.4,
                        ))
                        fig_ades.update_layout(
                            yaxis=dict(title="Quantidade", range=[0, max(total_auth, 1) * 1.2]),
                            xaxis=dict(title=""),
                            plot_bgcolor="white",
                            margin=dict(t=20, b=20, l=40, r=40),
                            height=260,
                            showlegend=False,
                        )
                        st.plotly_chart(fig_ades, use_container_width=True)
                    except ImportError:
                        df_chart = pd.DataFrame({"Questionários": {"Autorizados": total_auth, "Respondidos": total_resp}})
                        st.bar_chart(df_chart, use_container_width=True, height=260)

                    st.divider()

                    # Médias por dimensão — gráfico de barras coloridas
                    cols_media = [c for c in df_res.columns if c.startswith('Media_') and c != 'Media_Geral']
                    if cols_media:
                        _bloco_grafico_dimensoes(df_res, cols_media, key_prefix="admin")

                    st.divider()
                    st.subheader("Histórico de Respostas")
                    colunas_exibir = [c for c in df_res.columns if c != 'CPF_Hash']
                    st.dataframe(df_res[colunas_exibir], use_container_width=True)

                    csv_res = df_res[colunas_exibir].to_csv(index=False, sep=';', encoding='utf-8-sig')
                    st.download_button(
                        "⬇️ Baixar resultados (.csv)",
                        csv_res, f"resultados_{cnpj_cod}.csv", "text/csv"
                    )

                    # ── Gerar Laudo DRPS em PDF ───────────────────────────────────
                    st.divider()
                    st.subheader("📄 Gerar Laudo DRPS em PDF")

                    if not LAUDO_DISPONIVEL:
                        st.error("Módulo `gerar_laudo.py` não encontrado na pasta do projeto.")
                    elif cols_media:
                        # Carrega CNAE e Grau de Risco do cadastro da empresa
                        df_acessos_res = db.carregar_acessos()
                        _row_emp = df_acessos_res[df_acessos_res['CNPJ'] == cnpj_cod]
                        if not _row_emp.empty:
                            _r = _row_emp.iloc[0]
                            _cnae_default = str(_r.get('CNAE', _r.get('cnae', ''))).strip()
                            _grau_default = str(_r.get('Grau_Risco', _r.get('grau_risco', ''))).strip()
                        else:
                            _cnae_default, _grau_default = '', ''

                        st.caption(f"CNAE Principal: **{_cnae_default or '—'}** | Grau de Risco: **{_grau_default or '—'}** "
                                    "(dados do cadastro da empresa)")

                        if st.button("📄 Gerar Laudo DRPS em PDF", type="primary", use_container_width=True):
                            with st.spinner("Gerando laudo..."):
                                nome_empresa   = empresa_sel.split(" — CNPJ:")[0].strip()
                                df_num_laudo   = df_res[cols_media].apply(pd.to_numeric, errors='coerce')
                                medias_laudo   = df_num_laudo.mean().to_dict()
                                medias_dim     = {}
                                for col, val in medias_laudo.items():
                                    nome_dim = col.replace("Media_", "")
                                    dim_key  = f"Dim_{nome_dim}"
                                    medias_dim[dim_key] = round(4.0 - val, 2) if nome_dim.lower() in _DIMS_INV_LOWER else val

                                _cnae_final = _cnae_default if _cnae_default else "—"
                                _grau_final = _grau_default if _grau_default else "—"

                                dados_emp = {
                                    "Empresa":    nome_empresa,
                                    "CNPJ":       cnpj_cod,
                                    "CNAE":       _cnae_final,
                                    "Grau_Risco": _grau_final,
                                }
                                logo_path = "logo_sstg.png" if os.path.exists("logo_sstg.png") else None
                                try:
                                    pdf_bytes = gerar_laudo_pdf(
                                        dados_empresa=dados_emp,
                                        medias_por_dim=medias_dim,
                                        total_respondentes=total_resp,
                                        logo_path=logo_path,
                                        total_autorizados=total_auth,
                                    )
                                    db.registrar_laudo(cnpj_cod, "DRPS")
                                    st.success("Laudo DRPS gerado com sucesso!")
                                    st.download_button(
                                        "⬇️ Baixar Laudo DRPS PDF",
                                        pdf_bytes,
                                        f"Laudo_DRPS_{cnpj_cod}_{datetime.now().strftime('%d-%m-%Y')}.pdf",
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
        df_mov = db.carregar_acessos()

        if df_mov.empty:
            st.info("Nenhuma empresa cadastrada. Faça o cadastro primeiro.")
        else:
            df_mov = normalizar_status(df_mov)
            m1, m2, m3, m4, m5 = st.tabs(["➕ Admissão", "🚫 Desligamento", "🔴 Inativação", "✅ Reativação", "🗑️ Exclusão"])

            # ── ADMISSÃO ─────────────────────────────────────────────────────
            with m1:
                st.markdown("#### Incluir colaborador(es) em empresa já cadastrada")
                empresas_mov = df_mov.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                    lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                ).tolist()
                empresa_adm  = st.selectbox("Empresa:", empresas_mov, key="emp_adm", index=None, placeholder="Digite o nome da empresa...")
                if not empresa_adm:
                    st.info("👆 Digite ou selecione a empresa para continuar.")
                else:
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
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            # ── INATIVAÇÃO TEMPORÁRIA ────────────────────────────────────────
            with m3:
                st.markdown("#### Inativar colaborador temporariamente")
                st.info("Use para afastamentos, licenças ou suspensões temporárias. O CPF ficará bloqueado para responder, mas poderá ser reativado posteriormente.")

                col1, col2 = st.columns([2, 1])
                cpf_inat    = col1.text_input("CPF (somente números):", max_chars=11, key="cpf_inat")
                motivo_inat = col2.selectbox(
                    "Motivo:", [
                        "Licença médica", "Licença maternidade", "Licença paternidade",
                        "Afastamento INSS", "Férias prolongadas", "Suspensão disciplinar", "Outro"
                    ],
                    key="motivo_inat"
                )

                if cpf_inat and len(cpf_inat) == 11:
                    reg_inat = df_mov[df_mov['CPF'] == cpf_inat]
                    if not reg_inat.empty:
                        r = reg_inat.iloc[0]
                        st.info(f"Colaborador: **{r['Empresa']}** | Função: **{r.get('Função','—')}** | Status atual: **{r.get('Status','Ativo')}**")
                    else:
                        st.warning("CPF não encontrado no sistema.")

                if st.button("🔴 INATIVAR TEMPORARIAMENTE", use_container_width=True, key="btn_inat", type="primary"):
                    cpf_i = cpf_inat.strip().replace(".", "").replace("-", "")
                    if not validar_cpf_formato(cpf_i):
                        st.error("CPF inválido.")
                    else:
                        ok, msg = atualizar_status_cpf(cpf_i, "Inativo", motivo_inat)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            # ── REATIVAÇÃO ───────────────────────────────────────────────────
            with m4:
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

            # ── EXCLUSÃO DE CADASTRO ─────────────────────────────────────────
            with m5:
                st.markdown("#### Excluir colaborador cadastrado por engano")
                st.error("⚠️ **Ação irreversível.** Use apenas para corrigir erros de cadastro. O registro será permanentemente removido do banco de dados.")

                empresas_exc = df_mov.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                    lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
                ).tolist()
                empresa_exc = st.selectbox("Empresa:", empresas_exc, key="emp_exc", index=None, placeholder="Digite o nome da empresa...")
                if not empresa_exc:
                    st.info("👆 Digite ou selecione a empresa para continuar.")
                else:
                    cnpj_exc    = empresa_exc.split("CNPJ: ")[-1]

                    cpf_exc = st.text_input("CPF do colaborador a excluir (somente números):", max_chars=11, key="cpf_exc")

                    if cpf_exc and len(cpf_exc) == 11:
                        reg_exc = df_mov[(df_mov['CPF'] == cpf_exc) & (df_mov['CNPJ'] == cnpj_exc)]
                        if not reg_exc.empty:
                            r = reg_exc.iloc[0]
                            st.warning(f"Colaborador encontrado: **{r.get('Função','—')}** | Depto: **{r.get('Departamento','—')}** | Status: **{r.get('Status','Ativo')}**")
                            confirmar = st.checkbox(f"Confirmo a exclusão definitiva do CPF `{cpf_exc}` desta empresa.", key="chk_exc")
                            if st.button("🗑️ EXCLUIR COLABORADOR", use_container_width=True, key="btn_exc", type="primary", disabled=not confirmar):
                                cpf_e = cpf_exc.strip().replace(".", "").replace("-", "")
                                db.deletar_acesso_cpf(cpf_e, cnpj_exc)
                                st.success(f"✅ CPF {cpf_exc} removido com sucesso da empresa.")
                                st.rerun()
                        else:
                            st.warning("CPF não encontrado nesta empresa.")

    # ── ABA 5: SEGURANÇA E ACESSO RH ──────────────────────────────────────────
    with t5:
        st.subheader("🔐 Segurança e Acesso RH")
        st.info("Gere ou redefina senhas de acesso para o módulo 'Gestão das Respostas (RH)'")

        df_acessos = db.carregar_acessos()

        if not df_acessos.empty:
            # Seleção de empresa
            empresas_unicas = df_acessos.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
            ).tolist()

            empresa_sel = st.selectbox("Selecione a empresa para gerar nova senha RH:", empresas_unicas, key="seg_empresa_sel", index=None, placeholder="Digite o nome da empresa...")
            if not empresa_sel:
                st.info("👆 Digite ou selecione a empresa para continuar.")
            else:
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

                        db.atualizar_acessos_por_cnpj(cnpj_cod, {"Senha_RH_Hash": hash_senha(nova_senha)})

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
        st.subheader("📚 Documentação SSTG - DRPS AEP-RP Diagnóstico de Riscos Psicossociais e Ergonômicos (NR-1 / NR-17)")
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

    # ── ABA 7: USUÁRIOS OPERACIONAIS ─────────────────────────────────────────
    with t7:
        st.subheader("👥 Gerenciamento de Usuários Operacionais")

        if st.session_state.get('admin_perfil') != 'admin':
            st.warning("⛔ Esta aba é restrita ao Administrador SSTG.")
            st.info("Usuários operacionais não têm permissão para gerenciar outros usuários.")
        else:
            st.info(
                "Usuários operacionais têm acesso ao Admin SSTG com as mesmas abas, "
                "exceto esta (**👥 Usuários**) e a **Zona de Perigo**."
            )

            # ── CRIAR NOVO USUÁRIO ────────────────────────────────────────────
            with st.expander("➕ Criar Novo Usuário Operacional", expanded=True):
                with st.form("form_novo_usuario", clear_on_submit=True):
                    col_u1, col_u2 = st.columns(2)
                    novo_login  = col_u1.text_input("Login (usuário):", placeholder="ex: joao.silva")
                    novo_nome   = col_u2.text_input("Nome completo:")
                    col_u3, col_u4 = st.columns(2)
                    nova_senha  = col_u3.text_input("Senha:", type="password")
                    conf_senha  = col_u4.text_input("Confirmar senha:", type="password")
                    submitted_u = st.form_submit_button("✅ Criar Usuário", use_container_width=True, type="primary")

                if submitted_u:
                    if not novo_login or not novo_nome or not nova_senha:
                        st.error("Preencha todos os campos.")
                    elif nova_senha != conf_senha:
                        st.error("As senhas não coincidem.")
                    elif len(nova_senha) < 6:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    elif novo_login.strip().lower() == "admin":
                        st.error("O login 'admin' é reservado.")
                    else:
                        ok, msg = criar_usuario_operacional(novo_login.strip().lower(), novo_nome, nova_senha)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            st.divider()

            # ── LISTAR USUÁRIOS ───────────────────────────────────────────────
            st.subheader("Usuários Cadastrados")
            df_usr = carregar_usuarios()

            if df_usr.empty:
                st.info("Nenhum usuário operacional cadastrado ainda.")
            else:
                # Exibir tabela sem a coluna de hash
                df_exib = df_usr[["Usuario", "Nome", "Status", "Data_Criacao"]].copy()
                df_exib.columns = ["Login", "Nome", "Status", "Criado em"]
                st.dataframe(df_exib, use_container_width=True, hide_index=True)

                st.divider()
                st.subheader("Ativar / Desativar Usuário")

                usuarios_lista = df_usr['Usuario'].tolist()
                usr_sel = st.selectbox("Selecione o usuário:", usuarios_lista, key="usr_sel_acao")

                if usr_sel:
                    status_atual = df_usr.loc[df_usr['Usuario'] == usr_sel, 'Status'].iloc[0]
                    st.caption(f"Status atual: **{status_atual}**")

                    col_at, col_des = st.columns(2)
                    with col_at:
                        if st.button("✅ Ativar", use_container_width=True,
                                     disabled=(status_atual == 'Ativo'), key="btn_ativar_usr"):
                            ok, msg = reativar_usuario_operacional(usr_sel)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                            st.rerun()
                    with col_des:
                        if st.button("🚫 Desativar", use_container_width=True,
                                     disabled=(status_atual == 'Inativo'), key="btn_desativar_usr"):
                            ok, msg = desativar_usuario_operacional(usr_sel)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                            st.rerun()

                st.divider()
                st.subheader("🔑 Redefinir Senha de Usuário Operacional")
                df_usr2 = carregar_usuarios()
                if not df_usr2.empty:
                    usr_reset = st.selectbox(
                        "Usuário para redefinir senha:", df_usr2['Usuario'].tolist(), key="usr_reset_sel"
                    )
                    with st.form("form_reset_usr_interno", clear_on_submit=True):
                        nova_p  = st.text_input("Nova senha:", type="password", key="ri_nova")
                        conf_p  = st.text_input("Confirmar nova senha:", type="password", key="ri_conf")
                        subm_ri = st.form_submit_button("💾 Redefinir Senha", use_container_width=True, type="primary")
                    if subm_ri:
                        if not nova_p:
                            st.error("Informe a nova senha.")
                        elif nova_p != conf_p:
                            st.error("As senhas não coincidem.")
                        elif len(nova_p) < 6:
                            st.error("Mínimo de 6 caracteres.")
                        else:
                            ok, msg = redefinir_senha_operacional(usr_reset, nova_p)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

            st.divider()
            st.subheader("🔐 Alterar Senha do Administrador")
            with st.form("form_alterar_admin_t7", clear_on_submit=True):
                s_atual = st.text_input("Senha atual:", type="password", key="t7_s_atual")
                s_nova  = st.text_input("Nova senha:", type="password", key="t7_s_nova")
                s_conf  = st.text_input("Confirmar nova senha:", type="password", key="t7_s_conf")
                subm_adm_t7 = st.form_submit_button("💾 Alterar Senha Admin", use_container_width=True, type="primary")
            if subm_adm_t7:
                if not s_atual or not s_nova:
                    st.error("Preencha todos os campos.")
                elif hash_senha(s_atual) != get_senha_admin_hash():
                    st.error("❌ Senha atual incorreta.")
                elif s_nova != s_conf:
                    st.error("As novas senhas não coincidem.")
                elif len(s_nova) < 6:
                    st.error("Mínimo de 6 caracteres.")
                else:
                    set_senha_admin(s_nova)
                    st.success("✅ Senha do administrador alterada com sucesso!")

    # ── ABA 8: RESULTADOS AEP (NR-17) ─────────────────────────────────────────
    with t8:
        st.subheader("Resultados da Avaliação Ergonômica (AEP / NR-17)")
        df_acessos_aep = db.carregar_acessos()

        if not df_acessos_aep.empty:
            opcoes_empresa_aep = df_acessos_aep.drop_duplicates('CNPJ')[['Empresa', 'CNPJ']].apply(
                lambda r: f"{r['Empresa']} — CNPJ: {r['CNPJ']}", axis=1
            ).tolist()
            empresa_sel_aep = st.selectbox("Selecione a empresa:", opcoes_empresa_aep, key="aep_admin_empresa_sel", index=None, placeholder="Digite o nome da empresa...")
            if not empresa_sel_aep:
                st.info("👆 Digite ou selecione a empresa para continuar.")
            else:
                cnpj_cod_aep    = empresa_sel_aep.split("CNPJ: ")[-1]
                nome_empresa_aep = empresa_sel_aep.split(" — CNPJ:")[0].strip()

                with st.expander("🔗 Link do Questionário AEP para esta empresa"):
                    link_emp_aep = f"{QUEST_AEP_URL}?cnpj={cnpj_cod_aep}"
                    st.code(link_emp_aep, language=None)
                    st.caption(
                        "Copie e envie este link para o RH da empresa repassar aos colaboradores responderem "
                        "a Avaliação Ergonômica (AEP). No app, selecione o módulo '🦴 Questionário Ergonômico (AEP)'."
                    )

                total_auth_aep = len(df_acessos_aep[df_acessos_aep['CNPJ'] == cnpj_cod_aep])
                _bloco_resultados_aep(cnpj_cod_aep, total_auth_aep, key_prefix="admin", empresa_nome=nome_empresa_aep, mostrar_laudo=True)
        else:
            st.info("Nenhuma empresa cadastrada. Faça o cadastro primeiro.")

# =============================================================================
# MÓDULO GESTÃO DAS RESPOSTAS (RH)
# =============================================================================
elif menu == "📊 Gestão das Respostas (RH)":
    if 'rh_logado' not in st.session_state:
        st.session_state.rh_logado = False
        st.session_state.rh_cnpj = None

    if not st.session_state.rh_logado:
        # ── Acesso livre para Admin master (sem necessidade de senha RH) ───────
        if st.session_state.get('admin_logado') and st.session_state.get('admin_perfil') == 'admin':
            st.success("🔓 Acesso Admin Master — selecione a empresa para acessar diretamente, sem senha.")
            df_acessos_admin = db.carregar_acessos()
            if not df_acessos_admin.empty:
                df_emp_admin = df_acessos_admin.drop_duplicates(subset=["CNPJ"])
                opcoes_emp_admin = {
                    f"{row['Empresa']} — CNPJ: {row['CNPJ']}": row['CNPJ']
                    for _, row in df_emp_admin.iterrows()
                }
                emp_sel_admin = st.selectbox("Empresa:", list(opcoes_emp_admin.keys()), key="rh_admin_empresa_sel")
                if st.button("🔓 Acessar como Admin", use_container_width=True, key="rh_admin_acesso_btn"):
                    cnpj_sel_admin = opcoes_emp_admin[emp_sel_admin]
                    st.session_state.rh_logado = True
                    st.session_state.rh_cnpj = cnpj_sel_admin
                    st.session_state.rh_empresa = df_emp_admin[df_emp_admin['CNPJ'] == cnpj_sel_admin].iloc[0]['Empresa']
                    st.rerun()
            st.divider()

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
                df_acessos = db.carregar_acessos()

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
    df_acessos = db.carregar_acessos()

    # ── Links dos Questionários ─────────────────────────────────────────────
    with st.expander("🔗 Links dos Questionários para esta empresa", expanded=True):
        st.markdown("**📋 Questionário Psicossocial (COPSOQ III)**")
        link_emp = f"{QUEST_PSICOSSOCIAL_URL}?cnpj={cnpj_cod}"
        st.code(link_emp, language=None)
        st.caption(
            "Copie e envie este link para os colaboradores da empresa responderem o "
            "Questionário Psicossocial. Funciona em qualquer dispositivo, conectado à internet."
        )

        st.divider()

        st.markdown("**🦴 Questionário Ergonômico (AEP / NR-17)**")
        link_emp_aep = f"{QUEST_AEP_URL}?cnpj={cnpj_cod}"
        st.code(link_emp_aep, language=None)
        st.caption(
            "Copie e envie este link para os colaboradores da empresa responderem a "
            "Avaliação Ergonômica (AEP). Pode ser enviado de forma independente do questionário acima."
        )

    # ── Card do E-book Educativo ───────────────────────────────────────────
    with st.expander("📘 E-books Educativos — Compartilhe com os Colaboradores", expanded=True):
        st.markdown(
            "Envie o e-book correspondente **antes** do link de cada questionário. "
            "Ele explica o que é a avaliação, garante o anonimato e incentiva a participação."
        )

        st.markdown("**📋 E-book — Questionário Psicossocial**")
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #282C5B 0%, #1e3a8a 60%, #5A9F62 100%);
                border-radius: 14px; padding: 24px 26px; color: white; margin: 8px 0 16px 0;
                box-shadow: 0 4px 20px rgba(40,44,91,0.25);
            ">
                <div style="font-size:0.68em; letter-spacing:2px; opacity:0.7; text-transform:uppercase; margin-bottom:6px;">
                    Material de apoio · SSTG E-Social
                </div>
                <div style="font-size:1.2em; font-weight:800; margin-bottom:8px;">
                    📘 Sua Voz Importa — Saúde Mental no Trabalho
                </div>
                <div style="opacity:0.88; font-size:0.88em; margin-bottom:16px;">
                    E-book educativo: o que é a avaliação psicossocial, como funciona,
                    por que é anônima e como as respostas geram mudanças reais.
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">📖 Leitura rápida</span>
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">🔒 Explica o anonimato</span>
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">📱 Funciona no celular</span>
                </div>
                <a href="{EBOOK_URL}" target="_blank" style="
                    display:inline-block; background:#DC3B24; color:white;
                    text-decoration:none; font-weight:700; padding:9px 22px;
                    border-radius:50px; font-size:0.88em;
                ">📘 Abrir E-book ↗</a>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("**Link do e-book para copiar e enviar:**")
        st.code(EBOOK_URL, language=None)
        st.caption("💡 Sugestão: envie o e-book 2 a 3 dias antes de abrir o questionário para aumentar a adesão.")

        st.divider()

        st.markdown("**🦴 E-book — Questionário Ergonômico (AEP / NR-17)**")
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #282C5B 0%, #1e3a8a 60%, #5A9F62 100%);
                border-radius: 14px; padding: 24px 26px; color: white; margin: 8px 0 16px 0;
                box-shadow: 0 4px 20px rgba(40,44,91,0.25);
            ">
                <div style="font-size:0.68em; letter-spacing:2px; opacity:0.7; text-transform:uppercase; margin-bottom:6px;">
                    Material de apoio · SSTG E-Social
                </div>
                <div style="font-size:1.2em; font-weight:800; margin-bottom:8px;">
                    🦴 Cuide do Seu Corpo no Trabalho — Avaliação Ergonômica (AEP)
                </div>
                <div style="opacity:0.88; font-size:0.88em; margin-bottom:16px;">
                    E-book educativo: o que é a Avaliação Ergonômica Preliminar (NR-17), como funciona,
                    por que é anônima e como as respostas ajudam a melhorar o posto de trabalho.
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">📖 Leitura rápida</span>
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">🔒 Explica o anonimato</span>
                    <span style="background:rgba(255,255,255,0.15); border-radius:20px; padding:3px 10px; font-size:0.75em;">📱 Funciona no celular</span>
                </div>
                <a href="{EBOOK_AEP_URL}" target="_blank" style="
                    display:inline-block; background:#DC3B24; color:white;
                    text-decoration:none; font-weight:700; padding:9px 22px;
                    border-radius:50px; font-size:0.88em;
                ">🦴 Abrir E-book ↗</a>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("**Link do e-book para copiar e enviar:**")
        st.code(EBOOK_AEP_URL, language=None)
        st.caption("💡 Sugestão: envie o e-book 2 a 3 dias antes de abrir o questionário para aumentar a adesão.")

    # ── Gerar Imagem de Compartilhamento ───────────────────────────────────
    with st.expander("🖼️ Gerar QRCode do Questionário para Compartilhamento"):
        st.info("Gere uma imagem com QR Code para compartilhar nas redes sociais ou enviar por email.")

        if COMPARTILHAMENTO_DISPONIVEL:
            col_gerar, col_espacador = st.columns([2, 1])

            with col_gerar:
                if st.button("🎨 Gerar Imagem com QR Code", use_container_width=True, key="btn_gerar_img_rh"):
                    try:
                        nome_empresa = st.session_state.rh_empresa

                        with st.spinner("Gerando imagem..."):
                            img_bytes = gerar_imagem_compartilhamento_simples(
                                empresa_nome=nome_empresa,
                                cnpj=cnpj_cod,
                                app_url=QUEST_PSICOSSOCIAL_URL
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
                            whatsapp_link = f"https://wa.me/?text=Prezado(a)%20Colaborador(a)%2C%0A%0AConvido-o%20a%20participar%20da%20avaliação%20de%20Riscos%20Psicossociais%20(SSTG-DRPS%20AEP-RP)%20através%20do%20link%3A%20{QUEST_PSICOSSOCIAL_URL}%3Fcnpj%3D{cnpj_cod}%0A%0AEsta%20é%20uma%20ferramenta%20essencial%20para%20diagnóstico%20do%20ambiente%20de%20trabalho%20conforme%20NR-1.%0A%0AObrigado!"
                            st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📱 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

                        with col2:
                            email_link = f"mailto:?subject=Convite - Avaliação de Riscos Psicossociais&body=Prezado(a) Colaborador(a),%0A%0AConvidamos-o a participar da avaliação de Riscos Psicossociais (SSTG-DRPS AEP-RP).%0A%0ALink para acesso:%0A{QUEST_PSICOSSOCIAL_URL}?cnpj={cnpj_cod}%0A%0AEsta avaliação é fundamental para diagnóstico do ambiente de trabalho conforme NR-1.%0A%0AObrigado!"
                            st.markdown(f'<a href="{email_link}"><button style="width:100%; padding:10px; background-color:#0078D4; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📧 Enviar via Email</button></a>', unsafe_allow_html=True)

                        st.caption("💡 Dica: Use esta imagem em emails, WhatsApp, Telegram ou redes sociais para aumentar a adesão ao questionário.")

                    except Exception as e:
                        st.error(f"Erro ao gerar imagem: {e}")
        else:
            st.warning("Módulo de compartilhamento não disponível. Verifique se `qrcode` e `Pillow` estão instalados.")

    # ── Resultado das Respostas ────────────────────────────────────────────
    st.divider()
    st.subheader("📈 Resultado das Respostas")

    df_res = db.carregar_respostas(cnpj_cod)
    if not df_res.empty:

        total_auth = len(df_acessos[df_acessos['CNPJ'] == cnpj_cod])
        total_resp = len(df_res)
        pct        = round((total_resp / total_auth) * 100, 1) if total_auth > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("CPFs Autorizados",   total_auth)
        c2.metric("Respostas Recebidas", total_resp)
        c3.metric("Taxa de Adesão",      f"{pct}%")

        # Gráfico de adesão
        st.subheader("📊 Adesão ao Questionário")
        try:
            import plotly.graph_objects as go
            fig_ades = go.Figure(go.Bar(
                x=["Autorizados", "Respondidos"],
                y=[total_auth, total_resp],
                marker_color=["#282C5B", "#5A9F62"],
                text=[str(total_auth), str(total_resp)],
                textposition="outside",
                width=0.4,
            ))
            fig_ades.update_layout(
                yaxis=dict(title="Quantidade", range=[0, max(total_auth, 1) * 1.2]),
                xaxis=dict(title=""),
                plot_bgcolor="white",
                margin=dict(t=20, b=20, l=40, r=40),
                height=260,
                showlegend=False,
            )
            st.plotly_chart(fig_ades, use_container_width=True)
        except ImportError:
            df_chart = pd.DataFrame({"Questionários": {"Autorizados": total_auth, "Respondidos": total_resp}})
            st.bar_chart(df_chart, use_container_width=True, height=260)

        # Médias por dimensão — gráfico de barras coloridas
        cols_media_rh = [c for c in df_res.columns if c.startswith('Media_') and c != 'Media_Geral']
        if cols_media_rh:
            st.divider()
            _bloco_grafico_dimensoes(df_res, cols_media_rh, key_prefix="rh")

        st.divider()
        colunas_exibir_rh = [c for c in df_res.columns if c != 'CPF_Hash']
        csv_rh = df_res[colunas_exibir_rh].to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button("⬇️ Baixar resultados (.csv)", csv_rh, f"resultados_{cnpj_cod}.csv", "text/csv")
    else:
        st.info("Nenhuma resposta registrada ainda para esta empresa.")

    # ── Resultados AEP (Avaliação Ergonômica) ──────────────────────────────
    st.divider()
    st.subheader("🦴 Resultados — Avaliação Ergonômica (AEP / NR-17)")
    total_auth_rh = len(df_acessos[df_acessos['CNPJ'] == cnpj_cod])
    _bloco_resultados_aep(cnpj_cod, total_auth_rh, key_prefix="rh", empresa_nome=st.session_state.rh_empresa, mostrar_laudo=False)

# =============================================================================
# MÓDULO QUESTIONÁRIO PSICOSSOCIAL
# =============================================================================
elif menu == "📋 Questionário Psicossocial":
    if 'passo' not in st.session_state:
        st.session_state.passo = "login"

    # ── TELA DE LOGIN ─────────────────────────────────────────────────────────
    if st.session_state.passo == "login":

        # Detecta CNPJ via query param (link individualizado)
        params    = st.query_params
        cnpj_link = params.get("cnpj", "")

        st.markdown("""
            <div class="hero-sstg">
                <h1>DRE - DRPS</h1>
                <p>Questionário Psicossocial (DRPS) — Protocolo COPSOQ III<br>Diagnóstico do Ambiente de Trabalho mensurado com a Escala de Avaliação (Likert)</p>
                <p class="hero-nr">Em atendimento à NR-01</p>
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
            df_link = db.carregar_acessos()
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

        # ── Acesso livre para Admin master (pré-visualização, sem salvar) ──────
        if st.session_state.get('admin_logado') and st.session_state.get('admin_perfil') == 'admin':
            with st.expander("🔓 Acesso Admin Master — Pré-visualizar Questionário"):
                df_acessos_prev = db.carregar_acessos()
                if not df_acessos_prev.empty:
                    opcoes_prev = {
                        f"{row['Empresa']} — {row.get('Função','')} — CPF: {row['CPF']}": row.to_dict()
                        for _, row in df_acessos_prev.iterrows()
                    }
                    sel_prev = st.selectbox("Colaborador:", list(opcoes_prev.keys()), key="psico_admin_prev_sel")
                    if st.button("🔓 Pré-visualizar como Admin", use_container_width=True, key="psico_admin_prev_btn"):
                        st.session_state.dados_sessao = opcoes_prev[sel_prev]
                        st.session_state._admin_preview = True
                        st.session_state.passo = "quest"
                        st.rerun()

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
                df_auth = db.carregar_acessos()
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
                    dados_salvar["CNPJ"] = dados_s['CNPJ']
                    if not st.session_state.get('_admin_preview'):
                        db.salvar_resposta(dados_salvar)
                    # Guarda médias no session_state para exibir na tela final
                    st.session_state.medias_fim = {
                        k: v for k, v in dados_salvar.items()
                        if k.startswith("Media_") and k != "Media_Geral"
                    }
                    st.session_state.media_geral_fim = dados_salvar.get("Media_Geral", 0)
                    # Limpa estado do wizard
                    st.session_state.dominio_atual = 0
                    st.session_state.respostas_salvas = {}
                    st.session_state.passo = "fim"
                    st.rerun()

    # ── TELA FINAL ────────────────────────────────────────────────────────────
    elif st.session_state.passo == "fim":
        if st.session_state.get('_admin_preview'):
            st.info("🔓 Pré-visualização do Admin Master — esta resposta NÃO foi salva no banco de dados.")
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

        # ── Exibe médias por dimensão ─────────────────────────────────────────
        medias_fim = st.session_state.get("medias_fim", {})
        if medias_fim:
            st.divider()
            st.subheader("📊 Seu perfil por dimensão")
            st.caption("Escala de 0 a 4  ·  valores mais altos = condição mais favorável (exceto dimensões de risco, já ajustadas)")
            # Obtém a ordem das dimensões conforme DIMENSOES
            nomes_dim_ord = list(DIMENSOES.keys())
            def _col_da_dim(nome_dim):
                return "Media_" + nome_dim.split(" ", 1)[1].replace("/", "_").replace(" ", "_")
            colunas_ord = [_col_da_dim(nd) for nd in nomes_dim_ord if _col_da_dim(nd) in medias_fim]
            n = len(colunas_ord)
            cols_fim = st.columns(min(n, 4))
            for i, col_nome in enumerate(colunas_ord):
                val = medias_fim[col_nome]
                nome_dim_orig = nomes_dim_ord[[_col_da_dim(nd) for nd in nomes_dim_ord].index(col_nome)]
                label = nome_dim_orig.split(" ", 1)[1] if " " in nome_dim_orig else nome_dim_orig
                # Inverte dimensões de risco para exibição (maior = melhor)
                nome_chave = col_nome.replace("Media_", "").lower()
                val_exib = round(4.0 - val, 2) if nome_chave in _DIMS_INV_LOWER else val
                if val_exib >= 3.0:
                    delta_txt = "🟢 Favorável"
                elif val_exib >= 2.0:
                    delta_txt = "🟡 Moderado"
                else:
                    delta_txt = "🔴 Atenção"
                cols_fim[i % 4].metric(label, f"{val_exib:.2f}", delta_txt)
            media_geral = st.session_state.get("media_geral_fim", None)
            if media_geral is not None:
                st.metric("**Média Geral**", f"{media_geral:.2f}")

        if st.button("🔄 Voltar ao Início", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# =============================================================================
# MÓDULO QUESTIONÁRIO ERGONÔMICO (AEP / NR-17)
# =============================================================================
else:
    if 'passo_aep' not in st.session_state:
        st.session_state.passo_aep = "login"

    # ── TELA DE LOGIN ─────────────────────────────────────────────────────────
    if st.session_state.passo_aep == "login":
        params    = st.query_params
        cnpj_link = params.get("cnpj", "")

        st.markdown("""
            <div class="hero-sstg">
                <h1>DRE - DRPS</h1>
                <p>Questionário Ergonômico (DRE) — Avaliação Ergonômica Preliminar<br>Sua percepção sobre postura, mobiliário, ambiente e organização do trabalho</p>
                <p class="hero-nr">Em atendimento à NR-17</p>
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
                        <div class="label">~8 minutos</div>
                    </div>
                    <div class="trust-badge">
                        <div class="icon">🦴</div>
                        <div class="label">NR-17 / PGR</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if cnpj_link:
            df_link = db.carregar_acessos()
            if not df_link.empty:
                emp_rows = df_link[df_link['CNPJ'] == cnpj_link]
                if not emp_rows.empty:
                    nome_emp_link = emp_rows.iloc[0]['Empresa']
                    st.info(f"🏢 Você está respondendo a Avaliação Ergonômica de: **{nome_emp_link}**")

        st.markdown("""
            <div class="mensagem-motivadora">
            <b>Participe da nossa avaliação ergonômica do posto de trabalho!</b><br>
            É rápida, totalmente anônima e essencial para identificarmos melhorias no seu ambiente de trabalho.<br><br>
            🔒 <b>100% Confidencial:</b> Suas respostas individuais são protegidas e nunca expostas.<br>
            ✨ <b>Foco na Verdade:</b> Responda com base no que realmente acontece no seu dia a dia.
            </div>
        """, unsafe_allow_html=True)

        # ── Acesso livre para Admin master (pré-visualização, sem salvar) ──────
        if st.session_state.get('admin_logado') and st.session_state.get('admin_perfil') == 'admin':
            with st.expander("🔓 Acesso Admin Master — Pré-visualizar Avaliação Ergonômica"):
                df_acessos_prev_aep = db.carregar_acessos()
                if not df_acessos_prev_aep.empty:
                    opcoes_prev_aep = {
                        f"{row['Empresa']} — {row.get('Função','')} — CPF: {row['CPF']}": row.to_dict()
                        for _, row in df_acessos_prev_aep.iterrows()
                    }
                    sel_prev_aep = st.selectbox("Colaborador:", list(opcoes_prev_aep.keys()), key="aep_admin_prev_sel")
                    if st.button("🔓 Pré-visualizar como Admin", use_container_width=True, key="aep_admin_prev_btn"):
                        st.session_state.dados_sessao_aep = opcoes_prev_aep[sel_prev_aep]
                        st.session_state._admin_preview = True
                        st.session_state.passo_aep = "quest"
                        st.rerun()

        col_cpf, col_btn = st.columns([3, 1])
        cpf_in_aep = col_cpf.text_input(
            "Digite seu CPF (somente os 11 números, sem pontos ou traços):",
            max_chars=11,
            placeholder="00000000000",
            key="cpf_in_aep"
        )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            acessar_aep = st.button("ACESSAR ▶", use_container_width=True, type="primary", key="btn_acessar_aep")

        if acessar_aep:
            cpf_limpo = cpf_in_aep.strip().replace(".", "").replace("-", "")
            if not validar_cpf_formato(cpf_limpo):
                st.error("⚠️ CPF inválido. Digite apenas os 11 números.")
            else:
                df_auth = db.carregar_acessos()
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
                            elif cpf_ja_respondeu_aep(dados['CNPJ'], cpf_limpo):
                                st.warning("⚠️ Você já participou desta avaliação ergonômica. Obrigado!")
                            else:
                                st.session_state.dados_sessao_aep = dados
                                st.session_state.passo_aep = "quest"
                                st.rerun()
                    else:
                        st.error("❌ CPF não autorizado. Procure o RH ou a equipe SSTG.")
                else:
                    st.error("Nenhuma empresa cadastrada no sistema. Contate a equipe SSTG.")

    # ── QUESTIONÁRIO AEP (página única) ───────────────────────────────────────
    elif st.session_state.passo_aep == "quest":
        dados_s  = st.session_state.dados_sessao_aep
        empresa  = dados_s['Empresa']
        funcao   = dados_s.get('Função', '')
        depto    = dados_s.get('Departamento', '')
        cpf_resp = dados_s['CPF']
        caption  = f"Organização: {empresa}"
        if funcao: caption += f"  |  Função: {funcao}"
        if depto:  caption += f"  |  Departamento: {depto}"

        st.title("🦴 Avaliação Ergonômica Preliminar (AEP)")
        st.caption(caption)
        st.caption("Como responder: ✓ **Sim** = acontece ou existe | ✗ **Não** = não acontece | **Parcial** = acontece às vezes ou em parte | **N/A** = não se aplica à sua função")
        st.divider()

        respostas_aep = {}
        for secao, perguntas in AEP_SECOES.items():
            st.markdown(f"### {secao}")
            for qid, dados_q in perguntas.items():
                chave = f"{cpf_resp}_aep_{qid}"
                val_salvo = st.session_state.get(chave)
                idx_inicial = AEP_OPCOES.index(val_salvo) if val_salvo in AEP_OPCOES else None
                resp = st.radio(f"**{dados_q['texto']}**", AEP_OPCOES, horizontal=True,
                                 key=chave, index=idx_inicial)
                respostas_aep[qid] = resp
            st.divider()

        st.markdown("### Relato do Trabalhador")
        relato_dor = st.text_area(
            "Você sente dor, desconforto ou cansaço no corpo durante ou após o trabalho? "
            "Se sim, descreva o local (costas, pescoço, ombro, braço, mão, perna...) e quando acontece.",
            key=f"{cpf_resp}_aep_relato_dor"
        )
        relato_sugestoes = st.text_area(
            "Você tem alguma outra observação ou sugestão de melhoria para o seu posto de trabalho?",
            key=f"{cpf_resp}_aep_relato_sugestoes"
        )

        st.divider()
        nao_resp = [qid for qid, val in respostas_aep.items() if val is None]
        total_q  = sum(len(p) for p in AEP_SECOES.values())
        st.progress((total_q - len(nao_resp)) / total_q,
                    text=f"Progresso: {total_q - len(nao_resp)} de {total_q} perguntas respondidas")

        if nao_resp:
            st.warning(f"⚠️ Responda as {len(nao_resp)} pergunta(s) pendente(s) para finalizar.")

        if st.button("✅ FINALIZAR E ENVIAR AVALIAÇÃO", use_container_width=True,
                      type="primary", disabled=bool(nao_resp)):
            dados_salvar = {
                "cpf_hash":            hash_cpf(cpf_resp),
                "cnpj":                dados_s['CNPJ'],
                "empresa":             empresa,
                "departamento":        depto,
                "funcao_posto":        funcao,
                "data":                date.today().isoformat(),
                "relato_dor":          relato_dor,
                "relato_sugestoes":    relato_sugestoes,
                "severidades":         AEP_SEVERIDADES_DEFAULT,
            }
            for qid in respostas_aep:
                dados_salvar[qid] = respostas_aep[qid]

            if not st.session_state.get('_admin_preview'):
                db.salvar_resposta_aep(dados_salvar)

            for secao in AEP_SECOES.values():
                for qid in secao:
                    st.session_state.pop(f"{cpf_resp}_aep_{qid}", None)
            st.session_state.passo_aep = "fim"
            st.rerun()

    # ── TELA FINAL ────────────────────────────────────────────────────────────
    elif st.session_state.passo_aep == "fim":
        if st.session_state.get('_admin_preview'):
            st.info("🔓 Pré-visualização do Admin Master — esta resposta NÃO foi salva no banco de dados.")
        st.title("✅ Avaliação Ergonômica Concluída!")
        st.balloons()
        st.success("Sua avaliação foi enviada com sucesso!")
        st.markdown("""
            <div class="mensagem-motivadora">
            <b>Muito obrigado pela sua participação!</b><br><br>
            Suas respostas contribuirão para a melhoria das condições ergonômicas do seu posto de trabalho.
            Os dados coletados serão analisados de forma <b>agregada e completamente anônima</b> pela equipe SSTG.
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Voltar ao Início", use_container_width=True, key="btn_voltar_aep"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


