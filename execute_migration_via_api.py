#!/usr/bin/env python3
"""
Executa migração SQL via API REST do Supabase (PostgreSQL)
"""
import subprocess
import sys

# Instalar psycopg2 se necessário
try:
    import psycopg2
except ImportError:
    print("📦 Instalando psycopg2...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

# Credenciais do Supabase
# URL: https://ghcqdmbojvwubwxweika.supabase.co
# Host: ghcqdmbojvwubwxweika.supabase.co
# Port: 5432
# Database: postgres
# User: postgres
# Password: (precisa ser obtida do console Supabase ou de st.secrets)

print("⚠️  MÉTODO 1: Conexão direta via psycopg2")
print("-" * 70)
print("Para usar este método, você precisa da senha do Postgres do Supabase.")
print("Essa senha está disponível em:")
print("  1. Console Supabase → Project Settings → Database → Connection String")
print("  2. Ou em st.secrets se já estiver configurada")
print()

# Tentar conectar (vai falhar sem a senha)
try:
    # Ler a senha de entrada
    password = input("Cole a senha PostgreSQL do Supabase (ou Enter para pular): ").strip()

    if not password:
        raise Exception("Senha não fornecida")

    conn = psycopg2.connect(
        host="ghcqdmbojvwubwxweika.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password=password
    )

    cursor = conn.cursor()

    # Ler arquivo SQL
    with open("SUPABASE_MIGRATION_COMPLETA.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Executar
    print("\n🚀 Executando migração...")
    cursor.execute(sql_content)
    conn.commit()

    print("✅ Migração concluída com sucesso!")
    print("\nTabelas criadas:")

    # Listar tabelas
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    for row in cursor.fetchall():
        print(f"  • {row[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n⚠️  Erro: {e}")
    print("\n" + "=" * 70)
    print("MÉTODO 2: Execução Manual no Console Supabase")
    print("=" * 70)
    print("""
1. Abra: https://app.supabase.com
2. Login: valter@sstgocupacional.com.br
3. Selecione projeto: sstg-app
4. Abra SQL Editor (lado esquerdo)
5. Crie uma nova query (botão "+ New query")
6. Cole o conteúdo do arquivo: SUPABASE_MIGRATION_COMPLETA.sql
7. Clique "Execute" (botão verde)
8. Aguarde a conclusão (deve levar segundos)
9. Valide: Database → Tables (deve aparecer 8 novas tabelas)

O arquivo está em:
  C:\\CLAUDE CODE\\CHECKLIST SST\\sstg-e-social\\SUPABASE_MIGRATION_COMPLETA.sql
""")
