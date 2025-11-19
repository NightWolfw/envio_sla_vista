# GPS Vista Frontend (Next.js)

Interface web construída em Next.js/TypeScript para consumir os endpoints FastAPI do projeto `gps_bot`.

## Pré-requisitos

- Node.js 18+
- API em FastAPI rodando (porta padrão `5000`)

## Variáveis de ambiente

Crie `frontend/.env.local` apontando para o backend:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
```

## Como rodar

```bash
cd frontend
npm install
npm run dev
# Acesse http://localhost:3000
```

## Estrutura principal

- `app/layout.tsx`: layout global + navegação lateral.
- `app/page.tsx`: visão geral (cards de estatísticas).
- `app/dashboard`: métricas e distribuição de tarefas.
- `app/grupos`: gestão de grupos WhatsApp (listagem + edição básica).
- `app/agendamentos`: listagem e criação de agendamentos.
- `app/mensagens`: CRUD simplificado de mensagens agendadas.
- `app/sla`: formulário para gerar preview de mensagens SLA.

## Build de produção

```bash
cd frontend
npm run build
npm run start
```

Integre com Docker conforme necessário (ex.: adicionando um serviço ao `docker-compose` que execute `npm ci && npm run build && npm run start`).
