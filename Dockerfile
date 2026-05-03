# ── Imagem base leve com Python 3.11 ──────────────────────────────────────────
FROM python:3.11-slim

# Evita prompts interativos durante instalação de pacotes do sistema
ENV DEBIAN_FRONTEND=noninteractive

# Variáveis de ambiente para o consumidor
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
    KAFKA_GROUP_ID=pipeline-vendas \
    KAFKA_TOPIC=vendas.public.vendas \
    PG_HOST=postgres-destino \
    PG_PORT=5432 \
    PG_DB=vendas_dw \
    PG_USER=admin \
    PG_PASSWORD=admin123

# Dependências do sistema necessárias para confluent-kafka e psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências Python primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do consumidor
COPY consumer.py .

# Comando padrão ao iniciar o container
CMD ["python", "-u", "consumer.py"]
