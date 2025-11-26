-- Tabelas de agregação no dw_sla para o dashboard (mês corrente apenas)

-- Agregação diária por CR e hierarquias
CREATE TABLE IF NOT EXISTS dashboard_tarefas_dia (
    data DATE NOT NULL,
    cr TEXT NOT NULL,
    cliente TEXT,
    diretor_executivo TEXT,
    diretor_regional TEXT,
    gerente_regional TEXT,
    gerente TEXT,
    supervisor TEXT,
    pec_01 TEXT,
    pec_02 TEXT,
    finalizadas_ok INT NOT NULL DEFAULT 0,
    nao_realizadas INT NOT NULL DEFAULT 0,
    em_aberto INT NOT NULL DEFAULT 0,
    iniciadas INT NOT NULL DEFAULT 0,
    total INT NOT NULL DEFAULT 0,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_dashboard_tarefas_dia_data ON dashboard_tarefas_dia(data);
CREATE INDEX IF NOT EXISTS idx_dashboard_tarefas_dia_cr ON dashboard_tarefas_dia(cr);

-- Ranking de executores por mês corrente
CREATE TABLE IF NOT EXISTS dashboard_executores (
    executor TEXT NOT NULL,
    cr TEXT,
    cliente TEXT,
    diretor_executivo TEXT,
    diretor_regional TEXT,
    gerente_regional TEXT,
    gerente TEXT,
    supervisor TEXT,
    pec_01 TEXT,
    pec_02 TEXT,
    finalizadas_ok INT NOT NULL DEFAULT 0,
    nao_realizadas INT NOT NULL DEFAULT 0,
    total INT NOT NULL DEFAULT 0,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_dashboard_executores_executor ON dashboard_executores(executor);
