from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image, CondPageBreak
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


# ===================== AÇÕES DE CONTROLE POR RISCO (pré-definidas pelo RT) =====================
# Chave = nº do risco no inventário (1 a 17, mesma ordem das perguntas q1..q17)
ACOES_CONTROLE_RT = {
    1: [  # Postura estática — fadiga muscular / dor lombar / varizes
        "Ajustar mobiliário para permitir alternância de postura (cadeiras reguláveis, mesas ajustáveis, apoios para os pés).",
        "Introduzir pausas breves a cada 50–60 minutos para mudança de posição e alongamentos simples guiados (cartazes, vídeos rápidos).",
        "Incentivar alternância entre tarefas sentadas e em pé (rodízio de posto ou mesas com regulagem de altura).",
    ],
    2: [  # Torção de tronco/pescoço — sobrecarga cervical e lombar / LER-DORT
        "Reorganizar layout para que telas, documentos e materiais de uso frequente fiquem à frente do trabalhador, evitando rotações constantes de pescoço e tronco.",
        "Usar suportes de monitor e de documentos para que o topo da tela fique na altura dos olhos e o material de leitura ao lado da tela.",
        "Aplicar treinamento prático sobre “regra da zona de alcance” (o que é muito usado deve ficar na zona próxima ao corpo).",
    ],
    3: [  # Levantamento de peso — lombalgias / hérnia de disco
        "Reduzir peso unitário de cargas (fracionamento de volumes, uso de caixas menores) para valores compatíveis com limites recomendados e idade/sexo da população.",
        "Adotar meios mecânicos (carrinhos, paleteiras, elevadores de carga, mesas elevatórias) e adequar trajetos para evitar degraus e desníveis.",
        "Treinar técnicas de levantamento seguro (aproximar carga, flexão de joelhos, evitar rotação de tronco com carga) e trabalho em duplas para cargas mais pesadas.",
    ],
    4: [  # Movimentos repetitivos — LER/DORT / tendinite / túnel do carpo
        "Redesenhar tarefas para reduzir repetitividade: automação parcial, uso de gabaritos, divisão da tarefa em etapas com rodízio entre trabalhadores.",
        "Implementar pausas regulares curtas (micro-pausas) com alongamentos orientados, especialmente para mãos, ombros e pescoço.",
        "Ajustar ferramentas e periféricos (teclados, mouses, alicates) para empunhadura neutra, reduzindo desvios extremos de punho.",
    ],
    5: [  # Força intensa — fadiga muscular / lesão tendínea
        "Substituir tarefas que exigem força manual por dispositivos mecânicos, pneumáticos ou elétricos (chaves, prensas, alavancas).",
        "Adaptar cabos e empunhaduras das ferramentas para aumentar área de contato e permitir uso com punho neutro, reduzindo a força necessária.",
        "Ajustar metas e cadência para evitar exigência de força máxima repetida e orientar sobre respeito aos limites individuais.",
    ],
    6: [  # Altura de mesa/bancada — postura compensatória / sobrecarga ombros
        "Ajustar altura de mesas/bancadas à atividade: levemente abaixo do cotovelo para digitação, mais baixa para tarefas de força, mais alta para tarefas de precisão.",
        "Adotar bancadas reguláveis em altura ou, quando não possível, ajustar cadeira e uso de apoios de pés, mantendo ombros relaxados.",
        "Realizar avaliação ergonômica para cada tipo de posto, com check-list e fotos, documentando antes e depois das melhorias.",
    ],
    7: [  # Cadeira — compressão de raiz nervosa / dor lombar
        "Utilizar cadeiras com apoio lombar, regulagens de altura, encosto e braços, permitindo que pés fiquem totalmente apoiados e joelhos em ângulo próximo de 90 graus.",
        "Ajustar profundidade do assento (espaço de 2–3 dedos entre borda do assento e parte posterior do joelho) para evitar compressão de vasos/nervos.",
        "Treinar ajustes personalizados da cadeira e orientar para evitar permanecer “na ponta da cadeira” por longos períodos.",
    ],
    8: [  # Tela/teclado/mouse — síndrome cervicobraquial / fadiga visual
        "Posicionar monitor com topo na altura dos olhos, a cerca de um braço de distância, e evitar reflexos ajustando iluminação e ângulo da tela.",
        "Manter teclado e mouse na altura do cotovelo, próximos ao corpo, e considerar apoios de punho ou mouses ergonômicos quando indicado.",
        "Orientar pausas visuais (regra 20-20-20: a cada 20 minutos, olhar 20 segundos para algo a 6 m) e, quando necessário, avaliação oftalmológica periódica.",
    ],
    9: [  # Ferramentas — sobrecarga de punho / De Quervain
        "Selecionar ferramentas com design ergonômico (cabos texturizados, diâmetro adequado, acionamento com esforço moderado, vibração reduzida).",
        "Ajustar comprimento e peso da ferramenta para adequar ao tipo de tarefa e posicionar a peça de trabalho para manter punho neutro.",
        "Realizar manutenção preventiva, lubrificação e substituição de ferramentas que exijam força excessiva ou apresentem vibrações anormais.",
    ],
    10: [  # Iluminação — fadiga visual / cefaleia
        "Adequar níveis de iluminância ao tipo de tarefa (trabalho de escritório, leitura, tarefas de precisão) conforme normas técnicas, evitando áreas de sombra e ofuscamento.",
        "Posicionar luminárias para que a luz venha lateralmente, reduzindo reflexos em telas e superfícies brilhantes.",
        "Realizar manutenção periódica de lâmpadas e luminárias (limpeza, substituição de lâmpadas queimadas) e prever luz suplementar em tarefas delicadas.",
    ],
    11: [  # Ruído — estresse / perda auditiva
        "Intervir na fonte (manutenção de máquinas, substituição por equipamentos menos ruidosos, enclausuramento de fontes críticas).",
        "Implementar barreiras acústicas, cabines e distanciamento físico entre fonte e postos de trabalho, planejando layout para reduzir exposição.",
        "Estabelecer Programa de Conservação Auditiva com monitoramento ambiental, audiometrias periódicas, rodízio de exposição e uso adequado de protetores auriculares quando necessário.",
    ],
    12: [  # Temperatura/ventilação — fadiga por calor / desconforto
        "Controlar temperatura e ventilação com climatização adequada, ventilação cruzada, exaustão local e isolamento de fontes de calor.",
        "Ajustar vestimentas de trabalho (tecidos mais leves em ambientes quentes, camadas em ambientes frios) e planejar pausas em locais mais confortáveis para recuperação térmica.",
        "Monitorar condições térmicas em diferentes horários e ajustar jornada ou rodízio nos períodos mais críticos.",
    ],
    13: [  # Ritmo imposto por máquina — estresse psicossocial / fadiga acelerada
        "Rever programação de máquinas e linhas para reduzir cadência excessiva, compatibilizando ritmo com capacidade humana sem exigir esforço máximo constante.",
        "Introduzir rodízio entre tarefas de maior e menor exigência, dando ao trabalhador algum grau de controle sobre o ritmo quando viável.",
        "Incluir esses aspectos no GRO como risco psicossocial, prevendo acompanhamento sistemático de queixas, absenteísmo e indicadores de saúde.",
    ],
    14: [  # Pausas insuficientes — fadiga acumulada / LER-DORT
        "Estruturar pausas regulares previstas em procedimento, com duração e frequência definidas conforme tipo de tarefa (por exemplo, micro-pausas a cada 50–60 minutos).",
        "Programar pausas ativas com orientações simples de alongamento e mobilidade articular.",
        "Monitorar efetividade das pausas (se são realmente realizadas) e ajustar em função de indicadores de fadiga e queixas dos trabalhadores.",
    ],
    15: [  # Pressão por metas — burnout / ansiedade / erro humano
        "Estabelecer metas realistas, construídas com participação das equipes e alinhadas à capacidade de recursos (pessoas, equipamentos, tempo).",
        "Treinar lideranças em gestão de pessoas e prevenção de riscos psicossociais, promovendo estilo de gestão menos punitivo e mais orientado a feedback construtivo.",
        "Implementar programas de apoio psicossocial (escuta qualificada, encaminhamento para apoio especializado, campanhas de saúde mental) e monitorar indicadores de clima e adoecimento.",
    ],
    16: [  # Atenção intensa contínua — fadiga cognitiva / erros críticos
        "Redesenhar tarefas de alta vigilância (monitoramento, operação crítica) para prever pausas mentais e revezamento de operadores.",
        "Reduzir estímulos desnecessários (ruído, interrupções constantes, múltiplas demandas simultâneas) e padronizar interfaces/telas para facilitar processamento de informação.",
        "Fornecer treinamento em estratégias de gestão de atenção e protocolos claros para situações anormais, diminuindo carga mental e ambiguidade.",
    ],
    17: [  # Falta de treinamento — risco de acidente / posturas incorretas
        "Estruturar programa contínuo de capacitação (integração, treinamentos periódicos, reciclagem) contemplando riscos, controles e uso correto de equipamentos.",
        "Utilizar métodos práticos e contextualizados (demonstração no posto, simulações, checklists) e registrar presença e avaliação de aprendizagem.",
        "Incluir treinamento como medida formal no PGR e no GRO, com cronograma, conteúdos mínimos e avaliação de eficácia (observação de campo, indicadores de acidentes).",
    ],
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
    el.append(CondPageBreak(3*cm))
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
    el.append(CondPageBreak(3*cm))
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
    el.append(CondPageBreak(3*cm))
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
        "Cada resposta indica a frequência com que a situação descrita ocorre (“Nunca”, "
        "“Raramente”, “Às vezes”, “Frequentemente” ou “Sempre”), convertida em um peso de "
        "0 a 1 (0%, 25%, 50%, 75% e 100%, respectivamente); nas perguntas invertidas o peso "
        "é complementar (1 - peso). Respostas “N/A” são excluídas do cálculo. "
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
    cores_classif = []
    for classif, info in ACAO_POR_CLASSIFICACAO.items():
        texto_faixa = f"<b>{info['faixa']}</b><br/>{info['faixa_desc']}"
        texto_acao = f"{info['acao']} {info['justificativa']}"
        dados_gr.append([Paragraph(texto_faixa, st['table_cell']), classif, Paragraph(texto_acao, st['table_cell'])])
        cores_classif.append(info["cor"])
    t2 = Table(dados_gr, colWidths=[5*cm, 2.2*cm, 11.3*cm])
    estilo_gr = [
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
    ]
    for i, cor in enumerate(cores_classif, start=1):
        estilo_gr.append(('BACKGROUND', (1, i), (1, i), cor))
        estilo_gr.append(('TEXTCOLOR', (1, i), (1, i), C_BRANCO))
        estilo_gr.append(('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'))
    t2.setStyle(TableStyle(estilo_gr))
    el.append(t2)
    return el


# ===================== SEÇÃO 5: INVENTÁRIO DE RISCOS =====================

def build_inventario_aep(st, inventario):
    el = []
    el.append(CondPageBreak(3*cm))
    el.append(_titulo_secao("5. Inventário de Riscos Ergonômicos", st))
    el.append(Paragraph(
        "A tabela a seguir consolida, para cada fator de risco avaliado, o percentual de respostas que "
        "indicaram a presença do risco, a Severidade, a Probabilidade e o Grau de Risco (GR) resultante. "
        "A coluna “Plano?” indica, com “SIM”, os riscos classificados como Médio, Alto ou Crítico, cuja "
        "inclusão no Plano de Ação (Seção 6.2) fica recomendada.",
        st['body']))
    el.append(Spacer(1, 0.15*cm))

    cab = ["Nº", "Risco Identificado", "% Risco", "Sev.", "Prob.", "GR", "Classificação", "Plano?"]
    dados = [cab]
    cores_linhas = []
    for item in inventario:
        plano = item.get("Plano?", "SIM" if item["Classificação"] in ("Médio", "Alto", "Crítico") else "NÃO")
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
    el.append(CondPageBreak(3*cm))
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

    def _tem_plano(it):
        return it.get("Plano?", "SIM" if it["Classificação"] in ("Médio", "Alto", "Crítico") else "NÃO") == "SIM"

    riscos_relevantes = [it for it in inventario if _tem_plano(it)]
    if not riscos_relevantes:
        el.append(Paragraph(
            "Nenhum fator de risco recebeu indicação “SIM” na coluna “Plano?” do Inventário de Riscos "
            "(Seção 5) nesta avaliação.", st['body']))
    else:
        el.append(Paragraph(
            "Integram este Plano de Ação os fatores de risco com indicação “SIM” na coluna “Plano?” do "
            "Inventário de Riscos (Seção 5) — classificações Médio, Alto e Crítico. "
            "As medidas de controle recomendadas para cada fator de risco foram pré-definidas pelo "
            "responsável técnico com base na natureza do risco e na hierarquia de prevenção, com o "
            "objetivo de minimizar, reduzir ou eliminar os impactos à saúde dos trabalhadores.",
            st['body']))
        el.append(Spacer(1, 0.15*cm))
        riscos_relevantes = sorted(riscos_relevantes, key=lambda x: x["GR"], reverse=True)
        cab = ["Risco Identificado", "GR", "Classif.", "Medidas de Controle Recomendadas", "Prazo"]
        dados = [cab]
        cores_linhas = []
        destaques = []
        for item in riscos_relevantes:
            info = ACAO_POR_CLASSIFICACAO[item["Classificação"]]
            prazo = info["prazo"]
            acoes_rt = ACOES_CONTROLE_RT.get(item["Nº"], [])
            if acoes_rt:
                acao = "<br/>".join(f"• {a}" for a in acoes_rt)
                if item["Classificação"] == "Crítico":
                    acao = f"<b>• {info['acao']}</b><br/>" + acao
            else:
                acao = info["acao"]
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
            "As linhas destacadas correspondem aos riscos classificados como Alto ou Crítico, "
            "prioritários para a execução das medidas de controle.",
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
    el.append(CondPageBreak(3*cm))
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
    el.append(CondPageBreak(3*cm))
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
