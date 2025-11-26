-- Adiciona flag de monitoramento na configuração do dashboard
ALTER TABLE IF EXISTS dashboard_config
ADD COLUMN IF NOT EXISTS monitor_ativo BOOLEAN NOT NULL DEFAULT FALSE;

-- Opcional: limpar hora_inicio/hora_fim se quiser desconsiderar
UPDATE dashboard_config SET hora_inicio = '00:00', hora_fim = '23:59' WHERE hora_inicio IS NOT NULL AND hora_fim IS NOT NULL;

