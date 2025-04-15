import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Conecta ao banco e retorna os dados
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect('logs.db')
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df

# Configuração do app
st.set_page_config(page_title="CyberGuardian Dashboard", layout="wide")
st.title("🔐 CyberGuardian - Monitoramento de Tentativas de Acesso")

# Carrega os dados
df = carregar_dados()

if df.empty:
    st.warning("Nenhuma tentativa registrada ainda.")
else:
    # KPIs
    col1, col2 = st.columns(2)
    col1.metric("🔁 Tentativas Registradas", len(df))
    col2.metric("👤 IPs únicos", df['ip'].nunique())

    st.markdown("---")

    # Tabela de registros
    with st.expander("📄 Ver todos os registros"):
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

    # IPs mais frequentes
    ip_count = df['ip'].value_counts().reset_index()
    ip_count.columns = ['IP', 'Tentativas']
    fig_ips = px.bar(ip_count, x='IP', y='Tentativas', title="🌍 IPs mais frequentes")
    st.plotly_chart(fig_ips, use_container_width=True)

    # Tentativas por hora
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hora'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:00:00')
    hora_count = df.groupby('hora').size().reset_index(name='Tentativas')
    fig_hora = px.line(hora_count, x='hora', y='Tentativas', markers=True, title="🕓 Tentativas por Hora")
    st.plotly_chart(fig_hora, use_container_width=True)
