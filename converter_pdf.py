#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converter Markdown para PDF - SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)"""

import subprocess
import os
import sys
from pathlib import Path

def converter_com_pandoc(md_file, pdf_file):
    """Converte usando Pandoc (melhor resultado)"""
    try:
        cmd = [
            'pandoc',
            md_file,
            '-o', pdf_file,
            '--pdf-engine=wkhtmltopdf',
            '-V', 'geometry:margin=1in',
            '--standalone',
            '--toc',
            '--toc-depth=2'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"✅ {pdf_file} gerado com sucesso (Pandoc)"
        else:
            return False, f"Erro Pandoc: {result.stderr}"
    except FileNotFoundError:
        return False, "Pandoc não instalado"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def converter_com_markdown2pdf(md_file, pdf_file):
    """Converte usando markdown2pdf"""
    try:
        from markdown2pdf.markdown2pdf import convert
        convert(md_file, pdf_file)
        return True, f"✅ {pdf_file} gerado com sucesso (markdown2pdf)"
    except Exception as e:
        return False, f"Erro markdown2pdf: {str(e)}"

def converter_com_weasyprint(md_file, pdf_file):
    """Converte usando WeasyPrint (alternativa)"""
    try:
        import markdown
        from weasyprint import HTML, CSS
        from io import StringIO

        # Ler markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Converter para HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'toc', 'codehilite'])

        # Adicionar CSS
        html_full = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                h1 {{ color: #282C5B; border-bottom: 3px solid #282C5B; padding-bottom: 10px; }}
                h2 {{ color: #5A9F62; margin-top: 30px; }}
                h3 {{ color: #333; margin-top: 20px; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background: #f4f4f4; padding: 15px; border-left: 4px solid #DC3B24; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #282C5B; color: white; }}
                a {{ color: #DC3B24; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Gerar PDF
        HTML(string=html_full).write_pdf(pdf_file)
        return True, f"✅ {pdf_file} gerado com sucesso (WeasyPrint)"
    except Exception as e:
        return False, f"Erro WeasyPrint: {str(e)}"

def main():
    """Função principal"""
    dir_projeto = Path("C:\\Users\\valte\\Claude")

    arquivos = [
        ("README.md", "README.pdf"),
        ("TUTORIAL.md", "TUTORIAL.pdf")
    ]

    print("=" * 60)
    print("[*] Convertendo Markdown para PDF")
    print("=" * 60)

    for md_file, pdf_file in arquivos:
        md_path = dir_projeto / md_file
        pdf_path = dir_projeto / pdf_file

        if not md_path.exists():
            print(f"\n[ERRO] Arquivo nao encontrado: {md_file}")
            continue

        print(f"\n[*] Convertendo: {md_file}")
        print(f"    -> {pdf_file}")

        # Tentar diferentes métodos
        success, msg = converter_com_weasyprint(str(md_path), str(pdf_path))

        if success:
            print(f"    {msg}")
        else:
            print(f"    [!] {msg}")
            print(f"    Tentando markdown2pdf...")
            success, msg = converter_com_markdown2pdf(str(md_path), str(pdf_path))
            if success:
                print(f"    {msg}")
            else:
                print(f"    [ERRO] Falha: {msg}")

    print("\n" + "=" * 60)
    print("[OK] Processo concluido!")
    print("=" * 60)

if __name__ == "__main__":
    main()
