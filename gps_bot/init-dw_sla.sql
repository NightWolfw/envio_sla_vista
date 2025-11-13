-- Schema do Banco dw_sla para GPS Bot
-- Este arquivo deve ser copiado para a pasta da Evolution API

-- Tabela de Grupos WhatsApp
CREATE TABLE IF NOT EXISTS grupos_whatsapp (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    nome_grupo VARCHAR(500) NOT NULL,
    envio BOOLEAN DEFAULT TRUE,
    cr VARCHAR(50),
    cliente VARCHAR(255),
    pec_01 VARCHAR(255),
    pec_02 VARCHAR(255),
    diretorexecutivo VARCHAR(255),
    diretorregional VARCHAR(255),
    gerenteregional VARCHAR(255),
    gerente VARCHAR(255),
    supervisor VARCHAR(255),
    dia_todo BOOLEAN DEFAULT FALSE,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Mensagens Agendadas
CREATE TABLE IF NOT EXISTS mensagens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    mensagem TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Agendamentos de SLA
CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    grupo_id INTEGER REFERENCES grupos_whatsapp(id) ON DELETE CASCADE,
    tipo_envio VARCHAR(50) NOT NULL CHECK (tipo_envio IN ('resultados', 'programadas')),
    dias_semana VARCHAR(50),
    data_envio TIMESTAMP NOT NULL,
    hora_inicio TIME NOT NULL,
    dia_offset_inicio INTEGER DEFAULT 0,
    hora_fim TIME NOT NULL,
    dia_offset_fim INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    proximo_envio TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Logs de Envio
CREATE TABLE IF NOT EXISTS logs_envio (
    id SERIAL PRIMARY KEY,
    mensagem_agendada_id INTEGER,
    group_id VARCHAR(255),
    nome_grupo VARCHAR(500),
    mensagem TEXT,
    status VARCHAR(50) CHECK (status IN ('sucesso', 'erro')),
    erro_detalhe TEXT,
    enviado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Logs de Agendamento SLA
CREATE TABLE IF NOT EXISTS logs_agendamento (
    id SERIAL PRIMARY KEY,
    agendamento_id INTEGER REFERENCES agendamentos(id) ON DELETE SET NULL,
    grupo_id INTEGER,
    grupo_nome VARCHAR(500),
    cr VARCHAR(50),
    tipo_envio VARCHAR(50),
    status VARCHAR(50),
    erro TEXT,
    executado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para Performance
CREATE INDEX IF NOT EXISTS idx_grupos_cr ON grupos_whatsapp(cr);
CREATE INDEX IF NOT EXISTS idx_grupos_envio ON grupos_whatsapp(envio);
CREATE INDEX IF NOT EXISTS idx_agendamentos_ativo ON agendamentos(ativo);
CREATE INDEX IF NOT EXISTS idx_agendamentos_proximo_envio ON agendamentos(proximo_envio);
CREATE INDEX IF NOT EXISTS idx_logs_status ON logs_envio(status);
CREATE INDEX IF NOT EXISTS idx_logs_agendamento_status ON logs_agendamento(status);

