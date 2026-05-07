# ✅ Checklist de Lançamento — SSTG - DRPS v6.2

**Data:** 07/05/2026  
**Responsável:** _______________  
**Assinado em:** _______________

---

## 📋 1. Pré-requisitos Técnicos

- [ ] **Python 3.9+** instalado (`py --version`)
- [ ] **Dependências instaladas** (`pip list`):
  - [ ] `streamlit >= 1.28.0`
  - [ ] `pandas >= 2.0.0`
  - [ ] `reportlab >= 4.0.0`
  - [ ] `pillow >= 9.0.0` ← necessário para QR Code
  - [ ] `qrcode[pil] >= 7.4.2` ← necessário para QR Code
- [ ] **Pasta `.streamlit/`** criada
- [ ] **Arquivo `.streamlit/config.toml`** presente e configurado
- [ ] **Arquivos principais presentes:**
  - [ ] `app.py`
  - [ ] `gerar_laudo.py`
  - [ ] `gerar_compartilhamento.py`
  - [ ] `gerar_pdf_publicacao.py`
  - [ ] `requirements.txt`
- [ ] **Arquivos de documentação presentes (raiz do projeto):**
  - [ ] `README.md`
  - [ ] `TUTORIAL.md`
  - [ ] `GUIA_INSTALACAO.md`
  - [ ] `GUIA_TECNICO.md`
  - [ ] `CHECKLIST_LANCAMENTO.md`
  - [ ] `DOCUMENTACAO_PUBLICACAO.md`

---

## ⚙️ 2. Configuração

- [ ] **`DATA_DIR`** definido corretamente
  - [ ] Streamlit Cloud: `./data/` (automático via `__file__`)
  - [ ] Local: caminho para Google Drive ou pasta local
- [ ] **`APP_URL`** configurado para o ambiente atual
- [ ] **`SHARE_URL`** aponta para URL pública do Streamlit Cloud
  - [ ] Testado: links enviados por WhatsApp/e-mail funcionam externamente
- [ ] **`SENHA_ADMIN`** alterada (não usar `sstg2025` em produção)
- [ ] **`DOC_DIR`** resolvido via `os.path.dirname(os.path.abspath(__file__))` — automático
- [ ] **Pasta `data/`** criada e acessível (Streamlit Cloud cria automaticamente)

---

## 📋 3. Módulo Admin (6 Abas)

### Aba 1 — Cadastro / Inclusão
- [ ] Cadastro manual de empresa funciona
- [ ] Senha RH gerada automaticamente após cadastro
- [ ] Senha RH exibida uma única vez com aviso
- [ ] Importação via CSV funciona
- [ ] Senha RH gerada para empresas importadas via CSV
- [ ] Duplicidade bloqueada por CPF + CNPJ (não global)
- [ ] Mesmo CPF aceito em empresas diferentes
- [ ] Links de questionário exibidos corretamente (usam `SHARE_URL`)

### Aba 2 — Conferência e Correção
- [ ] Lista de colaboradores carrega
- [ ] Filtro por empresa funciona
- [ ] Export CSV funciona
- [ ] Gerenciamento de período funciona (alterar datas)
- [ ] **Zona de Perigo — Excluir Empresa:**
  - [ ] Dropdown de empresa funciona
  - [ ] Contadores de impacto exibidos (CPFs e respostas)
  - [ ] Campo de senha admin presente
  - [ ] Senha incorreta bloqueia a ação
  - [ ] Ação remove CPFs do CSV e apaga arquivo de respostas
  - [ ] `st.rerun()` após exclusão atualiza a lista
- [ ] **Zona de Perigo — Resetar Tudo:**
  - [ ] Campo de senha admin presente
  - [ ] Senha incorreta bloqueia a ação
  - [ ] Ação remove todos os CSVs (acessos + respostas)

### Aba 3 — Resultados
- [ ] Seleção de empresa funciona
- [ ] Link público da empresa usa `SHARE_URL`
- [ ] Geração de QR Code funciona
- [ ] Imagem QR Code exibe nome da empresa corretamente
- [ ] QR Code é escaneável (teste com celular)
- [ ] Link dentro do QR Code abre questionário correto
- [ ] Botão WhatsApp abre conversa pré-preenchida
- [ ] Botão E-mail abre cliente com template
- [ ] Download da imagem PNG funciona
- [ ] Médias por dimensão exibidas
- [ ] Histórico de respostas exibido
- [ ] Export CSV de respostas funciona
- [ ] Geração de laudo PDF funciona

### Aba 4 — Movimentação de Pessoal
- [ ] Admissão de novos colaboradores funciona
- [ ] Desligamento (inativação) funciona
- [ ] Colaborador inativo não consegue acessar o questionário
- [ ] Reativação funciona
- [ ] Histórico de respostas preservado após desligamento

### Aba 5 — Segurança e Acesso RH
- [ ] Dropdown de seleção de empresa funciona
- [ ] Botão "Gerar Nova Senha RH" funciona
- [ ] Nova senha exibida uma única vez
- [ ] Nova senha invalida a senha anterior
- [ ] Login RH com nova senha funciona

### Aba 6 — Documentação
- [ ] Todos os 6 documentos listados
- [ ] Botão "Ler" abre o conteúdo `.md` sem erro "Arquivo não encontrado"
- [ ] Conteúdo renderizado em Markdown
- [ ] Botão de fechar documentação funciona
- [ ] Botão "⬇️ PDF" mostra aviso se PDF não gerado (não causa erro)

---

## 📊 4. Módulo Gestão das Respostas (RH)

- [ ] Tela de login exibida ao acessar o módulo
- [ ] Login com CNPJ + senha incorretos rejeitado
- [ ] Login com CNPJ + senha corretos aceito
- [ ] RH autenticado vê apenas dados da sua empresa
- [ ] Link do questionário exibido e correto
- [ ] Geração de QR Code funciona
- [ ] Botão WhatsApp funciona
- [ ] Botão E-mail funciona
- [ ] Dashboard de respostas carrega corretamente
- [ ] Métricas corretas (autorizados, respondidos, taxa)
- [ ] Gráfico de adesão exibido
- [ ] Logout ou navegação para outro módulo funciona

---

## 📋 5. Módulo Questionário Psicossocial

- [ ] Tela de login exibida com informações do protocolo
- [ ] CPF não autorizado rejeitado com mensagem clara
- [ ] CPF inativo rejeitado com mensagem clara
- [ ] CPF já respondeu (na mesma empresa) bloqueado
- [ ] **Mesmo CPF aceito em empresa diferente** ← regra v6.1
- [ ] Período encerrado bloqueia com mensagem de data
- [ ] **Wizard de navegação funciona** — exibe uma demanda por vez ← v6.2
- [ ] 40 questões no total distribuídas em 8 blocos
- [ ] Escala Likert (Nunca → Sempre) funcionando
- [ ] **Botão "Próxima Demanda ▶"** aparece no rodapé de cada bloco ← v6.2
- [ ] Botão bloqueia avanço se há questões não respondidas no bloco atual ← v6.2
- [ ] **Botão "◀ Demanda Anterior"** disponível a partir do bloco 2 ← v6.2
- [ ] Ao voltar ao bloco anterior, respostas já dadas são restauradas ← v6.2
- [ ] Barra de progresso por bloco exibida no topo (Bloco X de 8) ← v6.2
- [ ] Barra de progresso geral exibida no rodapé (X de 40 perguntas) ← v6.2
- [ ] **Sem contaminação entre respondentes** (keys únicas por CPF) ← v6.1
- [ ] Botão ENVIAR desabilitado enquanto há perguntas sem resposta ← v6.2
- [ ] Envio registra respostas corretamente
- [ ] Tela de confirmação após envio

---

## 🔒 6. Segurança

- [ ] Senhas RH armazenadas como hash (não texto puro)
- [ ] CPFs armazenados como hash nas respostas
- [ ] `SENHA_ADMIN` não está em texto puro no código (ou usar variável de ambiente)
- [ ] Arquivo `.gitignore` exclui dados sensíveis se repositório público
- [ ] Acesso RH isolado por empresa
- [ ] Exclusão de dados requer confirmação com senha admin
- [ ] Respostas de respondentes diferentes não se misturam (session_state por CPF)

---

## 🌐 7. Streamlit Cloud

- [ ] Deploy realizado com sucesso
- [ ] URL pública acessível
- [ ] App carrega sem erros no primeiro acesso
- [ ] `SHARE_URL` atualizado com URL de produção
- [ ] Links de compartilhamento testados externamente (fora da rede local)
- [ ] QR Code testado com celular (escaneamento real)
- [ ] App funciona em dispositivo mobile
- [ ] App hiberna e reactiva corretamente

---

## 📱 8. Compatibilidade

- [ ] Chrome Desktop ✅
- [ ] Firefox Desktop ✅
- [ ] Edge Desktop ✅
- [ ] Safari Desktop ✅
- [ ] Chrome Mobile ✅
- [ ] Safari Mobile (iOS) ✅

---

## 📚 9. Documentação

- [ ] README.md atualizado (v6.2, 07/05/2026)
- [ ] TUTORIAL.md atualizado com wizard de navegação e POP 020
- [ ] GUIA_INSTALACAO.md atualizado com pymupdf nas dependências
- [ ] GUIA_TECNICO.md atualizado com arquitetura v6.2
- [ ] CHECKLIST_LANCAMENTO.md atualizado (este documento)
- [ ] DOCUMENTACAO_PUBLICACAO.md atualizado (v6.2)
- [ ] POP020_TUTORIAL_TELAS.pdf presente na raiz do repositório

---

## ✅ Aprovação Final

| Critério | Status | Observações |
|----------|--------|-------------|
| Todos os módulos funcionando | ☐ | |
| Segurança validada | ☐ | |
| Testes em mobile realizados | ☐ | |
| Documentação atualizada | ☐ | |
| Backup configurado | ☐ | |
| URL de produção testada | ☐ | |

**Sistema pronto para produção:** ☐ Sim / ☐ Não  
**Data de aprovação:** _______________  
**Aprovado por:** _______________

---

**Última atualização:** 07/05/2026  
**Versão:** 6.2
