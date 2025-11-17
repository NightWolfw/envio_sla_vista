# Imagem base Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo \
    PIP_TRUSTED_HOST="pypi.org pypi.python.org files.pythonhosted.org"

# Instala dependências do sistema e atualiza certificados
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    tzdata \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org && \
    pip install --no-cache-dir -r requirements.txt \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org

# Copia código da aplicação
COPY . .

# Expõe porta do Flask
EXPOSE 5000

# Comando para rodar a aplicação FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]
