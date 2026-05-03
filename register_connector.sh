curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "vendas-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres-origem",
      "database.port": "5432",
      "database.user": "admin",
      "database.password": "admin123",
      "database.dbname": "vendas_origem",
      "database.server.name": "vendas",
      "table.include.list": "public.vendas",
      "plugin.name": "pgoutput"
    }
  }'