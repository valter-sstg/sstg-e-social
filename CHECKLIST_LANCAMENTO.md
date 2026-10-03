# ✅ Checklist de Lançamento — DRE - DRPS v8.0

**Versão:** 8.0
**Atualizado:** 14/07/2026
**Uso:** validar uma publicação/atualização do sistema no Streamlit Cloud
antes de liberar para uso pelas empresas atendidas.

**Data do teste:** ___/___/_____
**Responsável:** _______________________________
**Assinado em:** ___/___/_____

---

## 📋 1. Antes de Publicar (Pré-requisitos)

- [ ] Todos os arquivos alterados estão em `C:\Users\valte\Claude\upload_temp\`
- [ ] `requirements.txt` está sincronizado com as dependências reais
      (streamlit, pandas, reportlab, plotly, supabase, qrcode, pillow)
- [ ] `.streamlit/config.toml` presente com o tema SSTG (cores e fonte)
- [ ] Secrets `SUPABASE_URL` e `SUPABASE_KEY` configurados em
      `share.streamlit.io` → app → Settings → Secrets
- [ ] Arquivos de documentação (`.md` + `.pdf`) atualizados estão incluídos
      no upload, se aplicável

---

## 🚀 2. Pós-Publicação — Verificações Gerais

- [ ] **Reboot realizado** em `share.streamlit.io` (menu "⋮" → "Reboot app")
- [ ] **App carrega sem erros** na URL pública
      (`https://sstg-e-social-687zwalcuokbggvtc7iy9m.streamlit.app`)
- [ ] **Título da aba do navegador** correto: "DRE - DRPS | Gestão
      integrada de riscos ergonômicos e psicossociais (NR-1 / NR-17)"
- [ ] **Rodapé da barra lateral** exibe "v8.0 — DRE - DRPS / COPSOQ III +
      NR-17"
- [ ] **Cores SSTG aplicadas**: laranja (#DC3B24), navy (#282C5B), fundo
      cinza claro (#EFEFEF)
- [ ] **Menu principal exibe os 5 módulos:**
  - [ ] 🏠 Início
  - [ ] 📝 Questionários DRE-DRPS
  - [ ] 📊 Gestão das Respostas (RH)
  - [ ] 📚 Documentação
  - [ ] 🔐 Admin SSTG (Gestão)
- [ ] **Conexão com Supabase ativa** (sem erro de banco ao abrir qualquer
      módulo — se o banco estava hibernado, primeira carga pode demorar
      alguns segundos)

---

## 🔐 3. Acesso ao Módulo Admin

- [ ] Tela de login do módulo **🔐 Admin SSTG (Gestão)** aparece
- [ ] Senha correta concede acesso
- [ ] Senha incorreta é rejeitada com mensagem clara
- [ ] Após login, as abas aparecem:
  - [ ] 🆕 Cadastro/Inclusão
  - [ ] 📋 Conferência e Correção
  - [ ] 🔐 Segurança e Acesso RH
  - [ ] 📊 Resultados DRPS
  - [ ] 🦴 Resultados DRE
  - [ ] 🔄 Movimentação de Pessoal
  - [ ] 👥 Usuários (apenas perfil Administrador)
- [ ] Opção **"Alterar Senha"** disponível e funcional

---

## 📝 4. Teste de Cadastro — Aba Cadastro/Inclusão

### Cadastro manual

- [ ] Campos da empresa presentes: **CNPJ**, **Razão Social**, **CNAE
      Principal**, **Grau de Risco (NR-4)**
- [ ] Seletor **Grau de Risco (NR-4)** mostra as opções "—" / "1" / "2" /
      "3" / "4"
- [ ] Aviso explicando o impacto do Grau de Risco na severidade do DRE é
      exibido
- [ ] Campos **Data Início** e **Data Fim** do período presentes
- [ ] Validação: Data Fim > Data Início
- [ ] Tabela dinâmica para colaboradores (CPF, Função, Departamento)
      funciona — adicionar/remover linhas
- [ ] Botão **"✅ SALVAR E LIBERAR ACESSOS"** salva sem erros

### Cadastro via CSV

- [ ] Botão para baixar template CSV funciona
- [ ] Template tem colunas `CPF;Função;Departamento` (separador `;`)
- [ ] Upload de CSV com 3+ linhas é aceito
- [ ] Preview dos dados antes de salvar é exibido
- [ ] Linhas com CPF inválido são sinalizadas

### Links gerados

- [ ] Após salvar, **dois links** são exibidos em uma caixa de destaque:
  - [ ] Link **DRPS**: `.../questionario_psicossocial.html?cnpj=XXXXX`
  - [ ] Link **DRE**: `.../questionario_aep.html?cnpj=XXXXX`
- [ ] Ambos os links abrem corretamente em uma aba anônima/outro navegador

---

## 👤 5. Teste de Resposta — Questionário DRPS (Colaborador)

- [ ] Acesso pelo link DRPS (`questionario_psicossocial.html?cnpj=...`)
      redireciona corretamente ao app
- [ ] Tela de login do colaborador exibe nome da empresa
- [ ] **Validações de CPF:**
  - [ ] CPF cadastrado → acesso liberado
  - [ ] CPF não autorizado → mensagem clara de bloqueio
  - [ ] CPF já respondeu → mensagem "já participou"
  - [ ] Acesso fora do período → mensagem de período encerrado
- [ ] Questionário exibe os **7 blocos / 35 questões** do COPSOQ III
- [ ] Navegação entre blocos (Anterior/Próximo) funciona
- [ ] Escala de respostas funciona corretamente
- [ ] Envio final grava na tabela `respostas` e exibe confirmação de
      sucesso

---

## 🦴 6. Teste de Resposta — Questionário DRE (Colaborador)

- [ ] Acesso pelo link DRE (`questionario_aep.html?cnpj=...`) redireciona
      corretamente ao app
- [ ] Mesmas validações de CPF/período do item 5 se aplicam
- [ ] Questionário exibe as **4 seções / 17 questões** da AEP
- [ ] Cada item permite resposta de % de risco percebido (ou equivalente)
- [ ] Campos de relato (dor, sugestões, dificuldades) funcionam
- [ ] Envio grava em `respostas_aep` e exibe confirmação de sucesso

---

## 📊 7. Teste de Resultados DRPS (Admin)

- [ ] Aba **📊 Resultados DRPS** carrega sem erros
- [ ] KPIs (autorizados, respondidos, % de adesão) corretos
- [ ] Gráficos por dimensão exibem corretamente (plotly)
- [ ] Seletor de empresa funciona
- [ ] Botão **"📄 Gerar Laudo DRPS em PDF"** gera PDF sem erros
- [ ] PDF contém: dados da empresa, gráficos por dimensão, classificação
      de risco

---

## 🦴 8. Teste de Resultados DRE (Admin)

- [ ] Aba **🦴 Resultados DRE** carrega sem erros
- [ ] KPIs e gráfico de % de risco por item exibem corretamente
- [ ] Tabela de inventário de riscos exibe as colunas: **Nº, Seção, Risco
      Identificado, % Risco, Severidade, Probabilidade, GR, Classificação,
      Plano?**
- [ ] **Severidade** reflete o Grau de Risco (NR-4) cadastrado da empresa
- [ ] **Probabilidade** segue a fórmula `1 + 3 × %risco` (entre 1.00 e
      4.00)
- [ ] **GR = Severidade × Probabilidade** calculado corretamente (1.0–16.0)
- [ ] **Classificação** segue as faixas:
  - [ ] Baixo ≤ 4.0
  - [ ] Médio > 4.0–8.0 (ou ≥70% de risco mesmo com GR menor)
  - [ ] Alto > 8.0
  - [ ] Crítico quando % risco > 98% (sobrepõe o GR)
- [ ] **"Plano?" = SIM** a partir da classificação Médio
- [ ] Itens com menos de **3 respondentes no setor**
      (`MIN_RESPONDENTES_SETOR`) são agrupados/anonimizados corretamente
- [ ] Botão **"📄 Gerar Laudo DRE em PDF"** gera PDF sem erros
- [ ] PDF contém o inventário de riscos e ações de controle sugeridas

---

## 🔄 9. Teste de Movimentação de Pessoal

- [ ] Aba **🔄 Movimentação de Pessoal** lista colaboradores ativos e
      inativos
- [ ] **Inativar** colaborador por CPF funciona
- [ ] Colaborador inativado não consegue mais acessar os questionários
- [ ] **Reativar** colaborador por CPF funciona
- [ ] Colaborador reativado volta a ter acesso

---

## 🔐 10. Teste de Segurança e Acesso RH

- [ ] Aba **🔐 Segurança e Acesso RH** lista as empresas cadastradas
- [ ] Geração de senha RH (8 caracteres) por CNPJ funciona
- [ ] Senha é exibida **uma única vez** após geração
- [ ] Senha gerada permite login no módulo RH (item 11)

---

## 🏢 11. Teste do Módulo RH — Gestão das Respostas

- [ ] Login com **CNPJ + senha RH** funciona
- [ ] CNPJ ou senha incorretos são rejeitados com mensagem clara
- [ ] Após login, e-books disponíveis para download/compartilhamento:
  - [ ] E-book DRPS
  - [ ] E-book DRE
- [ ] **Nenhum link de questionário** é exibido neste módulo (apenas
      e-books)
- [ ] Botão **"↩ Voltar à tela inicial"** funciona
- [ ] Se logado como admin (`admin_logado`), botão **"🔄 Trocar de
      empresa"** aparece e funciona

---

## 📚 12. Teste do Módulo Documentação

- [ ] Módulo **📚 Documentação** aparece no menu principal (visível
      conforme regra de acesso — `admin_logado`)
- [ ] Cada documento listado abre/baixa corretamente:
  - [ ] README.md / .pdf
  - [ ] TUTORIAL.md / .pdf
  - [ ] GUIA_INSTALACAO.md / .pdf
  - [ ] GUIA_TECNICO.md / .pdf
  - [ ] CHECKLIST_LANCAMENTO.md / .pdf
- [ ] Itens sem arquivo correspondente exibem "arquivo não encontrado" sem
      quebrar a página (comportamento esperado e aceito para
      "Documentação de Publicação" e "POP020 Tutorial de Telas")

---

## 👁️ 13. Teste de Modo Demonstração

- [ ] Com `admin_logado`, botão **"👁️ Ver questionário em modo
      demonstração"** aparece
- [ ] Modo demonstração abre o questionário em modo **somente leitura**
      (`_demo_readonly`)
- [ ] Não é possível enviar respostas no modo demonstração
- [ ] Botão **"↩ Voltar / Encerrar"** retorna ao módulo Admin

---

## 👥 14. Teste de Usuários (Admin — perfil Administrador)

- [ ] Aba **👥 Usuários** visível apenas para perfil Administrador
- [ ] Criar novo usuário operacional funciona
- [ ] Listar usuários existentes funciona
- [ ] Ativar/desativar usuário funciona
- [ ] Redefinir senha de usuário funciona
- [ ] Usuário operacional **não vê** a aba 👥 Usuários ao logar

---

## 🔒 15. Testes de Segurança Gerais

- [ ] **CPF armazenado como hash** em `respostas`/`respostas_aep`
      (`cpf_hash`) — não é possível reverter ao CPF original
- [ ] Acesso fora do período (`data_inicio_periodo`/`data_fim_periodo`)
      bloqueado corretamente
- [ ] Senha do administrador alterada é exigida (não aceita a senha
      original do código após troca)
- [ ] Botão "Sair" / logout funciona em todos os módulos autenticados

---

## 💾 16. Teste de Backup

- [ ] Aba **📋 Conferência e Correção** → expander **💾 Backup** disponível
- [ ] Exportação gera um ZIP com CSVs de `acessos`, `respostas`,
      `respostas_aep`, `usuarios`, `laudos`
- [ ] Arquivo ZIP baixa corretamente e abre sem erros

---

## 🎨 17. Testes Visuais

- [ ] Cores SSTG consistentes em todos os módulos (laranja, navy, fundo
      cinza claro)
- [ ] Layout funciona em desktop
- [ ] Layout funciona em mobile (visualização responsiva do navegador)
- [ ] Ícones/emojis dos menus e abas exibem corretamente (sem caracteres
      quebrados)

---

## 📱 18. Compatibilidade de Browser

- [ ] Google Chrome → funciona
- [ ] Microsoft Edge → funciona
- [ ] Mozilla Firefox → funciona
- [ ] Navegador mobile (Chrome/Safari Android/iOS) → funciona

---

## 🧪 19. Testes de Erro & Edge Cases

- [ ] CNPJ inexistente no link do questionário → mensagem apropriada
- [ ] CPF vazio/format inválido → mensagem apropriada
- [ ] Data Fim < Data Início no cadastro → bloqueado com mensagem
- [ ] CSV com coluna/separador incorretos → mensagem apropriada
- [ ] Banco Supabase hibernado → app reconecta automaticamente
      (`db.ping()`) sem travar a interface

---

## 📊 20. Performance

- [ ] App carrega em menos de ~10 segundos após reboot (incluindo possível
      reativação do Supabase)
- [ ] Navegação entre módulos é fluida (sem recarregamentos completos
      desnecessários)
- [ ] Geração de laudo PDF (DRPS ou DRE) conclui em menos de ~15 segundos

---

## ✅ Status Geral

- [ ] ✅ **APROVADO PARA USO**
- [ ] ⚠️ **APROVADO COM RESSALVAS** (listar abaixo)
- [ ] ❌ **REPROVADO** (novo teste necessário após correções)

**Ressalvas / Observações:**
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

## ✍️ Assinatura

```
Data de Conclusão:        ___/___/_____

Responsável pelo Teste:    _____________________
Assinatura:                _____________________
```

---

**Checklist de Lançamento — DRE - DRPS v8.0**
