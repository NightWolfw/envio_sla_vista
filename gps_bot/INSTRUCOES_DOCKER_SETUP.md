# Instruções para Integração Docker Completa

## ✅ Arquivos Já Criados/Atualizados

1. ✅ `gps_bot/docker-compose.yml` - Atualizado para usar rede `evolution-net`
2. ✅ `gps_bot/init-dw_sla.sql` - Schema do banco dw_sla criado

## 📋 O Que Você Precisa Fazer Manualmente

### 1. Atualizar docker-compose.yml da Evolution API

**Localize o arquivo `docker-compose.yml` da Evolution API** e adicione o seguinte serviço:

```yaml
  # Adicione este serviço ANTES da seção 'volumes'
  postgres_dw_sla:
    container_name: postgres_dw_sla
    image: postgres:15
    networks:
      - evolution-net
    command: ["postgres", "-c", "max_connections=1000"]
    restart: always
    ports:
      - 5433:5432
    environment:
      - POSTGRES_USER=jonatan_lopes
      - POSTGRES_PASSWORD=Jl2@24Jl
      - POSTGRES_DB=dw_sla
    volumes:
      - postgres_dw_sla_data:/var/lib/postgresql/data
      - ./init-dw_sla.sql:/docker-entrypoint-initdb.d/init.sql
    expose:
      - 5432
```

**E adicione o volume:**

```yaml
volumes:
  evolution_instances:
  evolution_redis:
  postgres_data:
  postgres_dw_sla_data:  # ADICIONE ESTA LINHA
```

### 2. Copiar o Arquivo SQL

Copie o arquivo `gps_bot/init-dw_sla.sql` para a **pasta da Evolution API**:

```bash
cp gps_bot/init-dw_sla.sql /caminho/da/evolution-api/init-dw_sla.sql
```

### 3. Subir os Containers na Ordem Correta

```bash
# 1. Pare todos os containers
docker-compose down

# 2. No diretório da Evolution API, suba os serviços
cd /caminho/da/evolution-api
docker-compose up -d

# 3. Aguarde 30 segundos para os bancos iniciarem
sleep 30

# 4. No diretório do GPS Bot, suba o serviço
cd /caminho/do/gps_bot
docker-compose up -d --build
```

## 🧪 Testes de Conectividade

### Verificar se tudo está rodando:

```bash
# Ver todos os containers
docker ps

# Você deve ver:
# - evolution_api
# - postgres (Evolution)
# - postgres_dw_sla (GPS Bot)
# - redis
# - envio_sla_app
```

### Testar conexão do GPS Bot com Evolution API:

```bash
docker exec -it envio_sla_app bash
curl http://evolution_api:8080
# Deve retornar resposta da API
exit
```

### Testar conexão com banco dw_sla:

```bash
docker exec -it envio_sla_app bash
apt-get update && apt-get install -y postgresql-client
psql -h postgres_dw_sla -U jonatan_lopes -d dw_sla -c "SELECT version();"
# Deve mostrar a versão do PostgreSQL
exit
```

### Verificar logs:

```bash
# Logs do GPS Bot
docker logs -f envio_sla_app

# Logs da Evolution API
docker logs -f evolution_api

# Logs do banco dw_sla
docker logs -f postgres_dw_sla
```

## 🎯 Estrutura Final

```
evolution-net (rede Docker)
├── evolution_api (porta 8080)
├── postgres (Evolution DB)
├── postgres_dw_sla (GPS Bot DB - porta 5433)
├── redis
└── envio_sla_app (GPS Bot - porta 5000)
```

## 🔑 Comunicação Entre Containers

| De | Para | URL |
|-----|------|-----|
| envio_sla_app | Evolution API | `http://evolution_api:8080` |
| envio_sla_app | Banco dw_sla | `postgres_dw_sla:5432` |
| envio_sla_app | Banco Vista | `${DB_VISTA_HOST}:${DB_VISTA_PORT}` (externo) |

## ⚠️ Importante

- Todos os containers devem estar na rede `evolution-net`
- Use **nomes dos containers** para comunicação, não `localhost`
- O banco Vista (dw_gps) continua externo, acessado por IP/hostname real
- A porta 5433 (postgres_dw_sla) fica exposta no host para acesso externo, mas internamente usa porta 5432

## 🚀 Após Tudo Configurado

Acesse: `http://localhost:5000`

E teste enviando uma mensagem! 📱

