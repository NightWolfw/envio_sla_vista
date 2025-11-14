-- Migração: Adicionar tabela mensagens_agendadas
-- Data: 2025-01-XX
-- Descrição: Cria a tabela mensagens_agendadas para o sistema de mensagens agendadas

-- Criar tabela se não existir
CREATE TABLE IF NOT EXISTS mensagens_agendadas (
    id SERIAL PRIMARY KEY,
    mensagem TEXT NOT NULL,
    grupos_selecionados TEXT[] NOT NULL,
    tipo_recorrencia VARCHAR(50) NOT NULL CHECK (tipo_recorrencia IN ('UNICA', 'RECORRENTE')),
    dias_semana INTEGER[],
    horario TIME NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_mensagens_agendadas_ativo ON mensagens_agendadas(ativo);
CREATE INDEX IF NOT EXISTS idx_mensagens_agendadas_data_inicio ON mensagens_agendadas(data_inicio);

-- Confirmação
SELECT 'Tabela mensagens_agendadas criada com sucesso!' as status;

