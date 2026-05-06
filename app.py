import streamlit as st
import psycopg2
import pandas as pd
import google.generativeai as genai

# ── Configuracao do banco ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "vendas_dw",
    "user": "admin",
    "password": "admin123"
}

# ── Conexao com o banco ────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def executar_query(sql):
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        conn.close()

# ── Schema para contexto da IA ─────────────────────────────────────────────────
SCHEMA_CONTEXT = """
Voce e um especialista em SQL e dados de vendas.
Responda APENAS com o codigo SQL puro, sem explicacoes, sem markdown, sem backticks.
Use apenas SELECT. Nunca use INSERT, UPDATE, DELETE ou DROP.

Tabelas disponiveis no banco 'vendas_dw':

1. public_gold.gold_metricas_vendas
   - mes_venda (timestamp): mes de referencia
   - produto_id (integer): id do produto
   - total_pedidos (bigint): quantidade de pedidos
   - unidades_vendidas (numeric): total de unidades
   - receita_total (numeric): receita total em reais
   - ticket_medio (numeric): valor medio por pedido
   - maior_venda (numeric): maior venda do periodo
   - menor_venda (numeric): menor venda do periodo

2. public_silver.silver_vendas
   - venda_id (integer): id unico da venda
   - cliente_id (integer): id do cliente
   - produto_id (integer): id do produto
   - valor (numeric): valor da venda
   - quantidade (integer): quantidade vendida
   - data_venda (timestamp): data e hora da venda
   - mes_venda (timestamp): mes da venda

Exemplos:
P: Qual produto teve maior receita?
R: SELECT produto_id, receita_total FROM public_gold.gold_metricas_vendas ORDER BY receita_total DESC LIMIT 1;

P: Quantas vendas foram feitas?
R: SELECT COUNT(*) as total_vendas FROM public_silver.silver_vendas;

P: Qual o ticket medio por produto?
R: SELECT produto_id, ticket_medio FROM public_gold.gold_metricas_vendas ORDER BY ticket_medio DESC;

P: Liste todas as vendas ordenadas por valor
R: SELECT venda_id, cliente_id, produto_id, valor, quantidade, data_venda FROM public_silver.silver_vendas ORDER BY valor DESC;
"""

# ── Interface Streamlit ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Consultor de Vendas com IA",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Consultor de Vendas com IA")
st.caption("Pergunte sobre suas vendas em portugues — o Gemini gera o SQL e retorna os dados!")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuracao")
    api_key = st.text_input(
        "Chave API Google Gemini",
        type="password",
        placeholder="AIza..."
    )
    st.caption("Obtenha sua chave gratuita em: aistudio.google.com")
    st.divider()

    st.header("📋 Historico")
    if "historico" not in st.session_state:
        st.session_state.historico = []

    if st.session_state.historico:
        for i, item in enumerate(reversed(st.session_state.historico[-5:])):
            st.markdown(f"**{i+1}.** {item['pergunta'][:40]}...")
            st.caption(f"↳ {item['registros']} registro(s)")
    else:
        st.caption("Nenhuma consulta ainda.")

    if st.button("🗑️ Limpar historico"):
        st.session_state.historico = []
        st.rerun()

# ── Area principal ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    pergunta = st.text_input(
        "💬 Sua pergunta:",
        placeholder="Ex: Qual foi o produto mais vendido? Qual a receita total?",
    )
with col2:
    st.write("")
    st.write("")
    consultar = st.button("🔍 Consultar", type="primary", use_container_width=True)

# Sugestoes rapidas
st.markdown("**💡 Sugestoes rapidas:**")
cols = st.columns(4)
sugestoes = [
    "Qual produto teve maior receita?",
    "Quantas vendas foram feitas?",
    "Qual o ticket medio por produto?",
    "Liste todas as vendas por valor"
]
for i, sug in enumerate(sugestoes):
    if cols[i].button(sug, use_container_width=True):
        pergunta = sug
        consultar = True

st.divider()

# ── Processamento ──────────────────────────────────────────────────────────────
if consultar and pergunta:
    if not api_key:
        st.error("⚠️ Insira sua chave da API do Google Gemini na barra lateral!")
        st.stop()

    with st.spinner("🤔 Gerando SQL com Gemini..."):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-lite")
            prompt = f"{SCHEMA_CONTEXT}\n\nPergunta: {pergunta}"
            response = model.generate_content(prompt)
            sql_gerado = response.text.strip()
            sql_gerado = sql_gerado.replace("```sql", "").replace("```", "").strip()
        except Exception as e:
            st.error(f"Erro na API Gemini: {e}")
            st.stop()

    if not sql_gerado.upper().startswith("SELECT"):
        st.error("⚠️ Apenas consultas SELECT sao permitidas por seguranca.")
        with st.expander("Ver resposta da IA"):
            st.write(sql_gerado)
        st.stop()

    with st.spinner("⚡ Executando consulta no banco..."):
        df, erro = executar_query(sql_gerado)

    if erro:
        st.error(f"Erro na consulta: {erro}")
        with st.expander("SQL gerado pela IA"):
            st.code(sql_gerado, language="sql")
    else:
        st.success(f"✅ {len(df)} registro(s) encontrado(s)")

        tab1, tab2, tab3 = st.tabs(["📋 Dados", "📈 Grafico", "🔎 SQL Gerado"])

        with tab1:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Baixar CSV",
                csv,
                "resultado.csv",
                "text/csv",
                use_container_width=True
            )

        with tab2:
            colunas_numericas = df.select_dtypes(include="number").columns.tolist()
            if len(colunas_numericas) >= 1 and len(df) > 0:
                col_x = df.columns[0]
                col_y = st.selectbox(
                    "Escolha a metrica para o grafico:",
                    colunas_numericas
                )
                st.bar_chart(df.set_index(col_x)[col_y])
            else:
                st.info("Sem dados numericos suficientes para grafico.")

        with tab3:
            st.code(sql_gerado, language="sql")

        st.session_state.historico.append({
            "pergunta": pergunta,
            "sql": sql_gerado,
            "registros": len(df)
        })

elif not consultar:
    st.info("👆 Digite uma pergunta acima ou clique em uma sugestao rapida para comecar!")
