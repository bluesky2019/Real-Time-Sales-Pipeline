from confluent_kafka import Consumer
from datetime import datetime
import psycopg2
import json
import base64
import struct

# Conexao com PostgreSQL de destino
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="vendas_dw",
    user="admin",
    password="admin123"
)
cursor = conn.cursor()

# Garante que a tabela bronze existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bronze_vendas (
        venda_id     SERIAL PRIMARY KEY,
        cliente_id   INTEGER,
        produto_id   INTEGER,
        valor        NUMERIC(10,2),
        quantidade   INTEGER,
        data_venda   TIMESTAMP,
        created_at   TIMESTAMP DEFAULT NOW()
    )
""")
conn.commit()

# Configuracao do consumidor Kafka
consumer = Consumer({
    "bootstrap.servers": "localhost:29092",
    "group.id": "pipeline-vendas",
    "auto.offset.reset": "earliest"
})
consumer.subscribe(["vendas.public.vendas"])

print("Consumidor rodando...")


def decodificar_valor(valor):
    """Debezium envia NUMERIC como base64 - converte para decimal"""
    if isinstance(valor, str):
        try:
            decoded = base64.b64decode(valor)
            if len(decoded) == 2:
                return struct.unpack(">h", decoded)[0] / 100
            elif len(decoded) == 4:
                return struct.unpack(">i", decoded)[0] / 100
            elif len(decoded) == 8:
                return struct.unpack(">q", decoded)[0] / 100
        except Exception:
            return valor
    return valor


def decodificar_timestamp(ts):
    """Debezium envia TIMESTAMP como microsegundos Unix - converte para datetime"""
    if ts is not None:
        try:
            return datetime.utcfromtimestamp(ts / 1000000)
        except Exception:
            return None
    return None


while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    if msg.error():
        print("Erro Kafka:", msg.error())
        continue

    try:
        payload = json.loads(msg.value())
        after = payload.get("payload", {}).get("after")

        if after:
            after["valor"] = decodificar_valor(after.get("valor"))
            after["data_venda"] = decodificar_timestamp(after.get("data_venda"))

            cursor.execute("""
                INSERT INTO bronze_vendas (cliente_id, produto_id, valor, quantidade, data_venda)
                VALUES (%(cliente_id)s, %(produto_id)s, %(valor)s, %(quantidade)s, %(data_venda)s)
                ON CONFLICT (venda_id) DO UPDATE SET
                    valor = EXCLUDED.valor,
                    quantidade = EXCLUDED.quantidade
            """, after)
            conn.commit()
            print("Venda inserida:", after)

    except Exception as e:
        conn.rollback()
        print("Mensagem ignorada:", e)
        continue
