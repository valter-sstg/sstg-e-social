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
    "Crítico": {
        "faixa": "% risco > 98% (qualquer GR)",
        "faixa_desc": "Atribuída independentemente do GR sempre que o percentual médio de "
                "respostas indicadoras de risco superar 98%, configurando quase unanimidade "
                "na percepção de risco pelos trabalhadores.",
        "acao": "Intervenção imediata. Realizar Análise Ergonômica do Trabalho (AET) para "
                "avaliação aprofundada do fator de risco. Comunicar CIPA e médico do trabalho.",
        "justificativa": "Percentual de respostas indicadoras de risco superior a 98% da média "
                "das respostas, evidenciando quase unanimidade na percepção do risco pelos "
                "trabalhadores e configurando situação insuportável que exige avaliação "
                "aprofundada por meio de AET.",
        "prazo": "Imediato",
        "cor": colors.HexColor('#C0392B'),
    },
    "Alto": {
        "faixa": "GR > 8,0 — 16,0",
        "faixa_desc": "Combinação de Severidade e Probabilidade contínua que resulta em GR "
                "superior a 8,0, correspondente a probabilidade provável a muito provável "
                "de dano à saúde.",
        "acao": "Controle imediato. Medidas de engenharia e/ou administrativas em até 30 dias.",
        "justificativa": "Faixa de GR superior a 8,0, correspondente a probabilidade provável a "
                "muito provável de dano à saúde, demandando controle em curto prazo.",
        "prazo": "30 dias",
        "cor": C_LARANJA,
    },
    "Médio": {
        "faixa": "GR > 4,0 — 8,0 (ou % risco ≥ 70%)",
        "faixa_desc": "Combinação de Severidade e Probabilidade contínua que resulta em GR "
                "superior a 4,0 e até 8,0, correspondente a probabilidade possível a provável "
                "de dano à saúde. Adicionalmente, todo fator com percentual de respostas "
                "indicadoras de risco igual ou superior a 70% é classificado, no mínimo, "
                "como Médio, independentemente do GR calculado.",
        "acao": "Elaborar plano de ação com prazo de até 90 dias. Incluir no PGR.",
        "justificativa": "Faixa de GR superior a 4,0 e até 8,0 (ou percentual de respostas "
                "indicadoras de risco igual ou superior a 70%), correspondente a probabilidade "
                "possível a provável, devendo ser tratado de forma planejada dentro do PGR.",
        "prazo": "90 dias",
        "cor": C_AMARELO,
    },
    "Baixo": {
        "faixa": "GR ≤ 4,0",
        "faixa_desc": "Combinação de Severidade e Probabilidade contínua que resulta em GR de "
                "até 4,0, correspondente a baixa probabilidade de ocorrência de dano à saúde. "
                "Inclui os fatores sem respostas indicadoras de risco, nos quais a Probabilidade "
                "é 1,00 e o GR equivale à própria Severidade.",
        "acao": "Monitoramento periódico semestral. Sem necessidade de intervenção imediata.",
        "justificativa": "Faixa de GR de até 4,0, correspondente a baixa probabilidade de "
                "ocorrência, mantido sob monitoramento periódico.",
        "prazo": "Monitoramento semestral",
        "cor": C_VERDE,
    },
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

def build_capa_aep(st, empresa, cnpj, data_emissao, logo_path, grau_risco="—"):
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
        ("Grau de Risco da Atividade (NR-4):", grau_risco),
        ("Data de Emissão:", data_emissao),
        ("Norma de Referência:", "NR-17 (Portaria MTE 1.117/2023) e NR-01 (Portaria MTE 672/2021, "
                                  "atualizada pela Portaria MTE nº 765/2025)"),
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


# ===================== SEÇÃO 2: ESCOPO DA AVALIAÇÃO ERGONÔMICA =====================

def build_escopo_aep(st):
    el = []
    el.append(_titulo_secao("2. Escopo da Avaliação Ergonômica", st))
    el.append(Paragraph(
        "A presente AEP abrange os ambientes de trabalho da organização avaliada, com atividades "
        "realizadas presencialmente e remotamente.", st['body']))
    el.append(Paragraph("A avaliação contemplou:", st['body']))
    for item in [
        "análise da organização do trabalho;",
        "avaliação da carga cognitiva;",
        "avaliação das demandas operacionais;",
        "análise das condições organizacionais;",
        "identificação de fatores ergonômicos relacionados ao trabalho;",
        "percepção dos trabalhadores, e suas rotinas laborais.",
    ]:
        el.append(Paragraph(f"• {item}", st['lista']))
    return el


# ===================== SEÇÃO 3: PARTICIPAÇÃO DOS TRABALHADORES =====================

def build_participacao_aep(st):
    el = []
    el.append(_titulo_secao("3. Participação dos Trabalhadores", st))
    el.append(Paragraph("A organização assegurou:", st['body']))
    for item in [
        "participação dos trabalhadores;",
        "escuta ativa;",
        "confidencialidade;",
        "consulta durante a avaliação;",
        "acesso às informações relevantes.",
    ]:
        el.append(Paragraph(f"• {item}", st['lista']))
    el.append(Spacer(1, 0.1*cm))
    el.append(Paragraph(
        "A participação dos trabalhadores deverá permanecer contínua no ciclo de melhoria do GRO.",
        st['body']))
    return el


# ===================== SEÇÃO 4: METODOLOGIA =====================

def build_metodologia_aep(st, total_respondentes, total_autorizados, grau_risco_empresa="—"):
    el = []
    el.append(_titulo_secao("4. Metodologia de Avaliação", st))

    pct = round((total_respondentes / total_autorizados) * 100, 1) if total_autorizados else 0
    el.append(_subtitulo("4.1. Participação", st))
    el.append(_tabela_dados([
        ("Colaboradores Autorizados:", total_autorizados),
        ("Respostas Recebidas:", total_respondentes),
        ("Taxa de Adesão:", f"{pct}%"),
    ]))

    el.append(_subtitulo("4.2. Critério de Pontuação", st))
    el.append(Paragraph(
        "O questionário aplicado contém 17 perguntas distribuídas em 4 seções: A) Postura e Movimentos, "
        "B) Mobiliário e Equipamentos, C) Condições Ambientais e D) Organização do Trabalho. "
        "Cada resposta foi classificada como indicadora de risco (“Sim” nas perguntas diretas ou "
        "“Não” nas perguntas invertidas), parcialmente indicadora de risco (“Parcial”, ponderada "
        "com peso 0,5) ou sem risco; respostas “N/A” são excluídas do cálculo. "
        "Quando há identificação do setor/departamento do respondente, o percentual de respostas "
        "indicadoras de risco de cada pergunta é apurado pela média dos percentuais obtidos em "
        "cada setor, de modo que setores com menor número de respondentes tenham o mesmo peso "
        "que setores maiores na definição da faixa de risco; setores com menos de 3 respondentes "
        "são agrupados em um único conjunto no cálculo, preservando a representatividade "
        "estatística e o anonimato das respostas. "
        "O percentual de respostas indicadoras de risco de cada pergunta determina a Probabilidade, "
        "apurada de forma contínua (1,00 a 4,00 — Seção 4.3).",
        st['body']))

    el.append(_subtitulo("4.3. Probabilidade Contínua", st))
    el.append(Paragraph(
        "A Probabilidade é apurada de forma contínua e proporcional ao percentual de respostas "
        "indicadoras de risco, pela fórmula <b>Probabilidade = 1 + 3 × (% de risco)</b>, variando "
        "de 1,00 (nenhuma resposta indicadora de risco) a 4,00 (unanimidade na percepção do risco). "
        "A escala contínua elimina saltos de classificação nos limites entre faixas, assegurando que "
        "pequenas variações no percentual de respostas produzam variações igualmente pequenas no "
        "Grau de Risco. Exemplos de referência:",
        st['body']))
    dados_prob = [["% de respostas de risco", "Probabilidade resultante", "Interpretação"]]
    dados_prob += [
        ["0%", "1,00", "Improvável"],
        ["25%", "1,75", "Pouco provável"],
        ["50%", "2,50", "Possível"],
        ["75%", "3,25", "Provável"],
        ["100%", "4,00", "Muito provável"],
    ]
    t = Table(dados_prob, colWidths=[5.5*cm, 5.5*cm, 7.5*cm])
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

    el.append(_subtitulo("4.4. Grau de Risco (GR = Severidade × Probabilidade)", st))
    el.append(Paragraph(
        "A Severidade (1=Leve, 2=Moderada, 3=Grave, 4=Crítica) é pré-calibrada pelo responsável técnico "
        "para cada um dos 17 fatores de risco avaliados, com base no potencial de dano à saúde e no grau "
        "de risco da atividade econômica da organização (NR-4, conforme cadastro): empresas de grau de "
        "risco 1 ou 2 utilizam a calibração de menor exposição e empresas de grau de risco 3 ou 4 a "
        f"calibração de maior exposição. A organização avaliada possui grau de risco <b>{grau_risco_empresa}</b>. "
        "O Grau de Risco resulta da multiplicação entre Severidade e Probabilidade contínua, variando de "
        "1,0 a 16,0 (expresso com uma casa decimal), e é classificado conforme a tabela abaixo. "
        "Como regra de piso, fatores com percentual de respostas indicadoras de risco igual ou superior a "
        "70% são classificados, no mínimo, como Médio. "
        "A classificação “Crítico” é reservada às situações insuportáveis, atribuída exclusivamente quando o "
        "percentual médio de respostas indicadoras de risco (entre os setores avaliados) for superior a 98%, "
        "dada a quase unanimidade da percepção de risco pelos trabalhadores, independentemente do GR calculado.",
        st['body']))

    dados_gr = [["Faixa de GR", "Classificação", "Ação Recomendada"]]
    for classif, info in ACAO_POR_CLASSIFICACAO.items():
        texto_faixa = f"<b>{info['faixa']}</b><br/>{info['faixa_desc']}"
        texto_acao = f"{info['acao']} {info['justificativa']}"
        dados_gr.append([Paragraph(texto_faixa, st['table_cell']), classif, Paragraph(texto_acao, st['table_cell'])])
    t2 = Table(dados_gr, colWidths=[5*cm, 2.2*cm, 11.3*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), C_BRANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_BRANCO, C_CINZAC]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    el.append(t2)
    return el


# ===================== SEÇÃO 5: INVENTÁRIO DE RISCOS =====================

def build_inventario_aep(st, inventario):
    el = []
    el.append(_titulo_secao("5. Inventário de Riscos Ergonômicos", st))
    el.append(Paragraph(
        "A tabela a seguir consolida, para cada fator de risco avaliado, o percentual de respostas que "
        "indicaram a presença do risco, a Severidade, a Probabilidade e o Grau de Risco (GR) resultante. "
        "A coluna “Plano?” indica, com “SIM”, os riscos classificados como Alto ou Crítico, cujas medidas "
        "de controle recebem destaque prioritário no Plano de Ação (Seção 6.2).",
        st['body']))
    el.append(Spacer(1, 0.15*cm))

    cab = ["Nº", "Risco Identificado", "% Risco", "Sev.", "Prob.", "GR", "Classificação", "Plano?"]
    dados = [cab]
    cores_linhas = []
    for item in inventario:
        plano = item.get("Plano?", "SIM" if item["Classificação"] in ("Alto", "Crítico") else "NÃO")
        dados.append([
            str(item["Nº"]),
            Paragraph(item["Risco Identificado"], st['table_cell']),
            f"{item['% Risco']:.1f}%",
            str(item["Severidade"]),
            f"{item['Probabilidade']:.2f}",
            f"{item['GR']:.1f}",
            item["Classificação"],
            plano,
        ])
        cores_linhas.append(colors.HexColor(item["Cor"]))

    t = Table(dados, colWidths=[1*cm, 7.4*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.3*cm, 3.2*cm, 1.3*cm], repeatRows=1)
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
        estilo.append(('BACKGROUND', (6, i), (6, i), cor))
        estilo.append(('TEXTCOLOR', (6, i), (6, i), C_BRANCO))
        estilo.append(('FONTNAME', (6, i), (6, i), 'Helvetica-Bold'))
        estilo.append(('FONTNAME', (7, i), (7, i), 'Helvetica-Bold'))
    t.setStyle(TableStyle(estilo))
    el.append(t)
    return el


# ===================== SEÇÃO 6: MATRIZ CONSOLIDADA E PLANO DE AÇÃO =====================

def build_plano_acao_aep(st, inventario):
    el = []
    el.append(_titulo_secao("6. Matriz Consolidada e Plano de Ação", st))

    contagem = {"Crítico": 0, "Alto": 0, "Médio": 0, "Baixo": 0}
    for item in inventario:
        contagem[item["Classificação"]] += 1

    el.append(_subtitulo("6.1. Distribuição dos Riscos por Classificação", st))
    linha_chips = []
    for classif, qtd in contagem.items():
        cor = ACAO_POR_CLASSIFICACAO[classif]["cor"]
        linha_chips.append(_chip(f"{classif}: {qtd}", cor))
    chips_table = Table([linha_chips], colWidths=[4.6*cm]*4)
    chips_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    el.append(chips_table)
    el.append(Spacer(1, 0.3*cm))

    el.append(_subtitulo("6.2. Plano de Ação — Riscos Médio, Alto e Crítico", st))
    riscos_relevantes = [it for it in inventario if it["Classificação"] != "Baixo"]
    if not riscos_relevantes:
        el.append(Paragraph("Nenhum risco classificado como Médio, Alto ou Crítico foi identificado nesta avaliação.", st['body']))
    else:
        riscos_relevantes = sorted(riscos_relevantes, key=lambda x: x["GR"], reverse=True)
        cab = ["Risco Identificado", "GR", "Classif.", "Medida de Controle Recomendada", "Prazo"]
        dados = [cab]
        cores_linhas = []
        destaques = []
        for item in riscos_relevantes:
            info = ACAO_POR_CLASSIFICACAO[item["Classificação"]]
            acao = info["acao"]
            prazo = info["prazo"]
            destaque = item["Classificação"] in ("Alto", "Crítico")
            nome_risco = f"<b>{item['Risco Identificado']}</b>" if destaque else item["Risco Identificado"]
            dados.append([
                Paragraph(nome_risco, st['table_cell']),
                f"{item['GR']:.1f}",
                item["Classificação"],
                Paragraph(acao, st['table_cell']),
                prazo,
            ])
            cores_linhas.append(colors.HexColor(item["Cor"]))
            destaques.append(destaque)
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
        for i, (cor, destaque) in enumerate(zip(cores_linhas, destaques), start=1):
            if destaque:
                estilo.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FDF0E7')))
            estilo.append(('BACKGROUND', (2, i), (2, i), cor))
            estilo.append(('TEXTCOLOR', (2, i), (2, i), C_BRANCO))
            estilo.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
        t.setStyle(TableStyle(estilo))
        el.append(t)
        el.append(Spacer(1, 0.15*cm))
        el.append(Paragraph(
            "As linhas destacadas correspondem aos riscos com indicação “SIM” na coluna “Plano?” do "
            "Inventário (classificação Alto ou Crítico), prioritários para a execução das medidas de controle.",
            st['body']))

    el.append(Spacer(1, 0.2*cm))
    el.append(Paragraph(
        "As medidas de controle devem seguir a hierarquia de prevenção: Eliminação → Substituição → "
        "Controles de Engenharia → Controles Administrativos → Equipamento de Proteção Individual (EPI). "
        "Riscos classificados como Alto ou Crítico devem ser registrados no PGR da empresa e comunicados "
        "ao SESMT ou ao médico coordenador do PCMSO.", st['body']))
    return el


# ===================== SEÇÃO 7: NECESSIDADE DE AET =====================

def build_necessidade_aet(st, inventario):
    el = []
    el.append(_titulo_secao("7. Necessidade de Análise Ergonômica do Trabalho (AET)", st))
    el.append(Paragraph(
        "Uma avaliação contínua da necessidade de Análise Ergonômica do Trabalho — AET, será aplicável:",
        st['body']))
    for item in [
        "em caso de adoecimento;",
        "aumento de afastamentos;",
        "queixas recorrentes;",
        "alterações organizacionais relevantes;",
        "aumento da demanda operacional.",
    ]:
        el.append(Paragraph(f"• {item}", st['lista']))

    el.append(Spacer(1, 0.2*cm))
    riscos_criticos = [it for it in inventario if it["Classificação"] == "Crítico"]
    if riscos_criticos:
        nomes = "; ".join(it["Risco Identificado"] for it in riscos_criticos)
        el.append(Paragraph(
            f"Com base nos resultados desta AEP, foram identificados {len(riscos_criticos)} fator(es) de "
            f"risco classificado(s) como <b>Crítico</b> ({nomes}), o que indica a presença de uma das "
            "condições acima descritas. Recomenda-se, portanto, a realização de Análise Ergonômica do "
            "Trabalho — AET para o(s) fator(es) de risco crítico(s) identificado(s), conforme item 17.3.2 "
            "da NR-17.", st['body']))
    else:
        el.append(Paragraph(
            "Com base nos resultados desta AEP, não foram identificados fatores de risco classificados "
            "como <b>Crítico</b>, não havendo, no momento, indicativos das condições que demandariam a "
            "realização de Análise Ergonômica do Trabalho — AET, conforme item 17.3.2 da NR-17. A "
            "necessidade de AET deverá, contudo, ser reavaliada continuamente conforme os critérios "
            "acima.", st['body']))
    return el


# ===================== SEÇÃO 8: RELATOS E CONCLUSÃO =====================

def build_conclusao_aep(st, empresa, relatos, inventario):
    el = []
    el.append(_titulo_secao("8. Relatos dos Trabalhadores e Conclusão", st))

    el.append(_subtitulo("8.1. Relatos Coletados (Seção 3 do Questionário)", st))
    relatos_validos = [r.strip() for r in relatos if r and r.strip()]
    if relatos_validos:
        for relato in relatos_validos[:30]:
            el.append(Paragraph(f"• {relato}", st['lista']))
    else:
        el.append(Paragraph("Nenhum relato adicional foi registrado pelos respondentes.", st['body']))

    el.append(Spacer(1, 0.2*cm))
    el.append(_subtitulo("8.2. Conclusão", st))

    riscos_criticos = [it for it in inventario if it["Classificação"] == "Crítico"]
    if riscos_criticos:
        conclusao_aet = (
            "Diante da identificação de fator(es) de risco classificado(s) como <b>Crítico</b>, recomenda-se "
            "a realização de Análise Ergonômica do Trabalho — AET para aprofundamento da avaliação e "
            "definição de medidas de controle específicas, conforme detalhado na Seção 7 deste laudo."
        )
    else:
        conclusao_aet = (
            "Não foram identificados fatores de risco classificados como <b>Crítico</b> nesta avaliação, "
            "concluindo-se pela não recomendação de Análise Ergonômica do Trabalho — AET no presente "
            "momento, conforme detalhado na Seção 7 deste laudo."
        )

    el.append(Paragraph(
        f"A presente Avaliação Ergonômica Preliminar (AEP) da empresa <b>{empresa}</b> identificou os fatores "
        "de risco ergonômicos descritos no Inventário de Riscos (Seção 5), classificados conforme a Matriz "
        "Severidade × Probabilidade (Seção 4.4). Recomenda-se a implementação do Plano de Ação proposto "
        "(Seção 6), priorizando os riscos classificados como Alto e Crítico. " + conclusao_aet + " "
        "Recomenda-se, ainda, a revisão periódica deste inventário após qualquer alteração de processo, "
        "layout, equipamento ou força de trabalho, e no mínimo a cada 2 anos, conforme NR-01.", st['body']))

    el.append(Spacer(1, 1.5*cm))
    assinaturas = Table([
        ["", ""],
        [
            Paragraph(f"<b>{RESP_NOME}</b><br/>MTE: {RESP_MTE}<br/>CREA: {RESP_CREA}", st['body']),
            Paragraph("<b>Representante Legal da Organização</b><br/>Nome: "
                      "______________________________<br/>CPF: ______________________________",
                      st['body']),
        ],
    ], colWidths=[9*cm, 9*cm])
    assinaturas.setStyle(TableStyle([
        ('LINEABOVE', (0, 1), (-1, 1), 0.8, C_CINZA),
        ('TOPPADDING', (0, 1), (-1, 1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 30),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, -1), 20),
    ]))
    el.append(assinaturas)
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

    dados_empresa: dict com chaves 'Empresa', 'CNPJ' e 'Grau_Risco' (grau de risco NR-4 do cadastro)
    inventario: lista de dicts retornada por _calcular_inventario_aep (app_cloud.py)
    total_respondentes / total_autorizados: contagens para cálculo de adesão
    relatos: lista de strings com os relatos abertos dos trabalhadores
    """
    buffer = io.BytesIO()
    empresa = dados_empresa.get("Empresa", "—")
    cnpj    = dados_empresa.get("CNPJ", "—")
    grau_risco = str(dados_empresa.get("Grau_Risco", "—") or "—")
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
    story += build_capa_aep(st, empresa, cnpj, data_emissao, logo_path, grau_risco)
    story += build_escopo_aep(st)
    story += build_participacao_aep(st)
    story += build_metodologia_aep(st, total_respondentes, total_autorizados, grau_risco)
    story += build_inventario_aep(st, inventario)
    story += build_plano_acao_aep(st, inventario)
    story += build_necessidade_aet(st, inventario)
    story += build_conclusao_aep(st, empresa, relatos, inventario)

    doc.build(story, onFirstPage=_callback, onLaterPages=_callback)
    buffer.seek(0)
    return buffer.getvalue()
