#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador de Imagens para Compartilhamento - SSTG - DRPS v6.2"""

import io
import os
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────────────────────────────────────
# Localiza uma fonte TrueType disponível no sistema — roda UMA VEZ na importação
# ─────────────────────────────────────────────────────────────────────────────
def _encontrar_fonte_ttf() -> str | None:
    """
    Retorna o primeiro caminho de fonte TTF encontrado no sistema.
    Prioriza Arial (Windows) → DejaVu / Liberation (Linux) → Helvetica (macOS).
    Retorna None se nenhuma for encontrada (Pillow usará bitmap default).
    """
    windir = os.environ.get("WINDIR", "C:\\Windows")
    candidatos = [
        # Windows
        os.path.join(windir, "Fonts", "arial.ttf"),
        os.path.join(windir, "Fonts", "Arial.ttf"),
        os.path.join(windir, "Fonts", "calibri.ttf"),
        os.path.join(windir, "Fonts", "tahoma.ttf"),
        os.path.join(windir, "Fonts", "verdana.ttf"),
        # Windows — pasta de fontes do usuário (Windows 10+)
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts", "arial.ttf"),
        # Linux / Streamlit Cloud
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
    ]
    for caminho in candidatos:
        if caminho and os.path.isfile(caminho):
            return caminho
    return None


_FONTE_TTF = _encontrar_fonte_ttf()  # resolvido uma vez na importação


def _fonte(tamanho: int) -> ImageFont.ImageFont:
    """Carrega fonte TTF no tamanho pedido. Fallback: bitmap do Pillow."""
    if _FONTE_TTF:
        try:
            return ImageFont.truetype(_FONTE_TTF, tamanho)
        except Exception:
            pass
    # Pillow 10+ suporta size= em load_default
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


# ─────────────────────────────────────────────────────────────────────────────
# Função principal
# ─────────────────────────────────────────────────────────────────────────────
def gerar_imagem_compartilhamento_simples(empresa_nome: str, cnpj: str, app_url: str) -> io.BytesIO:
    """
    Gera imagem PNG de compartilhamento com QR Code.
    Layout: header navy · nome empresa grande · QR Code centralizado grande · rodapé.
    """

    # ── Constantes de layout ──────────────────────────────────────────────────
    LARGURA       = 1280
    MARGEM        = 50
    QR_TAMANHO    = 600          # 600 × 600 px  (~200 % do original de 200 px)
    ALTURA_HEADER = 120
    ALT_LINHA_EMP = 100          # altura de linha para fonte 80px
    ALT_RODAPE    = 60

    # ── Cores SSTG ────────────────────────────────────────────────────────────
    COR_NAVY    = (40, 44, 91)
    COR_VERDE   = (90, 159, 98)
    BRANCO      = (255, 255, 255)
    CINZA_CLARO = (190, 190, 190)
    CINZA_MED   = (130, 130, 130)

    # ── Fontes ────────────────────────────────────────────────────────────────
    f_header_sm  = _fonte(20)   # texto pequeno no header
    f_header_lg  = _fonte(46)   # título do header
    f_label      = _fonte(28)   # "Empresa:"
    f_empresa    = _fonte(80)   # nome da empresa — grande
    f_rodape     = _fonte(20)   # texto do rodapé

    # ── Helper: quebra texto em linhas que cabem na largura ───────────────────
    def quebrar_linhas(draw_ref, texto, fonte_ref, largura_max):
        palavras = texto.split()
        linhas, atual = [], ""
        for p in palavras:
            candidato = (atual + " " + p).strip()
            w = draw_ref.textbbox((0, 0), candidato, font=fonte_ref)[2]
            if w <= largura_max:
                atual = candidato
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        return linhas if linhas else [texto]

    # ── Pré-calcular linhas para determinar altura total ──────────────────────
    _tmp = Image.new("RGB", (LARGURA, 10))
    _drw = ImageDraw.Draw(_tmp)
    linhas_empresa   = quebrar_linhas(_drw, empresa_nome, f_empresa, LARGURA - 2 * MARGEM)
    bloco_empresa_h  = len(linhas_empresa) * ALT_LINHA_EMP

    # Posições verticais
    y_label   = ALTURA_HEADER + 30
    y_empresa = y_label + 44           # abaixo do label "Empresa:"
    y_qr      = y_empresa + bloco_empresa_h + 40
    ALTURA    = y_qr + QR_TAMANHO + 30 + ALT_RODAPE

    # ── Criar canvas ──────────────────────────────────────────────────────────
    img  = Image.new("RGB", (LARGURA, ALTURA), BRANCO)
    draw = ImageDraw.Draw(img)

    # Header navy
    draw.rectangle([(0, 0), (LARGURA, ALTURA_HEADER)], fill=COR_NAVY)
    draw.text((MARGEM, 16),
              "SSTG - DRPS  Diagnóstico de Riscos Psicossociais (NR-1)",
              fill=CINZA_CLARO, font=f_header_sm)
    draw.text((MARGEM, 50),
              "SSTG - DRPS  Diagnóstico de Riscos Psicossociais",
              fill=BRANCO, font=f_header_lg)

    # Label "Empresa:"
    draw.text((MARGEM, y_label), "Empresa:", fill=CINZA_MED, font=f_label)

    # Nome da empresa (multilinhas)
    y_cur = y_empresa
    for linha in linhas_empresa:
        draw.text((MARGEM, y_cur), linha, fill=COR_VERDE, font=f_empresa)
        y_cur += ALT_LINHA_EMP

    # ── QR Code ───────────────────────────────────────────────────────────────
    link = f"{app_url}/?cnpj={cnpj}"
    qr_obj = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr_obj.add_data(link)
    qr_obj.make(fit=True)
    qr_pil = qr_obj.make_image(fill_color=COR_NAVY, back_color=BRANCO)
    qr_pil = qr_pil.resize((QR_TAMANHO, QR_TAMANHO), Image.Resampling.LANCZOS)

    x_qr = (LARGURA - QR_TAMANHO) // 2   # centralizado
    img.paste(qr_pil, (x_qr, y_qr))

    # ── Rodapé ────────────────────────────────────────────────────────────────
    draw.rectangle([(0, ALTURA - ALT_RODAPE), (LARGURA, ALTURA)], fill=(235, 235, 235))
    txt_rodape = f"Imagem de compartilhamento: {empresa_nome}"
    bbox_r     = draw.textbbox((0, 0), txt_rodape, font=f_rodape)
    x_rod      = (LARGURA - (bbox_r[2] - bbox_r[0])) // 2
    draw.text((x_rod, ALTURA - ALT_RODAPE + 18), txt_rodape,
              fill=CINZA_MED, font=f_rodape)

    # ── Exportar ──────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# Função legada (mantida para compatibilidade)
# ─────────────────────────────────────────────────────────────────────────────
def gerar_imagem_compartilhamento(empresa_nome: str, cnpj: str, app_url: str) -> io.BytesIO:
    """Alias para gerar_imagem_compartilhamento_simples (compatibilidade)."""
    return gerar_imagem_compartilhamento_simples(empresa_nome, cnpj, app_url)
