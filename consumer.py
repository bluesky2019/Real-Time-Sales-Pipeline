from confluent_kafka import Consumer
import psycopg2
import json

# Conexão com PostgreSQL de destino
conn = psycopg2.connect(
    host="localhost", port=5433,
    dbname="vendas_dw", user="admin", password="admin123"
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

# Configuração do consumidor Kafka
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pipeline-vendas',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['vendas.public.vendas'])

print("🚀 Consumidor rodando... aguardando eventos de vendas")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    
    payload = json.loads(msg.value())
    after = payload.get('payload', {}).get('after')  # dados APÓS a operação
    
    if after:
        cursor.execute("""
            INSERT INTO bronze_vendas (cliente_id, produto_id, valor, quantidade, data_venda)
            VALUES (%(cliente_id)s, %(produto_id)s, %(valor)s, %(quantidade)s, %(data_venda)s)
            ON CONFLICT (venda_id) DO UPDATE SET
                valor = EXCLUDED.valor,
                quantidade = EXCLUDED.quantidade
        """, after)
        conn.commit()
        print(f"✅ Venda inserida: {after}")