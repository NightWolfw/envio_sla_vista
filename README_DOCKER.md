# 🐳 Docker Setup Completo - GPS Bot + Evolution API

Este arquivo gerencia **TODOS** os serviços em uma única rede Docker.

## 📦 O Que Sobe

- **Evolution API** - porta 8080
- **PostgreSQL (Evolution)** - porta 5432
- **PostgreSQL (GPS Bot - dw_sla)** - porta 5433
- **Redis** - porta 6379
- **GPS Bot** - porta 5000

Todos na mesma rede `evolution-net` para comunicação direta!

## 🚀 Como Usar

### 1. Configure os arquivos de ambiente

#### a) Configurar .env (GPS Bot)

Copie o exemplo e edite:

```bash
cp env.exemplo .env
nano .env
```

Configure as variáveis do **Banco Vista** (externo):

```env
DB_VISTA_HOST=seu-servidor-vista
DB_VISTA_PORT=5432
DB_VISTA_DATABASE=dw_gps
DB_VISTA_USER=postgres
DB_VISTA_PASSWORD=sua-senha
```

#### b) Configurar evolution-api.env (Evolution API)

O arquivo `evolution-api.env` já vem pré-configurado, mas você pode editar se precisar:

```bash
nano evolution-api.env
```

**Principais configurações:**
- `AUTHENTICATION_API_KEY` - Chave de autenticação da API
- `DATABASE_CONNECTION_URI` - Conexão com PostgreSQL
- `CACHE_REDIS_URI` - Conexão com Redis

### 2. Suba TUDO com um comando

```bash
docker-compose -f docker-compose-completo.yml up -d --build
```

### 3. Aguarde a inicialização (30 segundos)

```bash
# Ver logs de todos os serviços
docker-compose -f docker-compose-completo.yml logs -f

# Ou ver apenas o GPS Bot
docker-compose -f docker-compose-completo.yml logs -f envio_sla_app
```

### 4. Acesse as aplicações

- **GPS Bot**: http://localhost:5000
- **Evolution API**: http://localhost:8080

## 📄 Relatórios SLA (PDF via link)

- O envio automático agora gera o PDF localmente e envia **somente o link** no WhatsApp. Nada de upload de mídia pela Evolution API.
- Garanta que `PUBLIC_API_BASE_URL` (no `.env`) aponte para o endereço público do FastAPI; ele monta as URLs que são abertas no frontend/WhatsApp.
- Use `PDF_STORAGE_DIR` para definir onde os PDFs temporários serão salvos dentro do container (por padrão `gps_bot/temp_pdfs`). Eles são excluídos automaticamente após 5 minutos.
- Endpoints úteis para testes:
  - `POST /api/agendamentos/{id}/pdf` → gera e retorna um link único.
  - `POST /api/agendamentos/bulk/pdf` → gera links para vários agendamentos.
  - `GET /api/files/sla/{filename}` → baixa o PDF pelo link retornado.

## 📊 Comandos Úteis

```bash
# Ver status de todos os containers
docker-compose -f docker-compose-completo.yml ps

# Parar tudo
docker-compose -f docker-compose-completo.yml stop

# Iniciar tudo novamente
docker-compose -f docker-compose-completo.yml start

# Reiniciar apenas GPS Bot
docker-compose -f docker-compose-completo.yml restart envio_sla_app

# Ver logs específicos
docker-compose -f docker-compose-completo.yml logs -f evolution_api
docker-compose -f docker-compose-completo.yml logs -f postgres_dw_sla

# Rebuild apenas do GPS Bot (após mudanças no código)
docker-compose -f docker-compose-completo.yml up -d --build envio_sla_app

# Entrar no container para debug
docker exec -it envio_sla_app bash
docker exec -it evolution_api sh

# Destruir tudo (mantém volumes/dados)
docker-compose -f docker-compose-completo.yml down

# Destruir tudo incluindo dados (CUIDADO!)
docker-compose -f docker-compose-completo.yml down -v
```

## 🧪 Testes de Conectividade

### Testar Evolution API

```bash
curl http://localhost:8080
```

### Testar GPS Bot

```bash
curl http://localhost:5000
```

### Testar comunicação interna (dentro do container)

```bash
# Entrar no container do GPS Bot
docker exec -it envio_sla_app bash

# Testar conexão com Evolution API
curl http://evolution_api:8080

# Testar conexão com banco dw_sla
apt-get update && apt-get install -y postgresql-client
psql -h postgres_dw_sla -U jonatan_lopes -d dw_sla -c "\\dt"

# Sair
exit
```

## 🗄️ Banco de Dados

### Acessar banco dw_sla (GPS Bot)

```bash
# De dentro do container
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla

# Do host (se tiver psql instalado)
psql -h localhost -p 5433 -U jonatan_lopes -d dw_sla
# Senha: Jl2@24Jl
```

### Acessar banco Evolution

```bash
docker exec -it postgres psql -U evodm -d evolution
```

## 🔧 Troubleshooting

### GPS Bot não conecta na Evolution API

```bash
# Verificar se Evolution está rodando
docker-compose -f docker-compose-completo.yml logs evolution_api

# Verificar rede
docker network inspect evolution-net
```

### Erro de banco de dados

```bash
# Ver logs do banco
docker-compose -f docker-compose-completo.yml logs postgres_dw_sla

# Recriar banco do zero
docker-compose -f docker-compose-completo.yml down postgres_dw_sla
docker volume rm envio_sla_vista_postgres_dw_sla_data
docker-compose -f docker-compose-completo.yml up -d postgres_dw_sla
```

### Limpar tudo e começar do zero

```bash
# ATENÇÃO: Isso apaga TODOS OS DADOS!
docker-compose -f docker-compose-completo.yml down -v
docker-compose -f docker-compose-completo.yml up -d --build
```

## 🎯 Estrutura da Rede

```
evolution-net
├── evolution_api:8080      → API WhatsApp
├── postgres:5432           → Banco Evolution
├── postgres_dw_sla:5432    → Banco GPS Bot (porta 5433 no host)
├── redis:6379              → Cache
└── envio_sla_app:5000      → Aplicação GPS Bot
```

## ✅ Checklist Inicial

- [ ] Criar arquivo `.env` com dados do Banco Vista (`cp env.exemplo .env`)
- [ ] Verificar/editar `evolution-api.env` se necessário
- [ ] Rodar `docker-compose -f docker-compose-completo.yml up -d --build`
- [ ] Aguardar 30 segundos
- [ ] Acessar http://localhost:5000
- [ ] Criar instância na Evolution API (http://localhost:8080)
- [ ] Testar envio de mensagem

## 📝 Notas Importantes

- O banco **Vista (dw_gps)** continua externo, não está no Docker
- Portas expostas no host: 5000, 8080, 5432, 5433, 6379
- A comunicação entre containers usa os **nomes dos serviços**
- Todos os dados persistem em volumes Docker

## 🆘 Suporte

Se algo não funcionar:

1. Veja os logs: `docker-compose -f docker-compose-completo.yml logs`
2. Verifique os containers: `docker-compose -f docker-compose-completo.yml ps`
3. Teste conectividade interna (comandos acima)

Boa sorte! 🚀

