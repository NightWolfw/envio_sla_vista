-- Adiciona coluna para controlar envio automático de PDF por grupo
ALTER TABLE grupos_whatsapp
    ADD COLUMN IF NOT EXISTS envio_pdf BOOLEAN NOT NULL DEFAULT FALSE;

COMMENT ON COLUMN grupos_whatsapp.envio_pdf IS 'Define se o grupo recebe PDF automaticamente junto com a mensagem.';
