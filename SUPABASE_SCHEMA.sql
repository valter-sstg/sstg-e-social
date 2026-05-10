-- =====================================================
-- SSTG DRPS -- Schema Supabase
-- Execute no SQL Editor do Supabase (em ordem)
-- =====================================================

-- 1. ACESSOS AUTORIZADOS
CREATE TABLE IF NOT EXISTS acessos (
    id                   BIGSERIAL PRIMARY KEY,
    cpf                  TEXT NOT NULL,
    empresa              TEXT,
    cnpj                 TEXT NOT NULL,
    funcao               TEXT,
    departamento         TEXT,
    data_acesso_liberado TEXT,
    data_inicio_periodo  TEXT,
    data_fim_periodo     TEXT,
    status               TEXT DEFAULT 'Ativo',
    data_movimentacao    TEXT,
    motivo_movimentacao  TEXT,
    senha_rh_hash        TEXT,
    UNIQUE (cpf, cnpj)
);

-- 2. RESPOSTAS DO QUESTIONARIO
CREATE TABLE IF NOT EXISTS respostas (
    id           BIGSERIAL PRIMARY KEY,
    cpf_hash     TEXT NOT NULL,
    cnpj         TEXT NOT NULL,
    empresa      TEXT,
    funcao       TEXT,
    departamento TEXT,
    data         TEXT,
    -- Médias por dimensão (COPSOQ III)
    media_cargo              NUMERIC,
    media_controle           NUMERIC,
    media_demandas           NUMERIC,
    media_relacionamentos    NUMERIC,
    media_apoio_dos_colegas  NUMERIC,
    media_apoio_da_chefia    NUMERIC,
    media_comunicacao_e_mudancas    NUMERIC,
    media_comportamentos_ofensivos  NUMERIC,
    media_geral                     NUMERIC,
    UNIQUE (cpf_hash, cnpj)
);

-- Se a tabela ja existir, adicione a coluna nova com:
-- ALTER TABLE public.respostas ADD COLUMN IF NOT EXISTS media_comportamentos_ofensivos NUMERIC;

-- 3. USUARIOS OPERACIONAIS
CREATE TABLE IF NOT EXISTS usuarios (
    id           BIGSERIAL PRIMARY KEY,
    usuario      TEXT NOT NULL UNIQUE,
    nome         TEXT,
    senha_hash   TEXT,
    status       TEXT DEFAULT 'Ativo',
    data_criacao TEXT
);

-- 4. CONFIGURACOES
CREATE TABLE IF NOT EXISTS config (
    id    BIGSERIAL PRIMARY KEY,
    chave TEXT NOT NULL UNIQUE,
    valor TEXT
);

-- =====================================================
-- Row Level Security (RLS) -- opcional mas recomendado
-- =====================================================
-- ALTER TABLE acessos  ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE respostas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE config   ENABLE ROW LEVEL SECURITY;
-- 
-- Se habilitar RLS, adicione policies para a anon key:
-- CREATE POLICY "allow_all" ON acessos  FOR ALL USING (true) WITH CHECK (true);
-- CREATE POLICY "allow_all" ON respostas FOR ALL USING (true) WITH CHECK (true);
-- CREATE POLICY "allow_all" ON usuarios FOR ALL USING (true) WITH CHECK (true);
-- CREATE POLICY "allow_all" ON config   FOR ALL USING (true) WITH CHECK (true);
