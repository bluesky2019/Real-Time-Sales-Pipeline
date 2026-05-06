# 📊 Real-Time Sales Pipeline

> Pipeline de dados de ponta a ponta — do streaming em tempo real até consultas em linguagem natural com Inteligência Artificial.

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-CDC-FF4B4B?style=for-the-badge&logo=apachekafka&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-Google-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)

---

## 📌 Sobre o Projeto

Este projeto foi desenvolvido como extensão prática da minha formação em **Banco de Dados pela Estácio**, onde cursei disciplinas de Big Data com Python e tecnologias modernas de dados. O objetivo é construir um pipeline completo de engenharia de dados — do evento até a consulta por linguagem natural — utilizando tecnologias usadas por times de dados das maiores empresas do mundo.

A proposta une três grandes pilares da engenharia de dados moderna:

- **Streaming em tempo real** — cada venda é capturada no instante em que acontece via CDC
- **Modelagem por camadas com dbt** — dados organizados, testados e documentados em Bronze, Silver e Gold
- **IA Generativa** — interface em português que traduz perguntas em SQL automaticamente

---

## 🏗️ Arquitetura

```
[PostgreSQL Origem]
        │
        ▼  (WAL - Write-Ahead Log)
[Debezium CDC] ──► [Apache Kafka :9092] ──► [Consumidor Python]
                                                     │
                                                     ▼
                                           [PostgreSQL Destino :5433]
                                           ┌──────────────────────┐
                                           │  🟤 Bronze Layer      │ ← dados brutos
                                           │  🩶 Silver Layer      │ ← dados limpos
                                           │  🥇 Gold Layer        │ ← métricas
                                           └──────────────────────┘
                                                     │
                                                     ▼
                                       [Google Gemini API]
                                                     │
                                                     ▼
                                          [Interface Streamlit]
                                    "Qual o produto mais vendido?"
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Papel |
|---|---|---|
| Banco Origem | PostgreSQL 14 (Debezium) | Fonte dos dados de vendas com WAL habilitado |
| Banco Destino | PostgreSQL 14 | Data Warehouse com camadas Bronze/Silver/Gold |
| CDC | Debezium 2.4 | Captura mudanças em tempo real via WAL do PostgreSQL |
| Mensageria | Apache Kafka 7.4 + Zookeeper | Barramento de eventos resiliente |
| Consumidor | Python 3.9 + confluent-kafka | Processa eventos Kafka e persiste no banco destino |
| Transformação | dbt 1.10 + dbt-postgres | Modelos incrementais e camadas de dados |
| IA Generativa | Google Gemini 2.0 Flash Lite | Geração de SQL a partir de linguagem natural |
| Interface | Streamlit | Dashboard web com tabelas, gráficos e histórico |
| Infraestrutura | Docker + Docker Compose | Orquestração de todos os serviços |

---

## 📂 Estrutura do Projeto

```
sales-pipelines/
├── docker-compose.yml              # Orquestração dos 5 serviços
├── register_connector.sh           # Registro do conector Debezium via API REST
├── .gitignore
│
├── consumer/
│   ├── Dockerfile                  # Imagem Python do consumidor
│   ├── requirements.txt            # confluent-kafka + psycopg2
│   └── consumer.py                 # Consumidor Kafka → PostgreSQL destino
│
├── dbt_project/
│   ├── dbt_project.yml             # Configuração principal do dbt
│   ├── profiles.yml                # Conexão com o PostgreSQL destino
│   └── models/
│       ├── bronze/
│       │   ├── sources.yml         # Declaração da fonte de dados
│       │   └── bronze_vendas.sql   # View espelho dos dados brutos
│       ├── silver/
│       │   └── silver_vendas.sql   # Modelo incremental com limpeza
│       └── gold/
│           └── gold_metricas_vendas.sql  # Métricas agregadas por produto/mês
│
└── ai_app/
    └── app.py                      # Interface Streamlit + Google Gemini
```

---

## ⚡ Como Rodar o Projeto

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+
- Chave de API do Google Gemini (gratuita em [aistudio.google.com](https://aistudio.google.com))

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/sales-pipeline-realtime.git
cd sales-pipeline-realtime
```

### 2. Suba a infraestrutura

```bash
docker compose up -d
```

Aguarde ~60 segundos para todos os containers inicializarem. Verifique:

```bash
docker compose ps
```

### 3. Crie a tabela e insira dados no banco de origem

```bash
docker exec -it sales-pipelines-postgres-origem-1 psql -U admin -d vendas_origem -c "
CREATE TABLE IF NOT EXISTS vendas (
    venda_id   SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    valor      NUMERIC(10,2) NOT NULL,
    quantidade INTEGER NOT NULL,
    data_venda TIMESTAMP DEFAULT NOW()
);
INSERT INTO vendas (cliente_id, produto_id, valor, quantidade) VALUES
(1, 101, 250.00, 2),
(2, 102, 89.90, 1),
(3, 101, 500.00, 4);
"
```

### 4. Registre o conector Debezium

```bash
bash register_connector.sh
```

Verifique se está RUNNING:

```bash
curl http://localhost:8083/connectors/vendas-connector/status | python3 -m json.tool
```

### 5. Instale as dependências Python

```bash
pip install confluent-kafka psycopg2-binary dbt-postgres \
            streamlit google-generativeai pandas
```

### 6. Inicie o consumidor

```bash
cd consumer
python3 consumer.py
```

### 7. Execute os modelos dbt

```bash
cd ../dbt_project
dbt run
dbt test
```

### 8. Rode a interface com IA

```bash
cd ../ai_app
streamlit run app.py
```

Acesse **http://localhost:8501**, insira sua chave do Gemini e faça perguntas em português! 🎉

---

## 🧠 Como a IA Funciona

```
1. Usuário digita: "Qual foi o produto mais vendido?"
         │
         ▼
2. Streamlit envia a pergunta + schema das tabelas Gold para o Gemini
         │
         ▼
3. Gemini analisa e gera o SQL:
   SELECT produto_id, SUM(unidades_vendidas) as total
   FROM public_gold.gold_metricas_vendas
   GROUP BY produto_id ORDER BY total DESC LIMIT 1;
         │
         ▼
4. SQL executado no banco (apenas SELECT — read-only por segurança)
         │
         ▼
5. Resultado exibido como tabela + gráfico no Streamlit
```

---

## 📊 Camadas de Dados dbt

### 🟤 Bronze — Dados Brutos
View espelho da tabela de ingestão. Sem transformações, preservada para auditoria e reprocessamento.

### 🩶 Silver — Dados Limpos
Modelo **incremental** com estratégia `delete+insert`. Tipos corrigidos, timestamps convertidos, valores inválidos removidos e campos derivados como `mes_venda` calculados.

### 🥇 Gold — Métricas de Negócio
Tabela reconstruída a cada `dbt run` com agregações prontas: receita total, ticket médio, unidades vendidas, maior e menor venda por produto e período. É nesta camada que a IA realiza as consultas.

---

## 🔐 Segurança

- Conexão da IA com o banco é **somente leitura**
- Apenas queries `SELECT` são aceitas — qualquer outro comando é bloqueado em código
- Chave de API inserida via campo de senha na interface — nunca exposta no código

---

## 🎓 Contexto Acadêmico e Profissional

Este projeto é uma extensão prática da minha formação em **Banco de Dados pela Estácio**, consolidando conhecimentos adquiridos nas disciplinas de Big Data com Python e outras tecnologias de dados. Cada componente do pipeline representa uma habilidade real exigida pelo mercado de engenharia de dados:

| Componente | Habilidade demonstrada |
|---|---|
| Docker Compose | Infraestrutura como código |
| Debezium + Kafka | Streaming e arquitetura orientada a eventos |
| Python Consumer | Processamento de dados em tempo real |
| dbt | Modelagem declarativa e qualidade de dados |
| Google Gemini | Integração de IA generativa em aplicações de dados |
| Streamlit | Prototipação rápida de interfaces analíticas |

---

## 📚 Referências

- [Documentação oficial do dbt](https://docs.getdbt.com/)
- [Debezium — Change Data Capture](https://debezium.io/documentation/)
- [Apache Kafka Quickstart](https://kafka.apache.org/quickstart)
- [Google Gemini API](https://ai.google.dev/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">Feito com dedicação por quem acredita que dados bem tratados transformam decisões. Gilnei Azambuja Borges - Profissional sempre aprendendo mais🔥
</p>

## 🔗 Conecte-se

[![Portfolio](https://img.shields.io/badge/Portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://medium.com/@gilnei809/gilnei-azambuja-borges-analista-de-dados-e-administrador-de-banco-de-dados-8774175b0e46)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gilnei-azambuja-borges-1a83432b)
[![Hugging Face](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/bluesky2019)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/gilneiborges)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=FW4VNKJWXLTCJ)
