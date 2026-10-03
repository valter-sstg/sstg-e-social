# ☁️ Guia de Migração para Nuvem — SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1)

**Versão:** 1.0  
**Data:** 30/04/2026  
**Objetivo:** Mover a pasta Claude do computador local para a nuvem (máxima disponibilidade)

---

## 📋 Opções Disponíveis

| Opção | Espaço | Sincronização | Backup | Controle Versão | Custo |
|-------|--------|----------------|--------|-----------------|-------|
| **Google Drive Desktop** | 15 GB free | Automática | Sim | Não | Grátis |
| **OneDrive** | 5 GB free | Automática | Sim | Não | Grátis |
| **GitHub** | Ilimitado | Manual (Git) | Sim | **Sim** | Grátis |
| **Dropbox** | 2 GB free | Automática | Sim | Não | Pago |

---

## ✅ Opção 1: Google Drive Desktop (Recomendado)

### Vantagens
✅ 15 GB de espaço grátis  
✅ Sincronização automática  
✅ Acesso via web  
✅ Compartilhamento fácil  
✅ Interface intuitiva  

### Passo 1: Instalar Google Drive Desktop

1. Acesse: https://support.google.com/drive/answer/7329379
2. Clique em **"Download Google Drive for desktop"**
3. Execute o instalador
4. Faça login com sua conta Google

### Passo 2: Criar Pasta de Sincronização

1. Google Drive Desktop → Configurações (⚙️)
2. Ativa: **"Sincronizar para este computador"**
3. Selecione local: `G:\Meu Drive\` (ou outro disco)
4. Crie pasta: `SSTG-E-Social`
5. Aguarde sincronização completar

### Passo 3: Mover Arquivos para Google Drive

```bash
# Opção A: Copiar via Windows Explorer
# 1. Abra: C:\Users\valte\Claude
# 2. Selecione todos os arquivos (Ctrl+A)
# 3. Copie (Ctrl+C)
# 4. Navegue até: G:\Meu Drive\SSTG-E-Social
# 5. Cole (Ctrl+V)
# 6. Aguarde cópia completar

# Opção B: Copiar via PowerShell
Copy-Item -Path "C:\Users\valte\Claude\*" -Destination "G:\Meu Drive\SSTG-E-Social" -Recurse -Force
```

### Passo 4: Verificar Sincronização

```bash
# Verificar se arquivos estão em G:\Meu Drive\SSTG-E-Social
dir "G:\Meu Drive\SSTG-E-Social"

# Arquivo de teste
echo "teste" > "G:\Meu Drive\SSTG-E-Social\teste.txt"
# Abre Google Drive web para confirmar sincronização
```

### Passo 5: Atualizar app.py para Nova Localização

**Arquivo:** `C:\Users\valte\Claude\app.py`  
**Linha:** ~18

```python
# Antes:
DATA_DIR = ""

# Depois:
DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"
```

### Passo 6: Atualizar Atalho da Pasta Claude

```bash
# OPCIONAL: Criar atalho para pasta Google Drive
# Windows Explorer → Clique direito em G:\Meu Drive\SSTG-E-Social
# → Enviar para → Área de Trabalho (criar atalho)
```

---

## ✅ Opção 2: OneDrive (Alternativa)

### Vantagens
✅ 5 GB de espaço grátis  
✅ Já integrado ao Windows  
✅ Sincronização automática  
✅ Acesso via web (office.com)  

### Passo 1: Configurar OneDrive

1. Abra **OneDrive** (já está instalado)
2. Faça login com sua conta Microsoft
3. Nota o caminho de sincronização (ex: `C:\Users\valte\OneDrive`)

### Passo 2: Mover Arquivos para OneDrive

```bash
# Copiar via PowerShell
Copy-Item -Path "C:\Users\valte\Claude\*" -Destination "C:\Users\valte\OneDrive\SSTG-E-Social" -Recurse -Force
```

### Passo 3: Atualizar app.py

```python
# Antes:
DATA_DIR = ""

# Depois:
DATA_DIR = r"C:\Users\valte\OneDrive\SSTG-E-Social"
```

---

## ✅ Opção 3: GitHub (Recomendado para Backup + Versionamento)

### Vantagens
✅ Controle de versão (Git)  
✅ Histórico de todas as mudanças  
✅ Backup automático  
✅ Compartilhamento profissional  
✅ Integração com Streamlit Cloud  
⚠️ Público (a menos que use repositório privado)

### Passo 1: Criar Conta GitHub

1. Acesse: https://github.com/signup
2. Crie conta (use email pessoal ou corporativo)
3. Confirme email

### Passo 2: Criar Repositório

1. GitHub → New Repository
2. Nome: `sstg-e-social`
3. Descrição: "Sistema de Diagnóstico Psicossocial COPSOQ III"
4. **Privado** (recomendado)
5. Clique: "Create Repository"

### Passo 3: Inicializar Git Localmente

```bash
# Na pasta C:\Users\valte\Claude
cd "C:\Users\valte\Claude"

# Inicialize Git
git init
git config user.name "Seu Nome"
git config user.email "seu.email@example.com"

# Adicione todos os arquivos
git add .

# Primeiro commit
git commit -m "Initial commit - SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1) v6.0"

# Adicione repositório remoto
git remote add origin https://github.com/seu-usuario/sstg-e-social.git

# Envie para GitHub
git branch -M main
git push -u origin main
```

### Passo 4: Ignorar Arquivos Sensíveis

Crie arquivo `.gitignore`:

```bash
# C:\Users\valte\Claude\.gitignore

# Dados sensíveis
db_acessos_autorizados.csv
respostas_CNPJ_*.csv
*.env

# Cache Python
__pycache__/
*.pyc
.streamlit/

# Sistema
.DS_Store
Thumbs.db
```

### Passo 5: Backup Automático (GitHub Actions)

Crie arquivo `.github/workflows/backup.yml`:

```yaml
name: Daily Backup

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM todos os dias

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for changes
        run: |
          git status
          git log --oneline -5
```

---

## 🔄 Opção 4: Sincronização Dupla (Recomendado)

**Máxima disponibilidade = Usar 2 ou 3 opções!**

```
┌─────────────────────────────────────────────────┐
│  Local C:\Users\valte\Claude                    │
│  ├─ Pasta primária (desenvolvimento)            │
│  └─ Git push → GitHub (backup)                  │
│                                                 │
├─ Google Drive (sincronização automática)        │
│  ├─ G:\Meu Drive\SSTG-E-Social                 │
│  └─ DATA_DIR aponta aqui                        │
│                                                 │
└─ GitHub (versionamento + repositório remoto)   │
   ├─ Histórico de mudanças                       │
   └─ Acesso de qualquer lugar                    │
```

### Configuração Combinada

```python
# app.py - Usar Google Drive como DATA_DIR
DATA_DIR = r"G:\Meu Drive\SSTG-E-Social"

# .gitignore - Evitar sincronizar grandes arquivos
db_acessos_autorizados.csv
respostas_CNPJ_*.csv
```

```bash
# Fluxo diário:
# 1. Desenvolver em C:\Users\valte\Claude
# 2. Google Drive sincroniza automaticamente
# 3. Periodicamente: git push para GitHub
```

---

## 📊 Comparação Final

### Cenário 1: Apenas Google Drive (Simples)
```
✅ Fácil de usar
✅ Sincronização automática
✅ Acesso via web
❌ Sem controle de versão
❌ Sem histórico de mudanças
```

### Cenário 2: Google Drive + GitHub (Recomendado)
```
✅ Sincronização automática (Google Drive)
✅ Controle de versão (GitHub)
✅ Backup duplo
✅ Histórico completo
⚠️ Requer conhecimento de Git
```

### Cenário 3: Apenas OneDrive (Alternativa)
```
✅ Integrado ao Windows
✅ Sincronização automática
❌ Menor espaço (5GB)
❌ Sem controle de versão
```

---

## 🚀 Recomendação Final

**Para máxima disponibilidade operacional:**

1. **Primário:** Google Drive Desktop
   - Sincronização automática
   - Acesso rápido local
   - Espaço amplo (15 GB)

2. **Backup:** GitHub
   - Versionamento
   - Histórico completo
   - Acesso remoto

3. **Como usar:**
   ```
   Local (C:\Users\valte\Claude)
      ↓ sincroniza
   Google Drive (G:\Meu Drive\SSTG-E-Social)
      ↓ git push
   GitHub (repositório privado)
   ```

---

## 📝 Checklist de Migração

### Antes de Migrar
- [ ] Backup da pasta Claude em local seguro
- [ ] Verificar todos os arquivos estão presentes
- [ ] Anotar caminhos atuais (DATA_DIR, APP_URL, etc.)

### Durante Migração
- [ ] Instalar Google Drive Desktop (ou OneDrive)
- [ ] Criar pasta na nuvem
- [ ] Copiar arquivos
- [ ] Aguardar sincronização completar
- [ ] Verificar integridade dos arquivos

### Após Migração
- [ ] Atualizar DATA_DIR em app.py
- [ ] Reiniciar app.py
- [ ] Testar funcionalidades (cadastro, upload, etc.)
- [ ] Excluir pasta local (opcional - manter backup)
- [ ] Configurar GitHub (se usar)
- [ ] Teste acesso via web (Google Drive, GitHub)

### Validação
- [ ] App inicia sem erros
- [ ] Arquivos salvos vão para nuvem
- [ ] Arquivos sincronizados corretamente
- [ ] PDF downloads funcionam
- [ ] Dados persistem após reboot

---

## 🆘 Troubleshooting

### Problema: Sincronização lenta
**Solução:** Excluir arquivos grandes do Google Drive
- Arquivos .pdf podem ser regenerados
- Arquivos de cache Python
- Pastas `__pycache__`

### Problema: Acesso negado em G:\Meu Drive
**Causa:** Google Drive Desktop não está ativo
**Solução:**
```bash
# Verificar se Google Drive está rodando
tasklist | findstr "googledrivefs"

# Se não aparecer, inicie:
"C:\Program Files\Google\Drive File Stream\googledrivefs.exe"
```

### Problema: Git push falha
**Causa:** Credenciais não configuradas
**Solução:**
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@gmail.com"
git credential-manager-core erase https://github.com
# Tente novamente - pedirá para autenticar
```

---

## 📞 Próximos Passos

1. **Escolha a opção** (recomendamos Google Drive + GitHub)
2. **Execute os passos** do guia acima
3. **Teste a funcionalidade** do app
4. **Configure backups automáticos** (se usar GitHub)
5. **Documente** o novo local de armazenamento

---

**Guia de Migração — SSTG - DRPS Diagnóstico de Riscos Psicossociais (NR-1) v6.0**  
**Última atualização: 30/04/2026**
