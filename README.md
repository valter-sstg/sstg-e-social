# 🧠 DRE - DRPS — Gestão Integrada de Riscos Ergonômicos e Psicossociais

**Versão:** 8.0
**Atualizado:** 12/06/2026
**Status:** ✅ Em Produção (Streamlit Cloud)

---

## 🎯 O que é o DRE - DRPS?

Sistema **web** que reúne, em um único lugar, os dois diagnósticos exigidos pela
legislação trabalhista para a gestão de riscos ocupacionais:

- 📋 **DRPS** — Diagnóstico de Riscos Psicossociais, com base no protocolo
  **COPSOQ III** (Copenhagen Psychosocial Questionnaire), em atendimento à **NR-01**
  (Portaria MTE nº 765/2025).
- 🦴 **DRE** — Diagnóstico de Riscos Ergonômicos, com base na **AEP** (Análise
  Ergonômica Preliminar), em atendimento à **NR-17**.

Os dois questionários são respondidos pelos colaboradores, processados
automaticamente e transformados em **laudos técnicos em PDF**, prontos para
compor o **PGR** (Programa de Gerenciamento de Riscos) da empresa.

### Características Principais

✅ **Anonimato Garantido** — CPF nunca é armazenado em texto puro (hash SHA-256)
✅ **Dois Questionários Integrados** — Psicossocial (DRPS) e Ergonômico (DRE), no mesmo link de acesso
✅ **Metodologia de Grau de Risco (GR) v2** — classificação objetiva Baixo / Médio / Alto / Crítico
✅ **Modo Demonstração** — equipe SSTG visualiza qualquer questionário sem usar dados reais
✅ **Laudos Automáticos em PDF** — DRPS e DRE, com inventário de riscos e plano de ação
✅ **Painel "Início"** — indicadores (CNPJs, colaboradores, respostas, laudos) e gráficos
✅ **Módulo RH Simplificado** — acompanhamento por empresa + e-books de apoio
✅ **Persistência em Banco de Dados** — Supabase (PostgreSQL), sem perda de dados em atualizações
✅ **LGPD Compliant** — proteção de dados pessoais dos colaboradores

---

## 🧭 Menu do Sistema

O sistema é organizado em 5 módulos, acessíveis pelo menu lateral ("Módulo:"):

| Módulo | Quem usa | Para quê |
|--------|----------|----------|
| 🏠 **Início** | Todos | Dashboard com indicadores gerais e gráficos |
| 📝 **Questionários DRE-DRPS** | Colaboradores | Responder ao questionário Psicossocial (DRPS) ou Ergonômico (DRE) |
| 📊 **Gestão das Respostas (RH)** | RH da empresa cliente | Acompanhar respostas, gerar laudos, baixar e-books de apoio |
| 📚 **Documentação** | Equipe SSTG | Guias e tutoriais do sistema (esta seção) |
| 🔐 **Admin SSTG (Gestão)** | Equipe SSTG | Cadastro, conferência, resultados, segurança e usuários |

---

## 📖 Documentação Disponível

Todos os guias abaixo ficam disponíveis dentro do próprio sistema, no módulo
**📚 Documentação** (acesso restrito à equipe SSTG):

### Para a Equipe SSTG e RH

**👥 TUTORIAL.md** — Tutorial Operacional

- Como acessar o sistema (equipe SSTG, RH e colaboradores)
- Como cadastrar empresas e colaboradores
- Como gerar e distribuir os links de acesso
- Como o colaborador responde aos questionários DRPS e DRE
- Como consultar resultados, ler o Grau de Risco (GR) e gerar laudos
- Como usar o módulo RH (e-books, troca de empresa)
- FAQ com problemas comuns

### Para Administradores do Sistema

**🚀 GUIA_INSTALACAO.md** — Guia de Instalação e Publicação

- Como o sistema está publicado hoje (Streamlit Cloud + GitHub + Supabase)
- Como atualizar o sistema (fluxo de upload e reboot)
- Configuração de credenciais (Supabase, senhas)
- Backup e recuperação de dados
- Troubleshooting de publicação

### Para Desenvolvedores / Técnicos

**🔧 GUIA_TECNICO.md** — Documentação Técnica

- Arquitetura do sistema (app, banco de dados, geradores de laudo)
- Estrutura de dados no Supabase
- Fluxos de dados (cadastro, resposta, laudo)
- Metodologia de Grau de Risco (GR) v2 — fórmulas e classificação
- Variáveis e segredos de configuração
- Troubleshooting técnico

### Checklist

**✅ CHECKLIST_LANCAMENTO.md** — Checklist de Lançamento

- Lista de verificação para validar uma nova versão antes de publicar

---

## ⚡ Como Acessar

O sistema já está publicado e em uso — não é necessário instalar nada para
utilizá-lo no dia a dia.

### 1️⃣ Equipe SSTG (Admin)

1. Acesse o link do sistema
2. Menu **🔐 Admin SSTG (Gestão)**
3. Informe usuário e senha da equipe SSTG

### 2️⃣ RH da Empresa Cliente

1. Acesse o link do sistema
2. Menu **📊 Gestão das Respostas (RH)**
3. Informe o **CNPJ** e a **senha** definidos pela equipe SSTG para aquela empresa

### 3️⃣ Colaborador

1. Recebe um link específico (DRPS ou DRE) por WhatsApp/e-mail
2. Informa o **CPF** (11 dígitos)
3. Responde ao questionário (Psicossocial ou Ergonômico, conforme o link)
4. Envia as respostas — anônimas a partir desse ponto

### 4️⃣ Gerar Laudo

1. **🔐 Admin SSTG** → aba **📊 Resultados DRPS** ou **🦴 Resultados DRE**
2. Selecione a empresa
3. Clique em **Gerar Laudo (DRPS/DRE) em PDF**

---

## 🏗️ Arquitetura Resumida

```
┌──────────────────────────────────────┐
│        Navegador Web (qualquer SO)    │
│            Streamlit Frontend         │
└────────────────────┬──────────────────┘
                      │ HTTPS
┌────────────────────▼──────────────────┐
│        Streamlit Cloud (app.py)       │
│  • app.py — módulos Início/Quest./RH/ │
│    Documentação/Admin                 │
│  • db.py — camada de acesso ao banco  │
│  • gerar_laudo.py — laudo DRPS (PDF)  │
│  • gerar_laudo_aep.py — laudo DRE (PDF)│
│  • config.toml — tema visual          │
└────────────────────┬──────────────────┘
                      │ API (Supabase)
┌────────────────────▼──────────────────┐
│         Supabase (PostgreSQL)         │
│  • acessos — empresas e colaboradores │
│  • respostas / respostas_aep          │
│  • usuarios — login da equipe SSTG    │
│  • laudos — histórico de laudos gerados│
│  • config — chaves e parâmetros gerais │
└────────────────────────────────────────┘
```

O banco de dados (Supabase) garante que **nenhum dado se perde** quando o
sistema é atualizado/reiniciado no Streamlit Cloud — diferente das versões
anteriores, que usavam arquivos CSV locais.

---

## 📊 Fluxos de Dados Principais

### Fluxo DRPS (Psicossocial)

```
Equipe SSTG cadastra empresa e colaboradores (Admin → Cadastro)
        │
        ▼
Link DRPS é gerado e enviado ao colaborador (?cnpj=...)
        │
        ▼
Colaborador informa CPF → responde 35 questões (7 dimensões COPSOQ III)
        │
        ▼
Respostas gravadas no Supabase (CPF → hash, sem dados identificáveis)
        │
        ▼
Admin → 📊 Resultados DRPS → Gerar Laudo DRPS em PDF
```

### Fluxo DRE (Ergonômico)

```
Equipe SSTG cadastra empresa, colaboradores e Grau de Risco NR-4
        │
        ▼
Link DRE é gerado e enviado ao colaborador (?modulo=aep)
        │
        ▼
Colaborador informa CPF → responde 17 questões (4 seções A-D)
        │
        ▼
Respostas gravadas no Supabase
        │
        ▼
Admin → 🦴 Resultados DRE → Inventário de Riscos com GR → Gerar Laudo DRE em PDF
```

---

## 🔒 Segurança & LGPD

| Aspecto | Implementação |
|---------|---------------|
| **Anonimato** | CPF → hash SHA-256 (não pode ser revertido) |
| **Controle de Acesso** | Período de resposta configurável por empresa |
| **Acesso RH** | Login por CNPJ + senha definida pela equipe SSTG |
| **Acesso Admin** | Login de usuários da equipe SSTG (perfis admin/operacional) |
| **Inativação** | Colaboradores inativados perdem acesso ao questionário |
| **Persistência** | Banco de dados Supabase (PostgreSQL), com backups gerenciados |
| **Sigilo** | Resultados individuais não são exibidos; apenas médias/indicadores agregados |

---

## 📋 Estrutura dos Questionários

### DRPS — Psicossocial (COPSOQ III) — 35 questões em 7 dimensões

| # | Dimensão | Questões | Foco | Invertida? |
|---|----------|----------|------|------------|
| 1️⃣ | 📦 Cargo | 5 | Clareza da função | Não |
| 2️⃣ | 🎮 Controle | 6 | Autonomia de decisão | Não |
| 3️⃣ | ⚖️ Demandas | 8 | Pressão e carga de trabalho | ✅ Sim |
| 4️⃣ | ⚠️ Relacionamentos | 4 | Conflitos e assédio | ✅ Sim |
| 5️⃣ | 🤝 Apoio dos Colegas | 4 | Solidariedade entre colegas | Não |
| 6️⃣ | 👔 Apoio da Chefia | 5 | Suporte gerencial | Não |
| 7️⃣ | 📢 Comunicação e Mudanças | 3 | Transparência | Não |

Escala Likert de 5 pontos (Nunca → Sempre). Dimensões "invertidas" têm a
pontuação calculada de forma inversa (quanto mais frequente, maior o risco).

### DRE — Ergonômico (AEP / NR-17) — 17 questões em 4 seções

| Seção | Tema | Pergunta central |
|-------|------|-------------------|
| A. Postura e Movimentos | Como você usa o corpo no trabalho? | Posturas, movimentos repetitivos, esforço |
| B. Mobiliário e Equipamentos | O ambiente de trabalho está adequado? | Mesas, cadeiras, ferramentas, equipamentos |
| C. Condições Ambientais | Como é o ambiente físico onde você trabalha? | Iluminação, ruído, temperatura |
| D. Organização do Trabalho | Como o trabalho é estruturado e cobrado? | Ritmo, pausas, jornada |

Cada questão tem uma pergunta principal + uma linha de ajuda em linguagem
simples, pensada para colaboradores com diferentes níveis de escolaridade.

---

## 🎯 Metodologia de Grau de Risco (GR) — v2

O **Grau de Risco (GR)** do laudo DRE é calculado para cada um dos 17 itens do
inventário, combinando **Severidade** (pré-calibrada pelo Responsável Técnico,
conforme o Grau de Risco NR-4 da empresa) e **Probabilidade** (calculada a
partir do percentual de respostas que indicam risco):

```
Probabilidade = 1 + 3 × (% de respostas com risco)     → varia de 1,00 a 4,00
GR = Severidade (1-4) × Probabilidade (1,00-4,00)       → varia de 1,0 a 16,0
```

### Classificação

| Faixa de GR | Classificação | Observações |
|-------------|----------------|-------------|
| ≤ 4,0 | 🟢 Baixo | — |
| > 4,0 e ≤ 8,0 | 🟡 Médio | Plano de ação recomendado (Plano? = SIM) |
| > 8,0 | 🔴 Alto | Plano de ação obrigatório + destaque no laudo |
| % de risco > 98% | ⚫ Crítico | Situação insuportável — recomenda AET (Análise Ergonômica do Trabalho) |

**Regras adicionais:**
- Se ≥ 70% das respostas indicarem risco, a classificação **nunca** fica abaixo de Médio.
- Se 0% das respostas indicarem risco, o GR é sempre **Baixo**.
- Setores com menos de 3 respondentes são agrupados para preservar o anonimato.

A mesma lógica de "Plano? = SIM a partir de Médio" é usada também no laudo DRPS.

---

## 🎨 Identidade Visual SSTG

```
Cores Primárias:
🔵 Azul Navy:    #282C5B  (cabeçalhos, menus)
🟢 Verde:        #5A9F62  (sucesso, gráficos)
🟠 Laranja:      #DC3B24  (chamadas para ação / Alto risco)
⚪ Cinza Claro:  #EFEFEF  (fundo)

Tipografia: Sans Serif (Segoe UI / Arial)
Logo: logo_sstg.png (sidebar)
```

---

## 🚀 Publicação (Streamlit Cloud)

O sistema já está publicado e em produção:

- **Repositório:** GitHub — `valter-contador/sstg-e-social` (branch `main`)
- **Hospedagem:** Streamlit Cloud (plano gratuito)
- **Banco de dados:** Supabase (plano gratuito — "hiberna" após 7 dias sem uso, e
  é "despertado" automaticamente pelo próprio app)

Para o passo a passo de como atualizar o sistema publicado, veja o
**🚀 GUIA_INSTALACAO.md**.

---

## 📱 Compatibilidade

| Navegador | Desktop | Mobile |
|-----------|---------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ | ✅ |
| Edge | ✅ | ✅ |

**Recomendação:** equipe SSTG/RH em desktop para cadastro e laudos;
colaboradores podem responder pelo celular.

---

## 🛠️ Tecnologias Utilizadas

```
Frontend/Backend:  Streamlit (Python)
Banco de Dados:    Supabase (PostgreSQL)
Geração de PDF:    ReportLab
Gráficos:          Plotly
Segurança:         SHA-256, controle de período e de acesso
Hospedagem:        Streamlit Cloud
```

---

## 📈 Próximos Passos

- [ ] Acompanhar laudos DRE aplicados no dia a dia e ajustar conforme feedback
- [ ] Avaliar exportação de laudos em outros formatos
- [ ] Avaliar notificações automáticas de prazo de resposta

---

## ❓ FAQ Rápido

**P: Os dados dos colaboradores ficam seguros?**
R: Sim. O CPF é transformado em hash (SHA-256) e não pode ser revertido. Os
resultados exibidos são sempre agregados (médias por empresa/setor).

**P: O colaborador pode responder o questionário mais de uma vez?**
R: Não. O sistema identifica o CPF (via hash) e bloqueia duplicidade dentro
do período configurado.

**P: O que acontece se o sistema for atualizado? Os dados são perdidos?**
R: Não. Todos os dados ficam no banco de dados (Supabase), independente de
atualizações do aplicativo.

**P: Qual é a diferença entre DRPS e DRE?**
R: DRPS avalia riscos **psicossociais** (COPSOQ III, NR-01). DRE avalia riscos
**ergonômicos** (AEP, NR-17). São questionários, fluxos e laudos diferentes,
mas compartilham o mesmo sistema e podem ser enviados à mesma empresa.

**P: Como a equipe SSTG visualiza um questionário sem usar dados de um
colaborador real?**
R: No módulo de questionários, há um botão "👁️ Ver questionário em modo
demonstração", que abre uma versão somente leitura, sem gravar respostas.

**P: Qual é o custo de manter o sistema no ar?**
R: Os planos gratuitos do Streamlit Cloud e do Supabase atendem o uso atual.

---

## 📞 Suporte

**Documentação completa:** módulo **📚 Documentação** dentro do próprio sistema
(TUTORIAL, GUIA_INSTALACAO, GUIA_TECNICO, CHECKLIST_LANCAMENTO).

---

## 📄 Histórico de Versões (resumo)

| Versão | Destaques |
|--------|-----------|
| 6.0 | Versão inicial em CSV/rede local — apenas DRPS (COPSOQ III) |
| 7.0 | Migração para Supabase; adição do módulo DRE (AEP/NR-17) |
| 8.0 | Rebrand "DRE - DRPS"; painel Início com indicadores; metodologia GR v2; modo demonstração; módulo RH simplificado; módulo Documentação |

---

**Última atualização:** 12/06/2026
