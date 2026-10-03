#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerar PDF da Documentação de Publicação"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors

def markdown_para_pdf(md_file, pdf_file):
    """Converte Markdown para PDF usando ReportLab"""

    with open(md_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1) - Documentação de Publicação"
    )

    styles = getSampleStyleSheet()
    cor_navy = colors.HexColor("#282C5B")
    cor_verde = colors.HexColor("#5A9F62")
    cor_laranja = colors.HexColor("#DC3B24")

    style_h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=cor_navy,
        spaceAfter=12,
        spaceBefore=12,
        borderBottom=2,
        borderColor=cor_navy,
        borderPadding=5
    )

    style_h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=cor_verde,
        spaceAfter=10,
        spaceBefore=10
    )

    style_h3 = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=cor_laranja,
        spaceAfter=8,
        spaceBefore=8
    )

    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    )

    story = []
    linhas = conteudo.split('\n')
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        if not linha:
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        if linha.startswith('# '):
            titulo = linha[2:].strip()
            story.append(Paragraph(titulo, style_h1))
            story.append(Spacer(1, 0.2*inch))
            i += 1
            continue

        if linha.startswith('## '):
            subtitulo = linha[3:].strip()
            story.append(Paragraph(subtitulo, style_h2))
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        if linha.startswith('### '):
            sub3 = linha[4:].strip()
            story.append(Paragraph(sub3, style_h3))
            story.append(Spacer(1, 0.08*inch))
            i += 1
            continue

        if linha.startswith('---'):
            story.append(PageBreak())
            i += 1
            continue

        texto_processado = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1 (\2)', linha)
        texto_processado = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', texto_processado)
        texto_processado = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'<i>\1</i>', texto_processado)
        texto_processado = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', texto_processado)

        if linha.startswith('- '):
            item = texto_processado[2:].strip()
            story.append(Paragraph(f"<bullet>•</bullet> {item}", style_normal))
            i += 1
            continue

        if re.match(r'^\d+\.\s', linha):
            match = re.match(r'^(\d+)\.\s(.+)', linha)
            if match:
                num, item = match.groups()
                story.append(Paragraph(f"{num}. {item}", style_normal))
                i += 1
                continue

        if texto_processado:
            story.append(Paragraph(texto_processado, style_normal))

        i += 1

    try:
        doc.build(story)
        return True, f"PDF gerado: {pdf_file}"
    except Exception as e:
        return False, f"Erro ao gerar PDF: {str(e)}"

# Executar
if __name__ == "__main__":
    dir_projeto = Path("G:\\Meu Drive\\SSTG-E-Social")

    md_path = dir_projeto / "DOCUMENTACAO_PUBLICACAO.md"
    pdf_path = dir_projeto / "DOCUMENTACAO_PUBLICACAO.pdf"

    print("\n" + "=" * 70)
    print("  CONVERTENDO DOCUMENTAÇÃO DE PUBLICAÇÃO PARA PDF")
    print("=" * 70)

    if not md_path.exists():
        print(f"\n[ERRO] Arquivo não encontrado: {md_path}")
    else:
        print(f"\n[*] Processando: {md_path.name}")
        success, mensagem = markdown_para_pdf(str(md_path), str(pdf_path))

        if success:
            print(f"    [OK] {mensagem}")
            tamanho_kb = pdf_path.stat().st_size / 1024
            print(f"    Tamanho: {tamanho_kb:.1f} KB")
        else:
            print(f"    [ERRO] {mensagem}")

    print("\n" + "=" * 70)
    print("  CONVERSÃO CONCLUIDA")
    print("=" * 70 + "\n")
