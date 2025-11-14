# Migrações de Banco de Dados

## Como Aplicar as Migrações

### Opção 1: Recriar o Banco Completamente (Recomendado se não tiver dados importantes)

```bash
# Para o container
docker-compose -f docker-compose-completo.yml down

# Remove o volume do banco
docker volume rm envio_sla_vista_postgres_dw_sla_data

# Sobe tudo novamente (vai recriar o banco com a nova estrutura)
docker-compose -f docker-compose-completo.yml up -d
```

### Opção 2: Aplicar Migração Manualmente (Mantém dados existentes)

```bash
# Copiar arquivo de migração para o container
docker cp gps_bot/migrations/001_add_mensagens_agendadas.sql postgres_dw_sla:/tmp/

# Executar a migração
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -f /tmp/001_add_mensagens_agendadas.sql

# Verificar se a tabela foi criada
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -c "\dt mensagens_agendadas"
```

### Opção 3: Executar SQL Diretamente

```bash
# Conectar ao banco
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla

# Dentro do psql, cole o conteúdo de 001_add_mensagens_agendadas.sql
# Depois saia com \q
```

## Verificar se Funcionou

Após aplicar a migração, acesse: `http://localhost:5000/mensagens/`

Se não houver mais o erro "Internal Server Error", a tabela foi criada com sucesso!

