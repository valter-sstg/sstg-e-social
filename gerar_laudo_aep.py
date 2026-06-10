from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image
)
from datetime import datetime
import io
import os

from gerar_laudo import (
    C_AZUL, C_VERDE, C_LARANJA, C_AMARELO, C_CINZA, C_CINZAC, C_BRANCO,
    RESP_NOME, RESP_MTE, RESP_CREA,
    get_styles, _titulo_secao, _subtitulo, _tabela_dados, _chip,
)

# ===================== AÇÕES POR CLASSIFICAÇÃO (NR-17 / NR-01) =====================
ACAO_POR_CLASSIFICACAO = {
    "Crítico":  ("Intervenção imediata. Paralisação da atividade se necessário. "
                  "Comunicar CIPA e médico do trabalho.", colors.HexColor('#C0392B')),
    "Alto":     ("Controle imediato. Medidas de engenharia e/ou administrativas em até 30 dias.",
                  C_LARANJA),
    "Médio":    ("Elaborar plano de ação com prazo de até 90 dias. Incluir no PGR.",
                  C_AMARELO),
    "Baixo":    ("Monitoramento periódico semestral. Sem necessidade de intervenção imediata.",
                  C_VERDE),
}


def _header_footer_aep(canvas_obj, doc, empresa=""):
    canvas_obj.saveState()
    w, h = A4

    canvas_obj.setFillColor(C_AZUL)
    canvas_obj.rect(0, h - 1.4*cm, w, 1.4*cm, fill=1, stroke=0)
    canvas_obj.setFillColor(C_BRANCO)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawString(1*cm, h - 0.85*cm, "PGR / LAUDO — AVALIAÇÃO ERGONÔMICA PRELIMINAR (AEP)")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(w - 1*cm, h - 0.85*cm, f"Pág. {doc.page}")

    canvas_obj.setFillColor(C_VERDE)
    canvas_obj.rect(0, h - 1.55*cm, w, 0.15*cm, fill=1, stroke=0)

    canvas_obj.setFillColor(C_AZUL)
    canvas_obj.rect(0, 0, w, 0.75*cm, fill=1, stroke=0)
    canvas_obj.setFillColor(C_BRANCO)
    canvas_obj.setFont("Helvetica", 6.5)
    canvas_obj.drawCentredString(w / 2, 0.22*cm,
        f"SSTG E-Social — Gestão Ocupacional  |  Laudo AEP — NR-17  |  {empresa}  |  Documento Confidencial")

    canvas_obj.restoreState()


# ===================== SEÇÃO 1: CAPA / IDENTIFICAÇÃO =====================

def build_capa_aep(st, empresa, cnpj, data_emissao, logo_path):
    elementos = []

    logo_cell = ""
    if logo_path and os.path.exists(logo_path):
        logo_cell = Image(logo_path, width=4.5*cm, height=2.2*cm, kind='proportional')

    hero_data = [[
        logo_cell,
        [
            Paragraph("Laudo de Avaliação Ergonômica Preliminar (AEP)", st['titulo_capa']),
            Paragraph("Anexo do Programa de Gerenciamento de Riscos — PGR", st['subtitulo_capa']),
        ]
    ]]
    hero = Table(hero_data, colWidths=[5.5*cm, 13*cm])
    hero.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_AZUL),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 20),
        ('RIGHTPADDING', (1, 0), (1, 0), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elementos.append(hero)

    faixa = Table([[Paragraph("NR-17 — Ergonomia  |  NR-01 — Gerenciamento de Riscos Ocupacionais",
        ParagraphStyle('nr', fontName='Helvetica-Bold', fontSize=11,
                       textColor=C_BRANCO, alignment=TA_CENTER))]],
        colWidths=[18.5*cm])
    faixa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LARANJA),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(faixa)
    elementos.append(Spacer(1, 0.5*cm))

    elementos.append(_titulo_secao("1. Identificação", st))
    elementos.append(_tabela_dados([
        ("Razão Social:", empresa),
        ("CNPJ:", cnpj),
        ("Data de Emissão:", data_emissao),
        ("Norma de Referência:", "NR-17 (Portaria MTE 1.117/2023) e NR-01 (Portaria MTE 672/2021)"),
        ("Responsável Técnico:", RESP_NOME),
        ("MTE:", RESP_MTE),
        ("CREA:", RESP_CREA),
    ]))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(Paragraph(
        "Este documento apresenta os resultados da Avaliação Ergonômica Preliminar (AEP), aplicada por meio de "
        "questionário eletrônico anônimo aos colaboradores, conforme metodologia de Inventário de Riscos "
        "Ergonômicos baseada na Matriz Severidade × Probabilidade (NR-17 / NR-01).", st['body']))

    return elementos


# ===================== SEÇÃO 2: METODOLOGIA =====================

def build_metodologia_aep(st, total_respondentes, total_autorizados):
    el = []
    el.append(_titulo_secao("2. Metodologia de Avaliação", st))

    pct = round((total_respondentes / total_autorizados) * 100, 1) if total_autorizados else 0
    el.append(_subtitulo("2.1. Participação", st))
    el.append(_tabela_dados([
        ("Colaboradores Autorizados:", total_autorizados),
        ("Respostas Recebidas:", total_respondentes),
        ("Taxa de Adesão:", f"{pct}%"),
    ]))

    el.append(_subtitulo("2.2. Critério de Pontuação", st))
    el.append(Paragraph(
        "O questionário aplicado contém 17 perguntas distribuídas em 4 seções: A) Postura e Movimentos, "
        "B) Mobiliário e Equipamentos, C) Condições Ambientais e D) Organização do Trabalho. "
        "Cada resposta foi classificada como indicadora de risco (“Sim” nas perguntas diretas ou "
        "“Não” nas perguntas invertidas), parcialmente de risco (“Parcial”) ou sem risco. "
        "O percentual de respostas indicadoras de risco para cada pergunta determina a Probabilidade (1 a 4).",
        st['body']))

    el.append(_subtitulo("2.3. Escala de Probabilidade", st))
    dados_prob = [["Nível", "Classificação", "% de respostas de risco"]]
    dados_prob += [
        ["1", "Improvável", "< 10%"],
        ["2", "Possível", "10% — 30%"],
        ["3", "Provável", "30% — 70%"],
        ["4", "Muito Provável", "> 70%"],
    ]
    t = Table(dados_prob, colWidths=[2.5*cm, 6*cm, 10*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), C_BRANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_BRANCO, C_CINZAC]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    el.append(t)
    el.append(Spacer(1, 0.2*cm))

    el.append(_subtitulo("2.4. Grau de Risco (GR = Severidade × Probabilidade)", st))
    el.append(Paragraph(
        "A Severidade (1=Leve, 2=Moderada, 3=Grave, 4=Crítica) é definida pelo avaliador com base no potencial "
        "de dano à saúde de cada fator de risco ergonômico. O Grau de Risco resulta da multiplicação entre "
        "Severidade e Probabilidade, sendo classificado conforme a tabela abaixo:", st['body']))

    dados_gr = [["Faixa de GR", "Classificação", "Ação Recomendada"]]
    for classif, (acao, _cor) in ACAO_POR_CLASSIFICACAO.items():
        faixa = {"Crítico": "10 — 16", "Alto": "7 — 9", "Médio": "3 — 6", "Baixo": "1 — 2"}[classif]
        dados_gr.append([faixa, classif, acao])
    t2 = Table(dados_gr, colWidths=[2.5*cm, 3*cm, 13*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), C_BRANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_BRANCO, C_CINZAC]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    el.append(t2)
    return el


# ===================== SEÇÃO 3: INVENTÁRIO DE RISCOS =====================

def build_inventario_aep(st, inventario):
    el = []
    el.append(_titulo_secao("3. Inventário de Riscos Ergonômicos", st))
    el.append(Paragraph(
        "A tabela a seguir consolida, para cada fator de risco avaliado, o percentual de respostas que "
        "indicaram a presença do risco, a Severidade, a Probabilidade e o Grau de Risco (GR) resultante.",
        st['body']))
    el.append(Spacer(1, 0.15*cm))

    cab = ["Nº", "Risco Identificado", "% Risco", "Sev.", "Prob.", "GR", "Classificação"]
    dados = [cab]
    cores_linhas = []
    for item in inventario:
        dados.append([
            str(item["Nº"]),
            Paragraph(item["Risco Identificado"], st['table_cell']),
            f"{item['% Risco']:.1f}%",
            str(item["Severidade"]),
            str(item["Probabilidade"]),
            str(item["GR"]),
            item["Classificação"],
        ])
        cores_linhas.append(colors.HexColor(item["Cor"]))

    t = Table(dados, colWidths=[1*cm, 8.5*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.3*cm, 3.4*cm], repeatRows=1)
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), C_AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), C_BRANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    for i, cor in enumerate(cores_linhas, start=1):
        estilo.append(('BACKGROUND', (-1, i), (-1, i), cor))
        estilo.append(('TEXTCOLOR', (-1, i), (-1, i), C_BRANCO))
        estilo.append(('FONTNAME', (-1, i), (-1, i), 'Helvetica-Bold'))
    t.setStyle(TableStyle(estilo))
    el.append(t)
    return el


# ===================== SEÇÃO 4: MATRIZ CONSOLIDADA E PLANO DE AÇÃO =====================

def build_plano_acao_aep(st, inventario):
    el = []
    el.append(_titulo_secao("4. Matriz Consolidada e Plano de Ação", st))

    contagem = {"Crítico": 0, "Alto": 0, "Médio": 0, "Baixo": 0}
    for item in inventario:
        contagem[item["Classificação"]] += 1

    el.append(_subtitulo("4.1. Distribuição dos Riscos por Classificação", st))
    linha_chips = []
    for classif, qtd in contagem.items():
        _, cor = ACAO_POR_CLASSIFICACAO[classif]
        linha_chips.append(_chip(f"{classif}: {qtd}", cor))
    chips_table = Table([linha_chips], colWidths=[4.6*cm]*4)
    chips_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    el.append(chips_table)
    el.append(Spacer(1, 0.3*cm))

    el.append(_subtitulo("4.2. Plano de Ação — Riscos Médio, Alto e Crítico", st))
    riscos_relevantes = [it for it in inventario if it["Classificação"] != "Baixo"]
    if not riscos_relevantes:
        el.append(Paragraph("Nenhum risco classificado como Médio, Alto ou Crítico foi identificado nesta avaliação.", st['body']))
    else:
        riscos_relevantes = sorted(riscos_relevantes, key=lambda x: x["GR"], reverse=True)
        cab = ["Risco Identificado", "GR", "Classif.", "Medida de Controle Recomendada", "Prazo"]
        dados = [cab]
        cores_linhas = []
        for item in riscos_relevantes:
            acao, cor = ACAO_POR_CLASSIFICACAO[item["Classificação"]]
            prazo = {"Crítico": "Imediato", "Alto": "30 dias", "Médio": "90 dias"}[item["Classificação"]]
            dados.append([
                Paragraph(item["Risco Identificado"], st['table_cell']),
                str(item["GR"]),
                item["Classificação"],
                Paragraph(acao, st['table_cell']),
                prazo,
            ])
            cores_linhas.append(colors.HexColor(item["Cor"]))
        t = Table(dados, colWidths=[5.5*cm, 1.3*cm, 2.2*cm, 7.5*cm, 2*cm], repeatRows=1)
        estilo = [
            ('BACKGROUND', (0, 0), (-1, 0), C_AZUL),
            ('TEXTCOLOR', (0, 0), (-1, 0), C_BRANCO),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        for i, cor in enumerate(cores_linhas, start=1):
            estilo.append(('BACKGROUND', (2, i), (2, i), cor))
            estilo.append(('TEXTCOLOR', (2, i), (2, i), C_BRANCO))
            estilo.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
        t.setStyle(TableStyle(estilo))
        el.append(t)

    el.append(Spacer(1, 0.2*cm))
    el.append(Paragraph(
        "As medidas de controle devem seguir a hierarquia de prevenção: Eliminação → Substituição → "
        "Controles de Engenharia → Controles Administrativos → Equipamento de Proteção Individual (EPI). "
        "Riscos classificados como Alto ou Crítico devem ser registrados no PGR da empresa e comunicados "
        "ao SESMT ou ao médico coordenador do PCMSO.", st['body']))
    return el


# ===================== SEÇÃO 5: RELATOS E CONCLUSÃO =====================

def build_conclusao_aep(st, empresa, relatos):
    el = []
    el.append(_titulo_secao("5. Relatos dos Trabalhadores e Conclusão", st))

    el.append(_subtitulo("5.1. Relatos Coletados (Seção 3 do Questionário)", st))
    relatos_validos = [r.strip() for r in relatos if r and r.strip()]
    if relatos_validos:
        for relato in relatos_validos[:30]:
            el.append(Paragraph(f"• {relato}", st['lista']))
    else:
        el.append(Paragraph("Nenhum relato adicional foi registrado pelos respondentes.", st['body']))

    el.append(Spacer(1, 0.2*cm))
    el.append(_subtitulo("5.2. Conclusão", st))
    el.append(Paragraph(
        f"A presente Avaliação Ergonômica Preliminar (AEP) da empresa <b>{empresa}</b> identificou os fatores "
        "de risco ergonômicos descritos no Inventário de Riscos (Seção 3), classificados conforme a Matriz "
        "Severidade × Probabilidade (Seção 4). Recomenda-se a implementação do Plano de Ação proposto, "
        "priorizando os riscos classificados como Alto e Crítico, e a revisão periódica deste inventário "
        "após qualquer alteração de processo, layout, equipamento ou força de trabalho, e no mínimo a cada "
        "2 anos, conforme NR-01.", st['body']))

    el.append(Spacer(1, 1*cm))
    el.append(HRFlowable(width="40%", thickness=0.8, color=C_CINZA))
    el.append(Paragraph(RESP_NOME, st['body_bold']))
    el.append(Paragraph(f"Engenheiro de Segurança do Trabalho — MTE {RESP_MTE} / CREA {RESP_CREA}", st['body']))
    return el


# ===================== FUNÇÃO PRINCIPAL =====================

def gerar_laudo_aep_pdf(
    dados_empresa: dict,
    inventario: list,
    total_respondentes: int,
    total_autorizados: int,
    relatos: list = None,
    logo_path: str = "logo_sstg.png",
) -> bytes:
    """
    Gera o Laudo de Avaliação Ergonômica Preliminar (AEP / NR-17) em PDF e retorna os bytes.

    dados_empresa: dict com chaves 'Empresa', 'CNPJ'
    inventario: lista de dicts retornada por _calcular_inventario_aep (app_cloud.py)
    total_respondentes / total_autorizados: contagens para cálculo de adesão
    relatos: lista de strings com os relatos abertos dos trabalhadores
    """
    buffer = io.BytesIO()
    empresa = dados_empresa.get("Empresa", "—")
    cnpj    = dados_empresa.get("CNPJ", "—")
    data_emissao = datetime.now().strftime("%d/%m/%Y")
    relatos = relatos or []

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2.2*cm,
        bottomMargin=1.5*cm,
        title=f"Laudo AEP — {empresa}",
        author=RESP_NOME,
        subject="Laudo de Avaliação Ergonômica Preliminar — NR-17",
    )

    st = get_styles()

    def _callback(canvas_obj, doc_obj):
        if doc_obj.page > 1:
            _header_footer_aep(canvas_obj, doc_obj, empresa)

    story = []
    story += build_capa_aep(st, empresa, cnpj, data_emissao, logo_path)
    story += build_metodologia_aep(st, total_respondentes, total_autorizados)
    story += build_inventario_aep(st, inventario)
    story += build_plano_acao_aep(st, inventario)
    story += build_conclusao_aep(st, empresa, relatos)

    doc.build(story, onFirstPage=_callback, onLaterPages=_callback)
    buffer.seek(0)
    return buffer.getvalue()
