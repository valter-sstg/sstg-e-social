# 📚 SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)

**Versão:** 6.2  
**Atualizado:** 07/05/2026  
**Status:** ✅ Em Produção

---

## 🎯 O que é SSTG - DRPS?

Sistema **web-based** para coleta, análise e geração de **laudos de riscos psicossociais** utilizando o **protocolo COPSOQ III** (Copenhagen Psychosocial Questionnaire), conforme exigência da NR-1.

### Características Principais

✅ **3 Módulos** — Questionário, Gestão RH e Admin  
✅ **Anonimato Garantido** — CPF criptografado com SHA-256  
✅ **Período Controlado** — Janela de resposta configurável por empresa  
✅ **Cadastro em Lote** — Suporte a importação via CSV  
✅ **Links Personalizados** — URL individual por empresa com QR Code  
✅ **Laudo Automático** — PDF gerado com análise de risco  
✅ **Módulo RH** — Acesso seguro por CNPJ + senha para gestão das respostas  
✅ **Wizard de Navegação** — Uma demanda por vez, sem perda de respostas entre blocos  
✅ **LGPD Compliant** — Proteção de dados pessoais  
✅ **Nuvem** — Publicado no Streamlit Cloud, acessível de qualquer lugar  

---

## 🗂️ Módulos do Sistema

### 📋 Questionário Psicossocial
Interface para colaboradores responderem o questionário COPSOQ III:
- Acesso via CPF (autorizado pelo RH)
- 40 questões em 8 dimensões (blocos)
- Escala Likert 5 pontos (Nunca → Sempre)
- **Wizard de navegação** — uma demanda por vez, sem perda de respostas entre blocos
- Botão **"Próxima Demanda ▶"** com validação: só avança se todas as perguntas do bloco estão respondidas
- Botão **"◀ Demanda Anterior"** com restauração das respostas já dadas
- Barra de progresso por bloco (topo) + progresso geral em X/40 questões (rodapé)
- Mesmo CPF pode responder em empresas diferentes (bloqueio por CPF + CNPJ)

### 📊 Gestão das Respostas (RH)
Módulo exclusivo para o departamento de RH de cada empresa:
- Login seguro: **CNPJ + Senha** (gerada automaticamente no cadastro)
- Visualização de respostas e métricas da empresa
- Geração de QR Code para compartilhamento do questionário
- Integração com WhatsApp e E-mail
- Isolamento de dados: cada RH acessa apenas sua própria empresa

### 🔐 Admin SSTG (Gestão)
Painel administrativo com **6 abas**:

| Aba | Função |
|-----|--------|
| 📝 Cadastro / Inclusão | Registrar empresas e colaboradores (manual ou CSV) |
| 📋 Conferência e Correção | Visualizar acessos, gerenciar período, Zona de Perigo |
| 📊 Resultados | Respostas consolidadas, laudo PDF por empresa |
| 🔄 Movimentação de Pessoal | Admissão, desligamento, reativação |
| 🔐 Segurança e Acesso RH | Gerar/redefinir senhas de acesso RH |
| 📚 Documentação | Guias, tutoriais e POP 020 (visualizável e baixável) |

---

## 📖 Documentação

### Para Usuários RH
**👉 [TUTORIAL.md](TUTORIAL.md)** — Guia operacional completo  
- Acesso ao módulo RH, login, compartilhamento, análise de respostas

### Para Administradores de Sistema
**👉 [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)** — Instalação, setup e manutenção  
- Dependências, configuração, publicação no Streamlit Cloud, backup

### Para Desenvolvedores / Técnicos
**👉 [GUIA_TECNICO.md](GUIA_TECNICO.md)** — Arquitetura, fluxos e segurança  
- Stack, estrutura de dados, funções, segurança, troubleshooting

---

## ⚡ Início Rápido

### 1️⃣ Instalação (5 min)

```bash
# Instale dependências
pip install streamlit pandas reportlab pillow "qrcode[pil]"

# Inicie o app
streamlit run app.py
```

**URL de acesso:**
```
http://localhost:8501
```

### 2️⃣ Primeiro Cadastro (3 min)

1. Acesse o app
2. Selecione: **🔐 Admin SSTG (Gestão)**
3. Digite senha: `sstg2025`
4. Aba **📝 Cadastro / Inclusão** → preencha CNPJ, empresa e colaboradores
5. Clique **✅ SALVAR E LIBERAR ACESSOS**
6. O sistema gera automaticamente a **senha de acesso RH** — anote e envie ao RH

### 3️⃣ Distribuir Links (2 min)

1. Na **Aba 1** → **🔗 Link do Questionário para Compartilhar**
2. Copie o link da empresa
3. Envie por WhatsApp, e-mail ou gere o QR Code na **Aba 3 → Resultados**

### 4️⃣ Colaborador Responde (~10 min)

1. Colaborador acessa o link ou escaneia o QR Code
2. Digita seu CPF (11 dígitos)
3. Responde as **40 questões** (8 blocos)
4. Envia as respostas

### 5️⃣ RH Visualiza Respostas

1. Acesse: **📊 Gestão das Respostas (RH)**
2. Informe CNPJ e senha gerada no cadastro
3. Visualize métricas, gráficos e compartilhe o questionário

### 6️⃣ Gerar Laudo (2 min)

1. Admin → **Aba Resultados**
2. Selecione a empresa
3. Clique **📄 GERAR E BAIXAR LAUDO PDF**

---

## 🏗️ Arquitetura Resumida

```
┌─────────────────────────────────────┐
│     Navegador Web (Qualquer SO)     │
│         Streamlit Frontend          │
└────────────────┬────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────┐
│    Python Streamlit Application     │
│  • app.py (3 módulos)               │
│  • gerar_laudo.py (PDF)             │
│  • gerar_compartilhamento.py (QR)   │
└────────────────┬────────────────────┘
                 │ I/O
┌────────────────▼────────────────────┐
│    Armazenamento CSV                │
│  • db_acessos_autorizados.csv       │
│  • respostas_CNPJ_XXXXX.csv         │
└─────────────────────────────────────┘
```

---

## 🔒 Segurança & LGPD

| Aspecto | Implementação |
|--------|---------------|
| **Anonimato** | CPF → SHA-256 hash (impossível recuperar) |
| **Acesso RH** | CNPJ + Senha com hash SHA-256 |
| **Senha Segura** | Gerada com `secrets` module (criptograficamente seguro) |
| **Controle de Acesso** | Período configurável (data início/fim) |
| **Isolamento** | RH acessa apenas dados da própria empresa |
| **Inativação** | Colaboradores inativados perdem acesso |
| **Exclusão** | Admin pode excluir empresa + histórico com confirmação |

---

## 📊 Dimensões COPSOQ III (8 Blocos, 40 Questões)

| # | Dimensão | Questões | Invertida? |
|---|----------|----------|-----------|
| 1️⃣ | **📦 Cargo** | 5 | Não |
| 2️⃣ | **🎮 Controle** | 6 | Não |
| 3️⃣ | **⚖️ Demandas** | 8 | ✅ Sim |
| 4️⃣ | **⚠️ Relacionamentos** | 4 | ✅ Sim |
| 5️⃣ | **🤝 Apoio Colegas** | 4 | Não |
| 6️⃣ | **👔 Apoio Chefia** | 5 | Não |
| 7️⃣ | **📢 Comunicação** | 3 | Não |
| 8️⃣ | **🔄 Mudanças** | 5 | Não |

**Total:** 40 questões, escala Likert 5 pontos (Nunca → Sempre)

---

## 🚀 Deployment

### Opção 1: Streamlit Cloud (Produção)

**URL Pública:**
```
https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app
```

✅ Acesso global | ✅ HTTPS automático | ✅ Deploy via GitHub

### Opção 2: Rede Local (Desenvolvimento)

```bash
streamlit run app.py
# Acesse: http://localhost:8501
```

---

## 🛠️ Tecnologias Utilizadas

```
Frontend:      Streamlit 1.28+
Backend:       Python 3.9+
Data:          Pandas, CSV
PDF:           ReportLab 4.0+
QR Code:       qrcode + Pillow (PIL)
Visualiz. PDF: PyMuPDF (pymupdf) — renderização página a página
Segurança:     SHA-256, secrets module
Deployment:    Streamlit Cloud / GitHub
```

---

## 📱 Compatibilidade

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ | ✅ |
| Edge | ✅ | ✅ |

---

## ❓ FAQ Rápido

**P: Preciso de banco de dados?**  
R: Não, CSV é suficiente. Dados persistem no Streamlit Cloud via `./data/`.

**P: Os dados estão seguros?**  
R: Sim. CPF é criptografado (SHA-256) e senhas RH são armazenadas como hash — nunca em texto puro.

**P: Um colaborador pode responder por duas empresas?**  
R: Sim. O mesmo CPF pode ser cadastrado e responder em empresas diferentes. O bloqueio de duplicidade é por CPF + CNPJ.

**P: Como o RH acessa os resultados?**  
R: Pelo módulo **📊 Gestão das Respostas (RH)** com CNPJ + senha fornecida pelo Admin SSTG.

**P: Como recuperar a senha RH de uma empresa?**  
R: Admin acessa **Segurança e Acesso RH**, seleciona a empresa e clica em **Gerar Nova Senha**.

**P: Posso excluir uma empresa e seus dados?**  
R: Sim. Na aba **Conferência → Zona de Perigo → Excluir Empresa**, com confirmação obrigatória da senha Admin.

**P: Qual é o custo?**  
R: Gratuito. Streamlit Cloud tem versão free. Código open-source no GitHub.

---

## 📞 Suporte

- [TUTORIAL.md](TUTORIAL.md) — Para usuários RH
- [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md) — Para admins
- [GUIA_TECNICO.md](GUIA_TECNICO.md) — Para desenvolvedores

---

**Última atualização:** 07/05/2026  
**Versão:** 6.2  
**Próxima revisão:** 07/08/2026
