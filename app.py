import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_anthropic import ChatAnthropic
import psycopg2

# Configuração
DB_URI = "postgresql://admin:admin123@localhost:5433/vendas_dw"
db = SQLDatabase.from_uri(DB_URI, include_tables=["gold_metricas_vendas", "silver_vendas"])

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key="SUA_CHAVE_AQUI"
)

chain = create_sql_query_chain(llm, db)

# Interface Streamlit
st.set_page_config(page_title="📊 Consultor de Vendas com IA", layout="wide")
st.title("🤖 Consultor de Vendas — Perguntas em Linguagem Natural")
st.caption("Faça qualquer pergunta sobre suas vendas em português!")

pergunta = st.text_input(
    "💬 Sua pergunta:",
    placeholder="Ex: Qual foi o produto mais vendido no último mês?"
)

if st.button("Consultar", type="primary") and pergunta:
    with st.spinner("🤔 Analisando sua pergunta..."):
        try:
            # Gera o SQL a partir da pergunta
            sql_gerado = chain.invoke({"question": pergunta})
            
            # Executa no banco (somente SELECT - segurança)
            if sql_gerado.strip().upper().startswith("SELECT"):
                conn = psycopg2.connect(DB_URI)
                cursor = conn.cursor()
                cursor.execute(sql_gerado)
                resultado = cursor.fetchall()
                colunas = [desc[0] for desc in cursor.description]
                conn.close()
                
                st.success("✅ Consulta realizada!")
                st.code(sql_gerado, language="sql")
                
                import pandas as pd
                df = pd.DataFrame(resultado, columns=colunas)
                st.dataframe(df, use_container_width=True)
            else:
                st.error("⚠️ Apenas consultas SELECT são permitidas por segurança.")
        except Exception as e:
            st.error(f"Erro: {e}")