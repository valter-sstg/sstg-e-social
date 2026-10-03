# 👥 DRE - DRPS — Tutorial Operacional

**Versão:** 8.0
**Atualizado:** 14/07/2026
**Público:** Equipe SSTG | RH das empresas atendidas

---

## 📋 Índice

1. [Visão Geral do Menu](#visão-geral-do-menu)
2. [Equipe SSTG — Módulo Admin](#equipe-sstg--módulo-admin)
3. [RH da Empresa — Gestão das Respostas](#rh-da-empresa--gestão-das-respostas)
4. [Colaborador — Questionários DRE-DRPS](#colaborador--questionários-dre-drps)
5. [Módulo Início (Dashboard)](#módulo-início-dashboard)
6. [Módulo Documentação](#módulo-documentação)
7. [Compartilhamento com QR Code](#compartilhamento-com-qr-code)
8. [Exportação de Laudos (PDF e DOCX)](#exportação-de-laudos-pdf-e-docx)
9. [FAQ e Troubleshooting](#faq-e-troubleshooting)

---

## 🔓 Visão Geral do Menu

Ao abrir o link do sistema, o menu lateral ("Módulo:") mostra:

| Módulo | Quem acessa |
|--------|-------------|
| 🏠 Início | Todos (dashboard geral) |
| 📝 Questionários DRE-DRPS | Colaboradores (via link enviado pelo RH) |
| 📊 Gestão das Respostas (RH) | RH da empresa (CNPJ + senha) |
| 📚 Documentação | Equipe SSTG (login Admin) |
| 🔐 Admin SSTG (Gestão) | Equipe SSTG (login Admin) |

Se o link aberto contiver `?cnpj=...` ou `?modulo=aep`, o sistema já abre
diretamente no módulo **Questionários DRE-DRPS** — é assim que os
colaboradores acessam.

---

## 🛠️ Equipe SSTG — Módulo Admin

### Login

Selecione **🔐 Admin SSTG (Gestão)** no menu lateral. Existem dois tipos de acesso:

| Perfil | Como entra | O que pode fazer |
|--------|------------|-------------------|
| **Administrador** | usuário `admin` + senha da equipe SSTG | Acesso total, incluindo a aba 👥 Usuários e a ⚠️ Zona de Perigo |
| **Operacional** | usuário + senha criados pelo administrador (aba 👥 Usuários) | Acesso às demais abas (cadastro, conferência, resultados, segurança, movimentação) |

> 🔑 A senha do administrador pode ser alterada dentro do próprio módulo
> (opção "Alterar Senha"). Guarde-a em local seguro — ela não aparece em
> nenhuma tela após ser definida.

Após o login, ficam disponíveis 7 abas:

| Aba | Para quê |
|-----|----------|
| 🆕 Cadastro / Inclusão | Cadastrar empresas e colaboradores |
| 📋 Conferência e Correção | Consultar/editar cadastros, período, backup |
| 📊 Resultados DRPS | Acompanhar respostas e gerar o laudo Psicossocial |
| 🦴 Resultados DRE | Acompanhar respostas e gerar o laudo Ergonômico |
| 🔄 Movimentação de Pessoal | Inativar/reativar colaboradores |
| 🔐 Segurança e Acesso RH | Gerar a senha de acesso do RH de cada empresa |
| 👥 Usuários | Gerenciar usuários da equipe SSTG (admin only) |

---

### 🆕 Aba 1 — Cadastro / Inclusão

#### Passo 1: Dados da Empresa

Preencha:

```
CNPJ (somente números)        Razão Social
[__________________]          [___________________]

CNAE Principal                 Grau de Risco (NR-4)
[__________________]          [— | 1 | 2 | 3 | 4]

Data de início do período      Data de encerramento
[__________]                   [__________]
```

> ⚠️ **Grau de Risco (NR-4):** este campo é importante para o laudo **DRE**.
> Ele define a tabela de severidades usada no cálculo do Grau de Risco (GR)
> de cada item do inventário ergonômico. Se não souber, deixe "—" — o
> sistema usa a tabela padrão (GR 1-2).
>
> ⚠️ Fora do período definido, os colaboradores **não conseguem** responder
> aos questionários.

#### Passo 2: Colaboradores — Manual ou CSV

Escolha entre **✏️ Entrada Manual** (adicionar linha por linha) ou
**📊 Importar via CSV** (recomendado para 10+ colaboradores).

**Entrada manual** — adicione uma linha por colaborador:

```
╔═══════════════════════════════════════════════════════╗
║  CPF (11 dígitos)  │  Função / Cargo  │ Departamento  ║
╠═══════════════════════════════════════════════════════╣
║ [06320453451]      │ [Assist. Adm]    │ [Atendimento] ║
║ [70164124403]      │ [Assist. ST]     │ [Seg. Trab.]  ║
╚═══════════════════════════════════════════════════════╝
```

**Importação via CSV** — baixe o template, preencha em Excel/Bloco de Notas
e faça upload. O arquivo deve ter as colunas, separadas por `;`:

```csv
CPF;Função;Departamento
06320453451;Assist. Adm;Atendimento
70164124403;Assist. ST;Seg. Trabalho
```

> **⚠️ Importante:** CPF com exatamente 11 dígitos, sem pontos ou traços.

#### Passo 3: Salvar e Gerar Links

Clique em **✅ SALVAR E LIBERAR ACESSOS**. O sistema cadastra os colaboradores
(avisando sobre CPFs já existentes ou inválidos) e exibe **dois links**, um
para cada questionário:

```
┌─────────────────────────────────────────────────────────────────┐
│  🔗 Links para Compartilhar — Empresa XYZ                        │
├─────────────────────────────────────────────────────────────────┤
│  📋 Questionário DRPS (Psicossocial)                              │
│  https://valter-sstg.github.io/sstg-e-social/                │
│      questionario_psicossocial.html?cnpj=XXXXXXXXXXXXXX          │
│                                                                   │
│  🦴 Questionário DRE (Ergonômico)                                 │
│  https://valter-sstg.github.io/sstg-e-social/                │
│      questionario_aep.html?cnpj=XXXXXXXXXXXXXX                   │
└─────────────────────────────────────────────────────────────────┘
```

Copie e envie cada link aos colaboradores (WhatsApp, e-mail, etc.). O link
DRPS abre o questionário Psicossocial; o link DRE abre o Ergonômico.

---

### 📋 Aba 2 — Conferência e Correção

- **Métricas no topo:** Total de CPFs, Ativos, Inativos, data do último cadastro.
- **Filtro por empresa:** selecione uma empresa ou deixe em branco para ver todas.
- **Tabela de cadastros:** todos os colaboradores e seus dados/status.
- **📅 Gerenciar Período de Aplicação** (expander): altere as datas de
  início/fim para reabrir ou encerrar a resposta de uma empresa.
- **💾 Backup** (expander): exporta um ZIP com todos os dados em CSV.
- **⚠️ Zona de Perigo** (expander, apenas administrador): excluir os dados
  de uma empresa (cadastros e respostas) ou resetar o banco. **Use com
  extremo cuidado — ação irreversível.**

---

### 🔐 Aba — Segurança e Acesso RH

Antes que o RH de uma empresa possa acessar o módulo **📊 Gestão das
Respostas (RH)**, a equipe SSTG precisa gerar uma senha de acesso:

1. Selecione a empresa.
2. Clique em **🔐 Gerar Nova Senha RH**.
3. O sistema gera uma senha de 8 caracteres (letras maiúsculas e números) e
   exibe **uma única vez** na tela.
4. Anote/copie a senha e envie ao RH junto com o CNPJ da empresa.

> ⚠️ Se a senha for perdida, basta gerar uma nova — a anterior deixa de
> funcionar.

---

### 📊 Aba — Resultados DRPS

- KPIs: CPFs autorizados, respostas recebidas, taxa de adesão.
- Gráfico de adesão (autorizados x respondidos).
- Gráfico de médias por dimensão do COPSOQ III.
- Tabela com o histórico completo de respostas (anônimo, por CPF_Hash).
- Botão **📄 Gerar Laudo DRPS em PDF** — gera o laudo completo (escopo,
  metodologia, inventário por dimensão, plano de ação e conclusão) e
  disponibiliza para download.

---

### 🦴 Aba — Resultados DRE

- KPIs: CPFs autorizados, respostas recebidas, taxa de adesão.
- Gráfico de % de risco por seção (A. Postura, B. Mobiliário, C. Ambiente,
  D. Organização do Trabalho).
- **Inventário de Riscos** (somente leitura), com uma linha por item (1-17):

| Nº | Seção | Risco Identificado | % Risco | Severidade | Probabilidade | GR | Classificação | Plano? |
|----|-------|---------------------|---------|------------|-----------------|----|----------------|--------|

  - **Severidade** vem pré-calibrada conforme o **Grau de Risco (NR-4)**
    cadastrado para a empresa.
  - **Probabilidade** é calculada a partir do % de respostas com risco.
  - **GR = Severidade × Probabilidade** (veja a fórmula completa no
    README.md, seção "Metodologia de Grau de Risco").
  - **Plano? = SIM** a partir da classificação Médio.

- Botão **📄 Gerar Laudo DRE em PDF** — gera o laudo completo (escopo,
  metodologia, inventário com GR, matriz/plano de ação, necessidade de AET
  e conclusão).

---

### 🔄 Aba — Movimentação de Pessoal

Para desligar um colaborador sem apagar o histórico:

1. Selecione a empresa e o CPF.
2. Informe o motivo (opcional, ex.: "Desligado em 12/06/2026").
3. Clique em **🚫 Inativar Colaborador**.

O colaborador inativado não consegue mais responder aos questionários. Para
restaurar o acesso, use a opção **✅ Reativar** na mesma aba.

---

### 👥 Aba — Usuários (apenas administrador)

Permite gerenciar os logins **operacionais** da equipe SSTG:

- **Criar usuário:** login, nome e senha (mínimo 6 caracteres).
- **Listar usuários:** veja quem está ativo/inativo.
- **Ativar/Desativar:** suspende o acesso sem excluir o usuário.
- **Redefinir senha:** gera uma nova senha para um usuário específico.

---

## 🏢 RH da Empresa — Gestão das Respostas

### Login

1. Acesse o link do sistema.
2. Menu **📊 Gestão das Respostas (RH)**.
3. Informe o **CNPJ** da empresa e a **senha RH** (recebida da equipe SSTG).

### O que você encontra

- Indicadores de adesão (quantos colaboradores já responderam).
- **E-books de apoio** — materiais explicativos sobre os programas
  Psicossocial e Ergonômico, com seus respectivos links de download. Esses
  são os únicos materiais que o RH compartilha por aqui — os links dos
  questionários ficam a cargo da equipe SSTG (aba Cadastro/Inclusão).

### Navegação

Após os e-books, há dois controles de navegação:

- **🔄 Trocar de empresa** (visível apenas para a equipe SSTG): permite
  alternar entre empresas sem precisar sair e fazer login novamente.
- **↩ Voltar à tela inicial**: encerra o acesso do RH e retorna à tela de
  login do módulo (equivalente a "Sair").

---

## 👤 Colaborador — Questionários DRE-DRPS

### Acesso

O colaborador recebe um link específico:

- **DRPS (Psicossocial):** `...questionario_psicossocial.html?cnpj=...`
- **DRE (Ergonômico):** `...questionario_aep.html?cnpj=...`

Ao abrir o link, o sistema já seleciona o questionário correto. A tela de
acesso pede o **CPF** (11 dígitos, sem pontos ou traços).

### Validações

| Situação | Mensagem |
|----------|----------|
| CPF não cadastrado | Seu CPF não está autorizado |
| Colaborador inativado | Seu acesso está inativo |
| Antes do período | O questionário ainda não foi aberto |
| Depois do período | O período de resposta encerrou — contate o RH |
| Já respondeu | Você já participou desta avaliação |
| Tudo OK | Abre o questionário |

### 👁️ Modo Demonstração (equipe SSTG)

Na tela de acesso, usuários logados como equipe SSTG (Admin) veem um botão
extra: **👁️ Ver questionário em modo demonstração**. Ele abre o questionário
completo em modo **somente leitura** — útil para mostrar o sistema a um
cliente sem usar dados reais e sem gravar nenhuma resposta. Para sair, use o
botão **↩ Voltar / Encerrar**.

### Questionário DRPS — 7 blocos / 35 questões

| Bloco | Tema | Questões |
|-------|------|----------|
| 📦 Cargo | Clareza da função | 5 |
| 🎮 Controle | Autonomia de decisão | 6 |
| ⚖️ Demandas | Pressão e carga | 8 |
| ⚠️ Relacionamentos | Conflitos e assédio | 4 |
| 🤝 Apoio dos Colegas | Solidariedade | 4 |
| 👔 Apoio da Chefia | Suporte gerencial | 5 |
| 📢 Comunicação e Mudanças | Transparência | 3 |

Cada questão usa escala Likert de 5 pontos (Nunca → Sempre). É possível
navegar entre blocos antes de enviar.

### Questionário DRE — 4 seções / 17 questões

| Seção | Tema |
|-------|------|
| A. Postura e Movimentos | Como você usa o corpo no trabalho |
| B. Mobiliário e Equipamentos | Mesas, cadeiras e ferramentas |
| C. Condições Ambientais | Iluminação, ruído, temperatura |
| D. Organização do Trabalho | Ritmo, pausas, jornada |

Cada pergunta tem um texto principal e uma linha de ajuda em linguagem
simples. Ao final, há duas perguntas abertas (relato de dor/incômodo e
sugestões de melhoria).

### Envio

Ao concluir, o colaborador clica em **✅ ENVIAR** e recebe a confirmação de
que as respostas foram salvas de forma anônima.

---

## 🏠 Módulo Início (Dashboard)

A tela inicial mostra uma visão geral do uso do sistema:

- **Cards de indicadores:** 🏢 CNPJs cadastrados · 👥 CPFs cadastrados ·
  📋 Questionários respondidos (DRPS + DRE) · 📄 Laudos gerados.
- **Gráfico de evolução:** quantidade acumulada de respostas por mês.
- **Gráfico de laudos:** quantidade de laudos DRPS x DRE já gerados.

---

## 📚 Módulo Documentação

O módulo **📚 Documentação** reúne todos os guias e tutoriais do sistema em um único lugar, acessível apenas para a equipe SSTG (após login no Admin).

### Conteúdo Disponível

| Documento | Para quem | O quê |
|-----------|-----------|-------|
| **TUTORIAL.md** | Equipe SSTG + RH | Tutorial operacional (este arquivo) — como usar cada módulo |
| **GUIA_INSTALACAO.md** | Administradores | Como publicar/atualizar o sistema, configurar credenciais, backup |
| **GUIA_TECNICO.md** | Desenvolvedores | Arquitetura, banco de dados, fluxos de dados, fórmulas do GR |
| **CHECKLIST_LANCAMENTO.md** | Administradores | Checklist de verificação antes de publicar uma nova versão |
| **README.md** | Todos | Visão geral do projeto e características principais |

### Como Acessar

1. Menu lateral → **📚 Documentação**
2. Você verá os links para cada guia em formato PDF ou Markdown
3. Clique para visualizar, download ou impressão

> 💡 **Dica:** Mantenha estes guias atualizados conforme o sistema evolui. Qualquer mudança
> significativa deve ser registrada aqui para facilitar o treinamento de novos usuários
> e a manutenção futura do sistema.

---

## 🎨 Compartilhamento com QR Code

A equipe SSTG pode gerar **imagens de compartilhamento com QR Code** para distribuir aos clientes. Essas imagens contêm o logo SSTG, o nome da empresa e um QR Code que leva direto aos questionários.

### Como Gerar

1. **Admin SSTG** → aba **🆕 Cadastro / Inclusão**
2. Após salvar a empresa e colaboradores, na seção **🔗 Links para Compartilhar**, clique em:
   - **📸 Gerar Imagem de Compartilhamento (DRPS)** — cria PNG com QR para Psicossocial
   - **📸 Gerar Imagem de Compartilhamento (DRE)** — cria PNG com QR para Ergonômico

### Características da Imagem

- ✅ Logo SSTG no topo (cabeçalho azul navy)
- ✅ Nome da empresa em destaque (texto verde grande)
- ✅ QR Code centralizado (600x600 px)
- ✅ Rodapé com identificação
- ✅ Dimensões: 1280 × altura variável (conforme tamanho do nome)
- ✅ Formato PNG (pronto para impressão ou digital)

### Usos

| Situação | Como usar |
|----------|-----------|
| **WhatsApp/Telegram** | Envie a imagem pelo chat (mais visual que um link texto) |
| **E-mail** | Anexe a imagem junto com instruções |
| **Cartaz/Mural** | Imprima e fixe nas dependências da empresa |
| **Apresentação** | Inclua no slide de apresentação do programa |

> ⚠️ **Nota:** O QR Code leva apenas ao link do questionário; não carrega dados de login.
> O CPF ainda deve ser informado ao abrir o link.

---

## 📄 Exportação de Laudos (PDF e DOCX)

Os laudos podem ser gerados em dois formatos: **PDF** (padrão) e **DOCX** (editável no Word).

### Geração de Laudo DRPS (Psicossocial)

1. **Admin SSTG** → aba **📊 Resultados DRPS**
2. Selecione a empresa
3. Clique em **📄 Gerar Laudo DRPS em PDF** (ou DOCX, se disponível)

**Conteúdo do Laudo DRPS:**
- Escopo e metodologia (COPSOQ III, NR-01)
- Tabela de respostas por dimensão
- Gráficos de risco (baixo/médio/alto)
- Inventário de riscos por dimensão
- Plano de ação recomendado
- Conclusão e assinatura

### Geração de Laudo DRE (Ergonômico)

1. **Admin SSTG** → aba **🦴 Resultados DRE**
2. Selecione a empresa
3. Clique em **📄 Gerar Laudo DRE em PDF** (ou DOCX, se disponível)

**Conteúdo do Laudo DRE:**
- Escopo e metodologia (AEP, NR-17)
- Inventário de Riscos Ergonômicos (17 itens)
- Cálculo de Grau de Risco (GR) para cada item
- Classificação (Baixo / Médio / Alto / Crítico)
- Plano de ação conforme classificação
- Recomendação de AET (Análise Ergonômica do Trabalho) se necessário
- Conclusão

### Diferenças entre PDF e DOCX

| Aspecto | PDF | DOCX |
|---------|-----|------|
| **Formato** | Fixa, não editável | Editável no MS Word |
| **Uso** | Compartilhamento, arquivo | Ajustes finais, customização |
| **Assinatura** | Digital ou impressa | Inserir campos de assinatura |
| **Compatibilidade** | Universal | Requer MS Word ou alternativa |

> 💡 **Dica:** Gere o PDF para arquivo permanente e o DOCX se precisar fazer ajustes
> ou adicionar assinaturas digitais do RT (Responsável Técnico) e médico do trabalho.

### Armazenamento de Laudos

Todos os laudos gerados ficam registrados no banco de dados (tabela `laudos`), com:
- Data e hora de geração
- Versão do sistema (v8.0)
- Tipo (DRPS ou DRE)
- Formato (PDF ou DOCX)

Para consultar histórico de laudos, veja a aba **📋 Conferência e Correção** → expander **💾 Backup**.

---

## ❓ FAQ e Troubleshooting

### P1: "Seu CPF não está autorizado"

**Causa:** o CPF não foi cadastrado (ou foi cadastrado para outra empresa).

**Solução:**
1. Aba **📋 Conferência e Correção** → procure o CPF.
2. Se não existir, cadastre na aba **🆕 Cadastro / Inclusão**.
3. Verifique se não há erro de digitação (pontos/traços não são aceitos).

---

### P2: "O período de resposta encerrou"

**Solução:**
1. Aba **📋 Conferência e Correção** → expander **📅 Gerenciar Período de Aplicação**.
2. Selecione a empresa e ajuste as datas.

---

### P3: "Você já participou desta avaliação"

Isso é esperado — o sistema impede respostas duplicadas. Cada colaborador
responde uma vez por período, para cada questionário (DRPS e DRE são
independentes).

---

### P4: Erro ao importar CSV: "CPF inválido"

```
✅ Correto:   06320453451
❌ Errado:    6320453451       (10 dígitos)
❌ Errado:    063.204.534-51   (com pontos/traços)
```

---

### P5: O RH não consegue entrar no módulo "Gestão das Respostas"

**Causa mais comum:** a senha RH ainda não foi gerada (ou foi perdida).

**Solução:** Admin → aba **🔐 Segurança e Acesso RH** → selecione a empresa →
**🔐 Gerar Nova Senha RH** → envie CNPJ + nova senha ao RH.

---

### P6: Como mostrar o sistema a um cliente sem usar dados reais?

Use o botão **👁️ Ver questionário em modo demonstração**, disponível na tela
de acesso do módulo Questionários DRE-DRPS para quem está logado como equipe
SSTG.

---

### P7: Como alterar a senha do administrador?

Dentro do módulo **🔐 Admin SSTG (Gestão)**, use a opção "Alterar Senha".
Apenas administradores conseguem fazer isso (usuários operacionais não têm
essa opção).

---

### P8: Como usar o QR Code de compartilhamento?

1. Gere a imagem PNG na aba **Cadastro/Inclusão** após salvar uma empresa.
2. Compartilhe por WhatsApp, e-mail ou imprima para mural.
3. Quem escanear o QR Code será levado direto ao questionário correspondente (DRPS ou DRE).
4. Ainda assim, o colaborador precisa informar o CPF para validar e responder.

---

### P9: Qual é a diferença entre exportar em PDF e DOCX?

- **PDF:** Formato fixo, ideal para arquivo permanente, compartilhamento seguro (não editável).
- **DOCX:** Formato editável, útil se precisar fazer ajustes, adicionar assinaturas digitais ou
  customizar antes de enviar ao cliente.

Recomendação: gere ambos — PDF para arquivo, DOCX para possíveis ajustes.

---

### P10: Os laudos são salvos automaticamente?

Sim. Cada laudo gerado fica registrado no banco de dados com data/hora e tipo (DRPS/DRE).
Você pode consultar o histórico na aba **📋 Conferência e Correção** → expander **💾 Backup**.

---

### P11: Como acessar os guias técnicos dentro do sistema?

Menu → **📚 Documentação** (apenas para equipe SSTG logada).
Lá você encontra TUTORIAL, GUIA_INSTALACAO, GUIA_TECNICO e CHECKLIST_LANCAMENTO em PDF/Markdown.

---

### P12: Posso editar um laudo DOCX e refazer sem perder o histórico?

Sim. O histórico de laudos fica no banco de dados independente de qualquer edição local.
Você pode editar o DOCX quantas vezes quiser — a versão original sempre fica registrada.

---

## 📞 Suporte

Para dúvidas técnicas, consulte o **🔧 GUIA_TECNICO.md** ou contate a equipe
SSTG responsável pela manutenção do sistema.

---

**Sistema versão 8.0** — DRE - DRPS
**Última atualização:** 03/10/2026 (adições: Módulo Documentação, Compartilhamento com QR Code, Exportação DOCX)
