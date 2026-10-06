-- =====================================================
-- SSTG DRE-DRPS — Schema Supabase Completo
-- Execute no SQL Editor do Supabase
-- Ordem: 1, 2, 3, 4, 5, 6, 7, 8
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

-- 2. RESPOSTAS DO QUESTIONÁRIO DRPS (COPSOQ III)
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

-- 3. RESPOSTAS DO QUESTIONÁRIO DRE (AEP)
CREATE TABLE IF NOT EXISTS respostas_aep (
    id           BIGSERIAL PRIMARY KEY,
    cpf_hash     TEXT NOT NULL,
    cnpj         TEXT NOT NULL,
    empresa      TEXT,
    funcao       TEXT,
    departamento TEXT,
    data         TEXT,
    -- Scores por dimensão (AEP/NR-17)
    score_postura           NUMERIC,
    score_movimento         NUMERIC,
    score_esforco           NUMERIC,
    score_ambiente          NUMERIC,
    score_organizacao       NUMERIC,
    score_geral             NUMERIC,
    UNIQUE (cpf_hash, cnpj)
);

-- 4. AJUSTES AO DIAGNÓSTICO DRE (AEP)
CREATE TABLE IF NOT EXISTS ajustes_aep (
    id           BIGSERIAL PRIMARY KEY,
    cnpj         TEXT NOT NULL UNIQUE,
    empresa      TEXT,
    -- Ajustes aos scores e recomendações
    ajuste_postura    TEXT,
    ajuste_movimento  TEXT,
    ajuste_esforco    TEXT,
    ajuste_ambiente   TEXT,
    ajuste_organizacao TEXT,
    data_ajuste      TEXT,
    responsavel      TEXT
);

-- 5. AJUSTES AO DIAGNÓSTICO DRPS (COPSOQ III)
CREATE TABLE IF NOT EXISTS ajustes_drps (
    id           BIGSERIAL PRIMARY KEY,
    cnpj         TEXT NOT NULL UNIQUE,
    empresa      TEXT,
    -- Ajustes às dimensões e interpretação
    ajuste_cargo          TEXT,
    ajuste_controle       TEXT,
    ajuste_demandas       TEXT,
    ajuste_relacionamentos TEXT,
    ajuste_apoio          TEXT,
    ajuste_comunicacao    TEXT,
    ajuste_comportamentos TEXT,
    data_ajuste          TEXT,
    responsavel          TEXT
);

-- 6. LAUDOS GERADOS (PDF)
CREATE TABLE IF NOT EXISTS laudos (
    id           BIGSERIAL PRIMARY KEY,
    cnpj         TEXT NOT NULL,
    empresa      TEXT,
    tipo         TEXT NOT NULL, -- 'DRPS' ou 'DRE'
    versao       TEXT,
    data_geracao TEXT,
    responsavel  TEXT
);

-- 7. USUÁRIOS OPERACIONAIS (Admin)
CREATE TABLE IF NOT EXISTS usuarios (
    id           BIGSERIAL PRIMARY KEY,
    usuario      TEXT NOT NULL UNIQUE,
    nome         TEXT,
    senha_hash   TEXT,
    status       TEXT DEFAULT 'Ativo',
    data_criacao TEXT
);

-- 8. CONFIGURAÇÕES GERAIS
CREATE TABLE IF NOT EXISTS config (
    id    BIGSERIAL PRIMARY KEY,
    chave TEXT NOT NULL UNIQUE,
    valor TEXT
);

-- =====================================================
-- Row Level Security (RLS) — opcional mas recomendado
-- =====================================================
-- Descomentar se quiser habilitar RLS (precisa de policies específicas)
-- ALTER TABLE acessos  ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE respostas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE respostas_aep ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ajustes_aep ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ajustes_drps ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE laudos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE config ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- Fim do Schema — Aplicação DRE-DRPS está pronta
-- =====================================================
