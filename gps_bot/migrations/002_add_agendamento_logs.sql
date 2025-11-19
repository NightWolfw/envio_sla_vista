BEGIN;

-- Cria tabela para armazenar logs detalhados de cada agendamento
CREATE TABLE IF NOT EXISTS agendamento_logs (
    id SERIAL PRIMARY KEY,
    agendamento_id INTEGER REFERENCES agendamentos(id) ON DELETE CASCADE,
    grupo_id INTEGER REFERENCES grupos_whatsapp(id) ON DELETE SET NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    mensagem_enviada TEXT,
    resposta_api TEXT,
    erro TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices que aceleram buscas por agendamento e por status
CREATE INDEX IF NOT EXISTS idx_agendamento_logs_agendamento_id
    ON agendamento_logs(agendamento_id);
CREATE INDEX IF NOT EXISTS idx_agendamento_logs_status
    ON agendamento_logs(status);

COMMIT;
