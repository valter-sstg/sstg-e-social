# 📚 SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1) — Tutorial Operacional

**Versão:** 6.1  
**Data:** 05/05/2026  
**Público:** Equipe de Gestão RH | Pessoal Administrativo | Usuários Finais

---

## 📋 Índice

1. [Acesso ao Sistema](#acesso-ao-sistema)
2. [Módulo Admin — Gestão de Empresas](#módulo-admin)
3. [Cadastro Manual](#cadastro-manual)
4. [Cadastro via CSV (Em Lote)](#cadastro-via-csv)
5. [Gerar Links e QR Code](#gerar-links-e-qr-code)
6. [Módulo RH — Gestão das Respostas](#módulo-rh)
7. [Módulo Colaborador — Responder Questionário](#módulo-colaborador)
8. [Consultar Resultados e Laudo PDF](#consultar-resultados)
9. [Segurança e Acesso RH](#segurança-e-acesso-rh)
10. [Zona de Perigo — Exclusão de Dados](#zona-de-perigo)
11. [Movimentação de Pessoal](#movimentação-de-pessoal)
12. [Documentação Integrada](#documentação-integrada)
13. [FAQ e Troubleshooting](#faq-e-troubleshooting)

---

## 🔓 Acesso ao Sistema

### URL de Acesso

#### Online — Streamlit Cloud (Produção)

```
https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app
```

✅ Acesso de qualquer lugar | ✅ HTTPS | ✅ Sempre disponível

#### Local (Desenvolvimento)

```
http://localhost:8501
```

> ⚠️ Apenas quando o app está rodando na máquina local.

### Módulos Disponíveis

Na barra lateral, selecione o módulo desejado:

```
Módulo:
⭕ 📋 Questionário Psicossocial
⭕ 📊 Gestão das Respostas (RH)
🔴 🔐 Admin SSTG (Gestão)        ← selecionado
```

---

## 🛠️ Módulo Admin

### Autenticação

**Campo:** Senha de Administrador  
**Valor padrão:** `sstg2025`

> ⚠️ **Segurança:** Altere a senha padrão assim que possível.

### Interface Principal

Após login, você verá **6 abas**:

| Aba | Descrição |
|-----|-----------|
| **📝 Cadastro / Inclusão** | Registrar novas empresas e colaboradores |
| **📋 Conferência e Correção** | Visualizar, gerenciar acessos, Zona de Perigo |
| **📊 Resultados** | Respostas consolidadas, laudos PDF, QR Code |
| **🔄 Movimentação de Pessoal** | Admissão, desligamento, reativação |
| **🔐 Segurança e Acesso RH** | Gerar/redefinir senhas de acesso RH |
| **📚 Documentação** | Guias e tutoriais integrados |

---

## 📝 Cadastro Manual

### Passo 1: Selecionar Método

Na **Aba 1 — Cadastro / Inclusão**, selecione: **✏️ Entrada Manual**

### Passo 2: Preencher Dados da Empresa

```
CNPJ (somente números)           Razão Social
[__________________]             [___________________]
Ex: 49405001000105               Ex: Empresa Exemplo Ltda
```

### Passo 3: Definir Período de Aplicação

```
Data de início                   Data de encerramento
[__________]                     [__________]
Ex: 05/05/2026                   Ex: 05/06/2026
```

> ⚠️ Fora desse período, colaboradores **não** conseguem acessar o questionário.

### Passo 4: Adicionar Colaboradores

Clique em **➕ Adicionar linha** para cada colaborador:

```
╔════════════╦══════════════╦═══════════════╗
║ CPF        ║ Função       ║ Departamento  ║
╠════════════╬══════════════╬═══════════════╣
║ 06320453451║ Assist. Adm  ║ Atendimento   ║
║ 70164124403║ Analista RH  ║ RH            ║
╚════════════╩══════════════╩═══════════════╝
```

- **CPF:** 11 dígitos, sem pontos ou traços
- **Função e Departamento:** opcionais, mas recomendados

### Passo 5: Salvar

Clique em: **✅ SALVAR E LIBERAR ACESSOS**

Após salvar, o sistema exibe automaticamente:

```
🔐 Credenciais de Acesso RH
Empresa: Empresa Exemplo Ltda
CNPJ: 49405001000105
Senha de Acesso RH: A7K9M2P5
⚠️ Anote esta senha com segurança! Esta é a única vez que ela será exibida.
```

> **Importante:** Salve e envie a senha ao responsável de RH da empresa. Ela não poderá ser recuperada — apenas substituída por uma nova.

---

## 📊 Cadastro via CSV

### Quando Usar

✅ Ideal para cadastro de 10+ colaboradores ou importação em lote.

### Passo 1: Baixar Template

Na **Aba 1**, clique em: **⬇️ Baixar Template CSV**

### Passo 2: Preencher Arquivo

```csv
CPF;Função;Departamento
06320453451;Desenvolvedor;TI
70164124403;Analista;RH
29545382449;Coordenador;Administrativo
```

> ⚠️ Separador: `;` | CPF: 11 dígitos sem pontos ou traços

### Passo 3: Preencher Dados da Empresa

CNPJ, Razão Social e Período (igual ao cadastro manual).

### Passo 4: Upload e Confirmação

Faça o upload do CSV e clique em: **💾 SALVAR COLABORADORES DO CSV**

Resultado esperado:
```
✅ 3 colaborador(es) cadastrado(s) com sucesso.
🔐 Credenciais de Acesso RH geradas automaticamente.
⚠️ CPF(s) já cadastrados nesta empresa: [lista]
❌ CPF(s) inválidos: [lista]
```

> **Nota:** O mesmo CPF pode ser cadastrado em **empresas diferentes**. O bloqueio de duplicidade é por CPF + CNPJ.

---

## 🔗 Gerar Links e QR Code

### Links para Compartilhar

Na **Aba 1**, role até **🔗 Link do Questionário para Compartilhar**:

```
Empresa Exemplo Ltda
https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app/?cnpj=49405001000105
```

Copie e envie o link ao RH da empresa para distribuição.

### Gerar QR Code (Aba Resultados)

Na **Aba 3 — Resultados**:

1. Selecione a empresa
2. Expanda: **🖼️ Gerar QRCode do Questionário para Compartilhamento**
3. Clique em: **🎨 Gerar Imagem com QR Code**

A imagem gerada (1280×720 px) contém:
- Logo e nome da empresa em destaque
- QR Code escaneável com link direto
- Design profissional pronto para distribuição

**Opções de compartilhamento disponíveis:**

| Canal | Botão |
|-------|-------|
| WhatsApp | 📱 Enviar via WhatsApp |
| E-mail | 📧 Enviar via Email |
| Download | ⬇️ Baixar Imagem (PNG) |

---

## 📊 Módulo RH — Gestão das Respostas

### O que é este módulo?

O módulo **📊 Gestão das Respostas (RH)** permite que o departamento de RH de cada empresa acesse os dados da pesquisa, compartilhe o questionário com colaboradores e visualize métricas — **sem precisar de acesso administrativo**.

### Como Acessar

1. Na barra lateral, selecione: **📊 Gestão das Respostas (RH)**
2. Informe seu **CNPJ** (formato: XX.XXX.XXX/0001-XX)
3. Informe a **Senha RH** recebida do administrador SSTG
4. Clique em **Acessar**

### Obtendo as Credenciais

- **Primeiro acesso:** A senha é gerada automaticamente no momento do cadastro da empresa e exibida ao Admin SSTG
- **Senha perdida:** Solicite ao administrador SSTG que acesse **Segurança e Acesso RH → Gerar Nova Senha**

### O que o RH pode fazer

Após o login, o RH tem acesso a:

#### 1. Link do Questionário
Visualiza o link público do questionário da empresa para distribuição.

#### 2. QR Code para Compartilhamento
Gera imagem profissional com QR Code e compartilha via:
- 📱 WhatsApp (botão direto)
- 📧 E-mail (botão direto)
- ⬇️ Download (PNG)

#### 3. Respostas Recebidas
Visualiza dashboard com:
- Total de colaboradores autorizados
- Total de respostas recebidas
- Taxa de adesão (%)
- Gráfico de adesão

> **Segurança:** O RH acessa apenas os dados da sua própria empresa. Não é possível ver dados de outras empresas.

---

## 👥 Módulo Colaborador — Responder Questionário

### Acesso

O colaborador acessa via link ou QR Code recebido do RH:

```
https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app/?cnpj=XXXXXXXXXXX
```

### Passo 1: Informar CPF

Digite o CPF (11 dígitos, sem pontos ou traços) e clique em **ACESSAR ▶**

### Passo 2: Responder os Blocos

O questionário está dividido em **8 blocos (40 questões)**:

| Bloco | Nome | Questões |
|-------|------|----------|
| 1 | 📦 Cargo | 5 |
| 2 | 🎮 Controle | 6 |
| 3 | ⚖️ Demandas | 8 |
| 4 | ⚠️ Relacionamentos | 4 |
| 5 | 🤝 Apoio Colegas | 4 |
| 6 | 👔 Apoio Chefia | 5 |
| 7 | 📢 Comunicação | 3 |
| 8 | 🔄 Mudanças | 5 |

Escala de resposta: **Nunca / Raramente / Às vezes / Frequentemente / Sempre**

### Navegação Entre Blocos

Ao concluir todas as questões de um bloco, clique no botão ao final:

```
[✅ Próximo Bloco (2/8)]
```

> Se houver perguntas sem resposta no bloco, o botão exibe um aviso e não avança.

### Passo 3: Enviar

No último bloco, após responder todas as 40 questões:

```
[🚀 ENVIAR RESPOSTAS]
```

Uma mensagem de confirmação é exibida e as respostas são registradas.

> **Observações:**
> - O mesmo CPF não pode responder **duas vezes para a mesma empresa**
> - O mesmo CPF **pode** responder para empresas diferentes (cada empresa é independente)
> - O preenchimento dura aproximadamente **10 minutos**

---

## 📊 Consultar Resultados

Na **Aba 3 — Resultados**:

1. Selecione a empresa no dropdown
2. Veja as métricas:

```
┌──────────────────┬──────────────────┬──────────────┐
│ CPFs Autorizados │ Respostas Receb. │ Taxa Adesão  │
│       25         │       18         │    72%       │
└──────────────────┴──────────────────┴──────────────┘
```

3. Analise as médias por dimensão (escala 0 a 4)
4. Visualize o histórico completo de respostas
5. Exporte os dados em CSV

### Gerar Laudo PDF

1. Preencha CNAE Principal e Grau de Risco (opcional)
2. Clique em **📄 Gerar Laudo PDF**
3. Baixe o arquivo gerado

---

## 🔐 Segurança e Acesso RH

### Quando usar esta aba

Use quando uma empresa:
- Perdeu ou esqueceu a senha RH
- Precisa trocar o responsável de RH
- Quer resetar o acesso por segurança

### Como Gerar Nova Senha

1. Acesse **Aba 5 — Segurança e Acesso RH**
2. Selecione a empresa no dropdown
3. Clique em **🔐 Gerar Nova Senha RH**
4. A nova senha é exibida **uma única vez**

```
🔐 Credenciais Atualizadas
Empresa: Empresa Exemplo Ltda
CNPJ: 49405001000105
Nova Senha de Acesso RH: X3P7K1M9
⚠️ Anote esta senha! Esta é a única vez que ela será exibida.
```

5. Copie a senha e envie ao RH da empresa

> **Atenção:** A geração de nova senha **invalida automaticamente** a senha anterior.

---

## ⚠️ Zona de Perigo — Exclusão de Dados

Localização: **Aba 2 — Conferência e Correção → Zona de Perigo**

> ❌ Todas as ações nesta seção são **irreversíveis**.

### Excluir Empresa Individual

Remove uma empresa específica e **todo o seu histórico de respostas**.

1. Acesse a **Zona de Perigo → Aba "🗑️ Excluir Empresa"**
2. Selecione a empresa no dropdown
3. Verifique os contadores de impacto exibidos:
   ```
   CPFs que serão removidos: 25
   Respostas que serão apagadas: 18
   ```
4. Digite a **senha do Admin SSTG** para confirmar
5. Clique em **🗑️ EXCLUIR EMPRESA E TODO O HISTÓRICO**

### Resetar Banco Completo

Remove **todas** as empresas e **todos** os históricos.

1. Acesse a **Zona de Perigo → Aba "💣 Resetar Tudo"**
2. Digite a **senha do Admin SSTG**
3. Clique em **💣 RESETAR BANCO DE DADOS COMPLETO**

> Use apenas em casos extremos, como reinício completo do sistema.

---

## 🔄 Movimentação de Pessoal

Localização: **Aba 4 — Movimentação de Pessoal**

### Admissão (Incluir colaborador)

1. Selecione a empresa
2. Preencha a tabela com CPF, Função, Departamento
3. Clique em **➕ INCLUIR COLABORADORES**

### Desligamento (Inativar)

1. Informe o CPF do colaborador
2. Selecione o motivo do desligamento
3. Clique em **🚫 INATIVAR COLABORADOR**

> O CPF ficará bloqueado, mas o histórico de respostas é preservado.

### Reativação

1. Visualize a lista de inativos
2. Informe o CPF a reativar
3. Clique em **✅ REATIVAR COLABORADOR**

---

## 📚 Documentação Integrada

Localização: **Aba 6 — Documentação**

Acesse os guias diretamente no sistema, sem precisar abrir arquivos externos:

| Documento | Conteúdo |
|-----------|----------|
| 📄 README | Visão geral, início rápido, FAQ |
| 👥 TUTORIAL | Este guia completo |
| 🚀 GUIA_INSTALACAO | Setup, configuração, publicação |
| 🔧 GUIA_TECNICO | Arquitetura, dados, segurança |
| ✅ CHECKLIST_LANCAMENTO | Validação pré-produção |
| 🚀 DOCUMENTACAO_PUBLICACAO | Processo de publicação |

Clique em **Ler** para visualizar o conteúdo no sistema ou em **⬇️ PDF** para baixar.

---

## ❓ FAQ e Troubleshooting

### Perguntas Frequentes

**P: Esqueci a senha do Admin SSTG. O que fazer?**  
R: A senha padrão é `sstg2025`. Se foi alterada e esquecida, é necessário editar o arquivo `app.py` localmente e redefinir a variável `SENHA_ADMIN`.

**P: O RH perdeu a senha de acesso. Como recuperar?**  
R: Admin acessa **Segurança e Acesso RH**, seleciona a empresa e clica em **Gerar Nova Senha**. A senha antiga é invalidada automaticamente.

**P: Um colaborador pode responder duas vezes?**  
R: Não. O sistema bloqueia a segunda tentativa com a mensagem: *"Você já participou desta avaliação."*

**P: Um colaborador pode responder para duas empresas diferentes?**  
R: Sim. O mesmo CPF pode ser cadastrado e responder em empresas diferentes. O controle é por CPF + CNPJ.

**P: O questionário aparece com respostas já marcadas para outro respondente.**  
R: Isso foi corrigido na v6.1. Cada respondente tem suas próprias chaves de sessão (por CPF), evitando contaminação entre respostas.

**P: O colaborador diz que o link não funciona.**  
R: Verifique se o período de aplicação está ativo. Acesse **Conferência → Gerenciar Período** e ajuste as datas.

**P: Como excluir todos os dados de uma empresa?**  
R: Acesse **Conferência → Zona de Perigo → Excluir Empresa**. A ação exige confirmação com senha admin e é irreversível.

**P: A documentação mostra "Arquivo não encontrado".**  
R: Verifique se os arquivos `.md` estão na raiz do repositório. A partir da v6.1, o sistema usa caminho absoluto via `__file__` para localizar os documentos.

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| "CPF não autorizado" | CPF não cadastrado | Admin cadastra o CPF na empresa |
| "Período encerrado" | Data fim ultrapassada | Admin ajusta o período na Aba 2 |
| "Você já participou" | CPF já respondeu | Normal — resposta já registrada |
| "Senha incorreta" | Senha RH errada | Admin gera nova senha (Aba 5) |
| "PDF não disponível" | Arquivo não gerado | Execute `gerar_pdf_publicacao.py` |

---

**Última atualização:** 05/05/2026  
**Versão do sistema:** 6.1
