-- Cria tabela de configuração do dashboard (global)
CREATE TABLE IF NOT EXISTS dashboard_config (
    id SERIAL PRIMARY KEY,
    hora_inicio TIME NOT NULL DEFAULT '00:00',
    hora_fim TIME NOT NULL DEFAULT '23:59',
    intervalo_minutos INT NOT NULL DEFAULT 10,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Garante um único registro padrão
INSERT INTO dashboard_config (hora_inicio, hora_fim, intervalo_minutos)
SELECT '00:00', '23:59', 10
WHERE NOT EXISTS (SELECT 1 FROM dashboard_config);

