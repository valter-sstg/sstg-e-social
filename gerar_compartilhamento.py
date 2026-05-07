#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador de Imagens para Compartilhamento - SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)"""

import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def gerar_imagem_compartilhamento(empresa_nome: str, cnpj: str, app_url: str) -> io.BytesIO:
    """
    Gera imagem de compartilhamento com QR Code e informações da empresa

    Args:
        empresa_nome: Nome da empresa
        cnpj: CNPJ da empresa
        app_url: URL base da aplicação

    Returns:
        BytesIO: Imagem em formato PNG
    """

    # Dimensões
    largura, altura = 1200, 800
    padding = 50

    # Cores SSTG
    cor_navy = (40, 44, 91)          # #282C5B
    cor_verde = (90, 159, 98)        # #5A9F62
    cor_laranja = (220, 59, 36)      # #DC3B24
    cor_fundo = (239, 239, 239)      # #EFEFEF
    branco = (255, 255, 255)
    cinza_escuro = (100, 100, 100)

    # Criar imagem
    img = Image.new('RGB', (largura, altura), cor_fundo)
    draw = ImageDraw.Draw(img)

    # Desenhar retângulo de cabeçalho com gradiente (simulado com retângulo)
    draw.rectangle(
        [(0, 0), (largura, 200)],
        fill=cor_navy
    )

    # Tentar carregar fontes com múltiplos caminhos
    def _fonte(tamanho):
        candidatos = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/Library/Fonts/Arial.ttf",
            "arial.ttf",
        ]
        for c in candidatos:
            try:
                return ImageFont.truetype(c, tamanho)
            except Exception:
                continue
        try:
            return ImageFont.load_default(size=tamanho)
        except TypeError:
            return ImageFont.load_default()

    fonte_titulo    = _fonte(48)
    fonte_subtitulo = _fonte(32)
    fonte_normal    = _fonte(24)
    fonte_pequena   = _fonte(20)

    # Título: "SSTG E-SOCIAL"
    titulo = "SSTG E-SOCIAL"
    bbox = draw.textbbox((0, 0), titulo, font=fonte_titulo)
    titulo_largura = bbox[2] - bbox[0]
    x_titulo = (largura - titulo_largura) // 2
    draw.text((x_titulo, 40), titulo, fill=branco, font=fonte_titulo)

    # Subtítulo: "Avaliação de Riscos Psicossociais"
    subtitulo = "Avaliação de Riscos Psicossociais"
    bbox = draw.textbbox((0, 0), subtitulo, font=fonte_subtitulo)
    sub_largura = bbox[2] - bbox[0]
    x_sub = (largura - sub_largura) // 2
    draw.text((x_sub, 100), subtitulo, fill=cor_verde, font=fonte_subtitulo)

    # Seção de conteúdo
    y_conteudo = 250

    # Nome da empresa
    texto_empresa = f"Empresa: {empresa_nome}"
    draw.text((padding, y_conteudo), texto_empresa, fill=cor_navy, font=fonte_normal)

    y_conteudo += 70

    # Informações
    info_text = "⏱️ ~10 minutos   🔒 100% Confidencial   ✓ Validado"
    draw.text((padding, y_conteudo), info_text, fill=cinza_escuro, font=fonte_pequena)

    y_conteudo += 80

    # Gerar QR Code
    link = f"{app_url}/?cnpj={cnpj}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(link)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=cor_navy, back_color=branco)
    qr_tamanho = 200
    qr_img = qr_img.resize((qr_tamanho, qr_tamanho), Image.Resampling.LANCZOS)

    # Posicionar QR Code à esquerda
    x_qr = padding + 50
    img.paste(qr_img, (x_qr, y_conteudo))

    # Link ao lado do QR Code
    x_link = x_qr + qr_tamanho + 60
    y_link = y_conteudo + 30

    draw.text((x_link, y_link), "Escaneie o código QR", fill=cor_navy, font=fonte_normal)
    y_link += 50
    draw.text((x_link, y_link), "ou acesse:", fill=cinza_escuro, font=fonte_pequena)

    # Link em formato reduzido (com cor destaque)
    y_link += 50
    link_display = link.replace('https://', '').replace('http://', '')
    if len(link_display) > 40:
        link_display = link_display[:37] + "..."
    draw.text((x_link, y_link), link_display, fill=cor_laranja, font=fonte_pequena)

    # Rodapé com call to action
    y_rodape = altura - 80
    draw.rectangle([(0, y_rodape), (largura, altura)], fill=cor_navy)

    cta = "Clique no QR Code ou acesse o link para participar da pesquisa"
    bbox = draw.textbbox((0, 0), cta, font=fonte_normal)
    cta_largura = bbox[2] - bbox[0]
    x_cta = (largura - cta_largura) // 2
    draw.text((x_cta, y_rodape + 15), cta, fill=branco, font=fonte_normal)

    # Converter para BytesIO
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    return img_io


def gerar_imagem_compartilhamento_simples(empresa_nome: str, cnpj: str, app_url: str) -> io.BytesIO:
    """
    Versão simplificada otimizada para Streamlit Cloud
    Gera imagem de compartilhamento com QR Code
    """

    # Dimensões base — altura calculada dinamicamente abaixo
    largura = 1280
    margem  = 40

    # Cores SSTG
    cor_navy   = (40, 44, 91)
    cor_verde  = (90, 159, 98)
    branco     = (255, 255, 255)
    cinza_claro = (180, 180, 180)
    cinza_medio = (150, 150, 150)

    # ── Fontes ────────────────────────────────────────────────────────────────
    def fonte(tamanho):
        # Lista de caminhos a tentar, do mais específico ao mais genérico
        candidatos = [
            # Windows — caminhos absolutos
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            # Linux (Streamlit Cloud / Ubuntu)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            # macOS
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            # Relativo (funciona às vezes se o CWD contiver a fonte)
            "arial.ttf",
        ]
        for caminho_fonte in candidatos:
            try:
                return ImageFont.truetype(caminho_fonte, tamanho)
            except Exception:
                continue
        # Último recurso: fonte bitmap do Pillow (tamanho fixo ~10px)
        # Usamos FreeType embutido se disponível
        try:
            import importlib.resources
            return ImageFont.load_default(size=tamanho)
        except TypeError:
            return ImageFont.load_default()

    fonte_pequena  = fonte(18)
    fonte_titulo   = fonte(48)   # header — reduzido para caber na largura
    fonte_subtitulo = fonte(18)
    fonte_label    = fonte(20)
    fonte_empresa  = fonte(72)   # nome da empresa — conforme solicitado
    fonte_rodape   = fonte(18)

    # ── Helper: quebra texto em linhas que cabem na largura máxima ────────────
    def quebrar_linhas(draw, texto, fonte, largura_max):
        palavras = texto.split()
        linhas, atual = [], ""
        for p in palavras:
            candidato = (atual + " " + p).strip()
            w = draw.textbbox((0, 0), candidato, font=fonte)[2]
            if w <= largura_max:
                atual = candidato
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        return linhas

    # ── Pré-calcular linhas do nome da empresa para saber a altura necessária ─
    # Usamos um canvas temporário apenas para medir
    _tmp_img  = Image.new('RGB', (largura, 10))
    _tmp_draw = ImageDraw.Draw(_tmp_img)
    linhas_empresa = quebrar_linhas(_tmp_draw, empresa_nome,
                                    fonte_empresa, largura - 2 * margem)
    altura_linha_empresa = 88   # ~72pt + entrelinha
    altura_bloco_empresa = len(linhas_empresa) * altura_linha_empresa

    # ── Layout vertical ───────────────────────────────────────────────────────
    altura_header = 130
    y_label       = altura_header + 25
    y_empresa     = y_label + 30
    y_qr          = y_empresa + altura_bloco_empresa + 30
    qr_tamanho    = 500         # aumentado 150 % (200 → 500 px)
    altura_rodape = 55
    altura        = y_qr + qr_tamanho + 30 + altura_rodape

    # ── Criar imagem com altura calculada ─────────────────────────────────────
    img  = Image.new('RGB', (largura, altura), branco)
    draw = ImageDraw.Draw(img)

    # Header navy
    draw.rectangle([(0, 0), (largura, altura_header)], fill=cor_navy)

    # Texto pequeno topo
    draw.text((margem, 14),
              "SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)",
              fill=cinza_claro, font=fonte_subtitulo)

    # Título principal no header
    draw.text((margem, 55),
              "SSTG - DRPS Diagnóstico de Riscos Psicossociais",
              fill=branco, font=fonte_titulo)

    # Label "Empresa:"
    draw.text((margem, y_label), "Empresa:", fill=cinza_medio, font=fonte_label)

    # Nome da empresa (multilinhas se necessário)
    y_cur = y_empresa
    for linha in linhas_empresa:
        draw.text((margem, y_cur), linha, fill=cor_verde, font=fonte_empresa)
        y_cur += altura_linha_empresa

    # QR Code
    link   = f"{app_url}/?cnpj={cnpj}"
    qr_obj = qrcode.QRCode(version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_H,
                            box_size=8, border=2)
    qr_obj.add_data(link)
    qr_obj.make(fit=True)
    qr_img = qr_obj.make_image(fill_color=cor_navy, back_color=branco)
    qr_img = qr_img.resize((qr_tamanho, qr_tamanho), Image.Resampling.LANCZOS)

    x_qr = (largura - qr_tamanho) // 2
    img.paste(qr_img, (x_qr, y_qr))

    # Rodapé
    draw.rectangle([(0, altura - altura_rodape), (largura, altura)],
                   fill=(240, 240, 240))
    texto_rodape = f"Imagem de compartilhamento: {empresa_nome}"
    bbox_r = draw.textbbox((0, 0), texto_rodape, font=fonte_rodape)
    x_rodape = (largura - (bbox_r[2] - bbox_r[0])) // 2
    draw.text((x_rodape, altura - 38), texto_rodape,
              fill=cinza_medio, font=fonte_rodape)

    # Converter para BytesIO
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    return img_io
