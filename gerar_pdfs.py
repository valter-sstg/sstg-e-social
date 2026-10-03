#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerar PDFs a partir de Markdown - SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors

def markdown_para_pdf(md_file, pdf_file):
    """Converte Markdown simples para PDF usando ReportLab"""

    # Ler arquivo markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Criar documento PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)"
    )

    # Estilos customizados
    styles = getSampleStyleSheet()

    # Cores SSTG
    cor_navy = colors.HexColor("#282C5B")
    cor_verde = colors.HexColor("#5A9F62")
    cor_laranja = colors.HexColor("#DC3B24")

    # Criar estilos customizados
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

    # Processar linhas do markdown
    story = []
    linhas = conteudo.split('\n')
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        # Pular linhas vazias
        if not linha:
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        # H1 (# Titulo)
        if linha.startswith('# '):
            titulo = linha[2:].strip()
            story.append(Paragraph(titulo, style_h1))
            story.append(Spacer(1, 0.2*inch))
            i += 1
            continue

        # H2 (## Subtitulo)
        if linha.startswith('## '):
            subtitulo = linha[3:].strip()
            story.append(Paragraph(subtitulo, style_h2))
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        # H3 (### Subsubtitulo)
        if linha.startswith('### '):
            sub3 = linha[4:].strip()
            story.append(Paragraph(sub3, style_h3))
            story.append(Spacer(1, 0.08*inch))
            i += 1
            continue

        # Quebra de pagina (---)
        if linha.startswith('---'):
            story.append(PageBreak())
            i += 1
            continue

        # Links [texto](url) -> texto (url)
        texto_processado = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1 (\2)', linha)

        # Bold **texto** -> <b>texto</b>
        texto_processado = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', texto_processado)

        # Italico *texto* -> <i>texto</i>
        texto_processado = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'<i>\1</i>', texto_processado)

        # Code `texto` -> <font face="Courier" size="9">texto</font>
        texto_processado = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', texto_processado)

        # Bullet points (- item)
        if linha.startswith('- '):
            item = texto_processado[2:].strip()
            story.append(Paragraph(f"<bullet>•</bullet> {item}", style_normal))
            i += 1
            continue

        # Numbered list (1. item)
        if re.match(r'^\d+\.\s', linha):
            match = re.match(r'^(\d+)\.\s(.+)', linha)
            if match:
                num, item = match.groups()
                story.append(Paragraph(f"{num}. {item}", style_normal))
                i += 1
                continue

        # Texto normal
        if texto_processado:
            story.append(Paragraph(texto_processado, style_normal))

        i += 1

    # Gerar PDF
    try:
        doc.build(story)
        return True, f"PDF gerado: {pdf_file}"
    except Exception as e:
        return False, f"Erro ao gerar PDF: {str(e)}"

def main():
    """Funcao principal"""

    print("\n" + "=" * 70)
    print("  CONVERSOR MARKDOWN PARA PDF - SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)")
    print("=" * 70)

    dir_projeto = Path("C:\\Users\\valte\\Claude")

    arquivos = [
        ("README.md", "README.pdf"),
        ("TUTORIAL.md", "TUTORIAL.pdf"),
        ("GUIA_INSTALACAO.md", "GUIA_INSTALACAO.pdf"),
        ("GUIA_TECNICO.md", "GUIA_TECNICO.pdf"),
        ("CHECKLIST_LANCAMENTO.md", "CHECKLIST_LANCAMENTO.pdf")
    ]

    for md_file, pdf_file in arquivos:
        md_path = dir_projeto / md_file
        pdf_path = dir_projeto / pdf_file

        if not md_path.exists():
            print(f"\n[ERRO] Arquivo nao encontrado: {md_file}")
            continue

        print(f"\n[*] Processando: {md_file}")
        print(f"    Gerando: {pdf_file}")

        success, mensagem = markdown_para_pdf(str(md_path), str(pdf_path))

        if success:
            print(f"    [OK] {mensagem}")
            # Verificar tamanho
            tamanho_kb = pdf_path.stat().st_size / 1024
            print(f"    Tamanho: {tamanho_kb:.1f} KB")
        else:
            print(f"    [ERRO] {mensagem}")

    print("\n" + "=" * 70)
    print("  CONVERSAO CONCLUIDA")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
