# 🚀 Real-Time Sales Pipeline com PostgreSQL, dbt e IA Generativa

> Pipeline de dados de ponta a ponta — do streaming em tempo real até consultas em linguagem natural com Inteligência Artificial.

---

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-CDC-FF4B4B?style=for-the-badge&logo=apachekafka&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Anthropic-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

## 📌 Sobre o Projeto

Este projeto nasceu da interseção entre minha formação acadêmica em **Banco de Dados pela Estácio** — onde cursei disciplinas de Big Data com Python e tecnologias modernas de dados — e meu interesse prático em construir soluções reais de engenharia de dados.

A proposta é simples e poderosa: **capturar vendas em tempo real, transformá-las com qualidade e permitir que qualquer pessoa faça perguntas sobre os dados em português**, sem precisar escrever uma linha de SQL.

É um projeto que une três grandes pilares da engenharia de dados moderna:

- **Infraestrutura de Streaming** — dados capturados no instante em que acontecem
- **Modelagem com dbt** — dados organizados em camadas, testados e documentados
- **IA Generativa** — interface conversacional que traduz perguntas em consultas SQL

---

## 🏗️ Arquitetura

```
[PostgreSQL Origem]
        │
        ▼
[Debezium CDC] ──► [Apache Kafka] ──► [Consumidor Python]
                                              │
                                              ▼
                                    [PostgreSQL Destino]
                                    ┌─────────────────┐
                                    │  🟤 Bronze Layer │  ← dados brutos
                                    │  🩶 Silver Layer │  ← dados limpos
                                    │  🥇 Gold Layer   │  ← métricas de negócio
                                    └─────────────────┘
                                              │
                                              ▼
                              [LangChain + Claude/Gemini]
                                              │
                                              ▼
                                    [Interface Streamlit]
                               "Qual foi o produto mais vendido?"
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Papel |
|---|---|---|
| Banco de Dados | PostgreSQL 14 | Origem e destino dos dados |
| CDC (Change Data Capture) | Debezium | Captura mudanças em tempo real via WAL |
| Mensageria | Apache Kafka | Barramento de eventos resiliente |
| Consumidor | Python + confluent-kafka | Processa e persiste eventos |
| Transformação | dbt (Data Build Tool) | Modelos incrementais e camadas Bronze/Silver/Gold |
| IA Generativa | LangChain + Claude (Anthropic) | Geração de SQL a partir de linguagem natural |
| Interface | Streamlit | Dashboard web para perguntas em português |
| Infraestrutura | Docker + Docker Compose | Orquestração de todos os serviços |

---

## 📂 Estrutura do Projeto

```
sales-pipeline/
├── docker-compose.yml          # Orquestração dos serviços
├── register_connector.sh       # Registro do conector Debezium
│
├── consumer/
│   ├── Dockerfile
│   └── consumer.py             # Consumidor Kafka → PostgreSQL
│   |__ requirements.txt
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── bronze/
│       │   └── bronze_vendas.sql
│       ├── silver/
│       │   └── silver_vendas.sql
│       └── gold/
│           └── gold_metricas_vendas.sql
│
└── ai_app/
    └── app.py                  # Interface Streamlit com IA
```

---

## ⚡ Como Rodar o Projeto

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.10+
- Chave de API da Anthropic (ou Google Gemini)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/sales-pipeline.git
cd sales-pipeline
```

### 2. Suba a infraestrutura

```bash
docker-compose up -d
```

Aguarde todos os containers iniciarem (~30 segundos), depois registre o conector Debezium:

```bash
bash register_connector.sh
```

### 3. Instale as dependências Python

```bash
pip install confluent-kafka psycopg2-binary dbt-postgres \
            streamlit langchain langchain-community \
            langchain-anthropic pandas
```

### 4. Configure sua chave de API

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

### 5. Inicie o consumidor

```bash
python consumer/consumer.py
```

### 6. Execute os modelos dbt

```bash
cd dbt_project
dbt run    # transforma os dados nas camadas Bronze → Silver → Gold
dbt test   # valida a qualidade dos dados
```

### 7. Rode a interface com IA

```bash
streamlit run ai_app/app.py
```

Acesse `http://localhost:8501` e faça sua primeira pergunta! 🎉

---

## 🧠 Como a IA Funciona

O fluxo de uma pergunta em linguagem natural:

```
1. Usuário digita: "Qual foi o produto mais vendido no último mês?"
          │
          ▼
2. LangChain captura a pergunta e o schema das tabelas Gold
          │
          ▼
3. Claude/Gemini analisa e gera o SQL correspondente:
   SELECT produto_id, SUM(unidades_vendidas) as total
   FROM gold_metricas_vendas
   WHERE mes_venda >= DATE_TRUNC('month', NOW() - INTERVAL '1 month')
   GROUP BY produto_id ORDER BY total DESC LIMIT 1;
          │
          ▼
4. O SQL é executado no banco (somente SELECT — read-only por segurança)
          │
          ▼
5. O resultado é exibido como tabela interativa no Streamlit
```

---

## 📊 Modelagem dbt — Camadas de Dados

### 🟤 Bronze — Dados Brutos
Espelho exato do que chegou via Kafka. Sem transformações, preservado para auditoria e reprocessamento.

### 🩶 Silver — Dados Limpos
Tipos de dados corrigidos, valores inválidos removidos, campos derivados calculados (ex: `mes_venda`). Modelo **incremental** — processa apenas registros novos desde a última execução.

### 🥇 Gold — Métricas de Negócio
Dados agregados prontos para análise: receita total, ticket médio, unidades vendidas por produto e período. É nesta camada que a IA realiza as consultas.

---

## 🔐 Segurança

- A conexão da IA com o banco é **somente leitura (read-only)**
- Apenas queries `SELECT` são permitidas — qualquer tentativa de `INSERT`, `UPDATE` ou `DELETE` é bloqueada em código
- Variáveis de ambiente para credenciais — nunca hardcoded

---

## 🎓 Contexto Acadêmico e Profissional

Este projeto é uma extensão prática da minha formação em **Banco de Dados pela Estácio**, onde desenvolvi sólida base em:

- Big Data com Python
- Modelagem e administração de bancos relacionais
- Fundamentos de arquitetura de dados

O pipeline aqui construído aplica e aprofunda esses conhecimentos em um cenário real de mercado, incorporando tecnologias que estão no centro das equipes de dados das maiores empresas do mundo: **streaming com Kafka, CDC com Debezium, transformação declarativa com dbt e IA generativa com LangChain**.

O objetivo é demonstrar que engenharia de dados moderna não se resume a mover arquivos — é sobre construir sistemas confiáveis, rastreáveis e inteligentes que geram valor de negócio em tempo real.

---

## 📚 Referências e Aprendizado

- [Documentação oficial do dbt](https://docs.getdbt.com/)
- [Debezium — Change Data Capture](https://debezium.io/documentation/)
- [Apache Kafka Quickstart](https://kafka.apache.org/quickstart)
- [LangChain SQL Agent](https://python.langchain.com/docs/use_cases/sql/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 🤝 Contribuições

Contribuições são bem-vindas! Abra uma issue ou envie um pull request com melhorias, correções ou novas funcionalidades.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Feito com dedicação por quem acredita que dados bem tratados transformam decisões. Gilnei Azambuja Borges - Profissional sempre aprendendo mais🔥
</p>

## 🔗 Conecte-se

[![Portfolio](https://img.shields.io/badge/Portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://medium.com/@gilnei809/gilnei-azambuja-borges-analista-de-dados-e-administrador-de-banco-de-dados-8774175b0e46)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gilnei-azambuja-borges-1a83432b)
[![Hugging Face](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/bluesky2019)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/gilneiborges)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=FW4VNKJWXLTCJ)
