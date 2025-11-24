# MCP Servers

Use the following MCP Servers:
- **Context7** to search for updated documentation from commonly libraries.
- **Postgres** to search tables and collumns in database

Use the following external documentations:
- **Evolution API** - https://doc.evolution-api.com/v2/api-reference/

# Web Design

- Use the color #22d3ee for the background of all buttons in the project and #0f172a for the text of all buttons unless the user specifies a different color.

# Time

- Utilize sempre Timezone -03:00H (America/Sao_Paulo)

# VPS / Projeto

- Código em `/opt/envio_sla_vista` (VPS). Backend FastAPI container `envio_sla_app` na porta 5000; frontend Next.js rodando em 3000 (fora de Docker).
- Compose: `/opt/envio_sla_vista/docker-compose-completo.yml`. Subir/recriar: `docker compose -f docker-compose-completo.yml up -d --build envio_sla_app`.
- Variáveis de ambiente: `/opt/envio_sla_vista/.env` (inclui PUBLIC_API_BASE_URL=https://soloalive.uk).
- Nginx: configs em `/etc/nginx/sites-available/soloalive.uk` (proxy /api -> 127.0.0.1:5000, raiz -> 127.0.0.1:3000, headers CSP/HSTS).
- Logs úteis:
  - Backend: `docker compose -f docker-compose-completo.yml logs --tail=100 envio_sla_app`
  - Frontend: `/var/log/envio_front.log`
  - Nginx: `/var/log/nginx/error.log`

# Frontend

- Base API hardcoded em HTTPS: `frontend/lib/api.ts`, `frontend/lib/client.ts`, `frontend/components/DashboardResumoClient.tsx` usam `https://soloalive.uk/api`.
- Build/rodar: `cd /opt/envio_sla_vista/frontend && rm -rf .next .turbo && npm run build && nohup npm run start -- -p 3000 >/var/log/envio_front.log 2>&1 &`.

# Backend / SLA

- Scheduler/Envio: `gps_bot/app/services/scheduler_service.py` (envia texto e PDF como anexo via Evolution; respeita envio_pdf por grupo).
- WhatsApp Evolution: `gps_bot/app/services/whatsapp.py` (usa EVOLUTION_BASE_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME do .env).
- Geração de PDF: `gps_bot/app/services/pdf_sla.py` (PDF_STORAGE_DIR; auto limpeza em 5 min).
