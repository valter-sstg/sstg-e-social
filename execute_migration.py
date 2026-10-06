#!/usr/bin/env python3
"""
Script para executar a migração SQL no Supabase
"""
import sys
import subprocess

# Verificar/instalar supabase
try:
    from supabase import create_client
except ImportError:
    print("📦 Instalando supabase...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase", "-q"])
    from supabase import create_client

# Credenciais
url = "https://ghcqdmbojvwubwxweika.supabase.co"
key = "sb_publishable_yYdC6y0tQArjNvnwJZA4HQ_4WF1ONBq"

print("🔌 Conectando ao Supabase...")
try:
    sb = create_client(url, key)
    print("✅ Conectado com sucesso")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    sys.exit(1)

# Ler arquivo SQL
print("\n📖 Lendo arquivo de migração...")
try:
    with open("SUPABASE_MIGRATION_COMPLETA.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    print("✅ Arquivo lido")
except FileNotFoundError:
    print("❌ Arquivo SUPABASE_MIGRATION_COMPLETA.sql não encontrado")
    sys.exit(1)

# Dividir em statements
statements = []
for line in sql_content.split("\n"):
    line = line.strip()
    if line and not line.startswith("--"):
        statements.append(line)

sql_clean = " ".join(statements)
sql_statements = [s.strip() for s in sql_clean.split(";") if s.strip()]

print(f"\n📝 Total de statements: {len(sql_statements)}")
print("=" * 70)

# Executar cada statement
success_count = 0
for i, stmt in enumerate(sql_statements, 1):
    try:
        # Usar postgrest para executar SQL raw
        # A biblioteca supabase não tem suporte direto, então usamos rpc
        print(f"[{i}/{len(sql_statements)}] {stmt[:60]}...")

        # Tentar executar via query (limitado)
        # Para SQL raw, precisamos de um método diferente
        result = sb.rpc("exec_sql", {"query": stmt}).execute()
        success_count += 1
        print("  ✅ OK")
    except Exception as e:
        print(f"  ⚠️  Pulando: {str(e)[:50]}")
        # Continuar mesmo com erro, pois CREATE TABLE IF NOT EXISTS deve passar

print("\n" + "=" * 70)
print(f"✅ Tentativa concluída: {success_count} de {len(sql_statements)} statements executados")
print("\n💡 Se houver erros acima, execute manualmente no console Supabase:")
print("   1. Abra: https://app.supabase.com")
print("   2. Login: valter@sstgocupacional.com.br")
print("   3. Projeto: sstg-app")
print("   4. SQL Editor → Cole SUPABASE_MIGRATION_COMPLETA.sql")
print("   5. Execute (botão verde)")
