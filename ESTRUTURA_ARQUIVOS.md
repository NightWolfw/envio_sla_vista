# 📁 Estrutura de Arquivos - Setup Docker Completo

## Arquivos de Configuração

```
projeto/
├── docker-compose-completo.yml  ← ARQUIVO PRINCIPAL - Sobe tudo
├── .env                          ← Configurações GPS Bot (criar a partir de env.exemplo)
├── env.exemplo                   ← Template para .env
├── evolution-api.env             ← Configurações Evolution API (já pronto)
├── README_DOCKER.md              ← Documentação completa
└── ESTRUTURA_ARQUIVOS.md         ← Este arquivo
```

## Ordem de Configuração

### 1️⃣ Criar arquivo .env do GPS Bot
```bash
cp env.exemplo .env
nano .env
```

**O que configurar:**
- ✅ `DB_VISTA_HOST` - Host do banco Vista
- ✅ `DB_VISTA_PORT` - Porta do banco Vista
- ✅ `DB_VISTA_DATABASE` - Nome do banco Vista (dw_gps)
- ✅ `DB_VISTA_USER` - Usuário do banco Vista
- ✅ `DB_VISTA_PASSWORD` - Senha do banco Vista
- ✅ `SECRET_KEY` - Chave secreta do Flask (mude em produção)

### 2️⃣ Revisar evolution-api.env (opcional)
```bash
nano evolution-api.env
```

**Principais variáveis:**
- `AUTHENTICATION_API_KEY=309754692928797528226121395208`
- `DATABASE_CONNECTION_URI=postgresql://evodm:Jl2@24Jl@postgres:5432/evolution?schema=public`
- `CACHE_REDIS_URI=redis://redis:6379/6`

> **Nota:** O arquivo já vem configurado, você só precisa editar se quiser mudar algo.

### 3️⃣ Subir os containers
```bash
docker-compose -f docker-compose-completo.yml up -d --build
```

## 🎯 Resumo das Configurações

| Serviço | Arquivo de Config | O que tem lá |
|---------|-------------------|--------------|
| GPS Bot | `.env` | Banco Vista (externo) + SECRET_KEY |
| Evolution API | `evolution-api.env` | Todas configs da Evolution |
| Postgres dw_sla | `docker-compose-completo.yml` | Hardcoded no compose |
| Postgres Evolution | `docker-compose-completo.yml` | Hardcoded no compose |
| Redis | `docker-compose-completo.yml` | Config padrão |

## ✅ Checklist

- [ ] Criar `.env` a partir de `env.exemplo`
- [ ] Configurar dados do Banco Vista no `.env`
- [ ] (Opcional) Editar `evolution-api.env` se necessário
- [ ] Rodar `docker-compose -f docker-compose-completo.yml up -d --build`
- [ ] Aguardar containers subirem
- [ ] Acessar http://localhost:5000 (GPS Bot)
- [ ] Acessar http://localhost:8080 (Evolution API)

## 🔑 Credenciais Padrão

### Banco dw_sla (GPS Bot)
- Host: `postgres_dw_sla` (dentro do Docker) ou `localhost:5433` (do host)
- User: `jonatan_lopes`
- Password: `Jl2@24Jl`
- Database: `dw_sla`

### Banco Evolution
- Host: `postgres` (dentro do Docker) ou `localhost:5432` (do host)
- User: `evodm`
- Password: `Jl2@24Jl`
- Database: `evolution`

### Evolution API
- API Key: `309754692928797528226121395208`
- Instance: `envio_gps`

## 📝 Notas

- O `.env` NÃO deve ser versionado no Git (já está no .gitignore)
- O `env.exemplo` deve ser versionado (é só um template)
- O `evolution-api.env` você decide se versiona ou não
- Todos os containers compartilham a rede `evolution-net`
- Comunicação entre containers usa **nomes dos containers**, não `localhost`

## 🚀 Pronto!

Agora é só seguir o checklist e rodar! 🎉

