# Migrações de Banco de Dados

## Lista de Migrações

1. **001_add_mensagens_agendadas.sql** - Adiciona tabela `mensagens_agendadas`
2. **002_add_agendamento_logs.sql** - Adiciona tabela `agendamento_logs` para logs detalhados
3. **003_add_envio_pdf_to_grupos.sql** - Adiciona coluna `envio_pdf` aos grupos para controlar envio automático de PDF

## Como Aplicar as Migrações

### Opção 1: Recriar o Banco Completamente (Recomendado se não tiver dados importantes)

```bash
# Para o container
docker-compose -f docker-compose-completo.yml down

# Remove o volume do banco (ATENÇÃO: apaga todos os dados!)
docker volume rm envio_sla_vista_postgres_dw_sla_data

# Sobe tudo novamente (vai recriar o banco com a nova estrutura)
docker-compose -f docker-compose-completo.yml up -d
```

### Opção 2: Aplicar Migrações Manualmente (Mantém dados existentes) ⭐

```bash
# Migração 001 - Tabela mensagens_agendadas
docker cp gps_bot/migrations/001_add_mensagens_agendadas.sql postgres_dw_sla:/tmp/
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -f /tmp/001_add_mensagens_agendadas.sql

# Migração 002 - Tabela agendamento_logs
docker cp gps_bot/migrations/002_add_agendamento_logs.sql postgres_dw_sla:/tmp/
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -f /tmp/002_add_agendamento_logs.sql

# Verificar se as tabelas foram criadas
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -c "\dt mensagens_agendadas"
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla -c "\dt agendamento_logs"
```

### Opção 3: Executar SQL Diretamente

```bash
# Conectar ao banco
docker exec -it postgres_dw_sla psql -U jonatan_lopes -d dw_sla

# Dentro do psql, cole o conteúdo das migrações uma por uma
# Depois saia com \q
```

### Opção 4: Aplicar Todas de Uma Vez (Script Automatizado)

```bash
# Windows PowerShell
cd gps_bot/migrations
Get-ChildItem -Filter "*.sql" | Sort-Object Name | ForEach-Object {
    docker cp $_.FullName postgres_dw_sla:/tmp/$($_.Name)
    docker exec postgres_dw_sla psql -U jonatan_lopes -d dw_sla -f /tmp/$($_.Name)
}

# Linux/Mac
cd gps_bot/migrations
for file in *.sql; do
    docker cp "$file" postgres_dw_sla:/tmp/
    docker exec postgres_dw_sla psql -U jonatan_lopes -d dw_sla -f /tmp/"$file"
done
```

## Verificar se Funcionou

Após aplicar as migrações:

- **Mensagens Agendadas**: `http://localhost:5000/mensagens/`
- **Logs de Agendamento**: `http://localhost:5000/sla/listar` (clique em "Logs" de qualquer agendamento)

Se não houver mais erros "Internal Server Error", as tabelas foram criadas com sucesso! ✅

