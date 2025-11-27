import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Collins Demand Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS (VERSIÓN FINAL: SIDEBAR AZUL / TEXTO BLANCO) ---
st.markdown("""
    <style>
    /* =========================================
       1. PANEL PRINCIPAL (DERECHA) - CLARO
       ========================================= */
    /* Fondo General */
    [data-testid="stAppViewContainer"] {
        background-color: #f5f7f9 !important;
    }
    
    /* Texto Oscuro en el panel principal */
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] div[data-testid="stMarkdownContainer"] p {
        color: #0e2c4c !important;
    }

    /* Estilo de Tarjetas de Métricas (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Etiquetas dentro de los KPIs */
    div[data-testid="stMetricLabel"] label { color: #444444 !important; }
    div[data-testid="stMetricValue"] { color: #0e2c4c !important; }

    /* =========================================
       2. BARRA LATERAL (IZQUIERDA) - OSCURA
       ========================================= */
    /* Fondo Azul Corporativo */
    section[data-testid="stSidebar"] {
        background-color: #0e2c4c !important;
        border-right: 1px solid #0a1f35;
    }

    /* FUERZA BRUTA: Texto Blanco en TODO el Sidebar */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] li, 
    section[data-testid="stSidebar"] div.stMarkdown,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    /* Etiquetas específicas de los Filtros (Selectbox Labels) */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600; /* Un poco más negrita para leerse mejor */
    }
    
    /* Líneas divisorias blancas */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.4) !important;
    }

    /* Cajas de alerta (Info/Success) dentro del sidebar */
    section[data-testid="stSidebar"] .stAlert {
        background-color: rgba(255, 255, 255, 0.1) !important; /* Transparente */
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    section[data-testid="stSidebar"] .stAlert p {
        color: #ffffff !important;
    }

    /* =========================================
       3. GENERALES
       ========================================= */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CARGA DE DATOS ---
def cargar_datos():
    try:
        conn = sqlite3.connect("Collins_Demand_DB.db")
        df_hist = pd.read_sql("SELECT * FROM ventas_historicas", conn)
        df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha'])
        
        df_pron = pd.read_sql("SELECT * FROM pronosticos_activos", conn)
        df_pron['Fecha_Pronostico'] = pd.to_datetime(df_pron['Fecha_Pronostico'])
        conn.close()
        return df_hist, df_pron
    except Exception as e:
        return None, None

df_hist, df_pron = cargar_datos()

if df_hist is None or df_pron is None:
    st.error("⚠️ Error conectando a la base de datos. Ejecuta primero 'db_manager.py'.")
    st.stop()

# --- ENCABEZADO ---
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.markdown("# 💊") 
with col_titulo:
    st.title("Tablero Ejecutivo de Pronóstico de Demanda")
    st.markdown("### Proyecto Integrador Challenge CUGDL 2025B | Equipo: Quantum Analytics")

st.markdown("---")

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros")
st.sidebar.markdown("---")

# 1. Filtro CLIENTE
opciones_clientes = ["TODOS LOS CLIENTES (GLOBAL)"] + sorted(df_pron['Cliente_Descripcion'].unique().tolist())
cliente_sel = st.sidebar.selectbox("Seleccionar Cliente:", opciones_clientes)

# 2. Filtro PRODUCTO
if cliente_sel == "TODOS LOS CLIENTES (GLOBAL)":
    prods_disponibles = df_pron['Producto_Descripcion'].unique().tolist()
else:
    prods_disponibles = df_pron[df_pron['Cliente_Descripcion'] == cliente_sel]['Producto_Descripcion'].unique().tolist()

opciones_productos = ["TODOS LOS PRODUCTOS (TOTAL)"] + sorted(prods_disponibles)
prod_sel = st.sidebar.selectbox("Seleccionar Producto:", opciones_productos)

# --- LÓGICA DE VISTAS (GLOBAL VS INDIVIDUAL) ---

# A. Pronóstico
if cliente_sel == "TODOS LOS CLIENTES (GLOBAL)" and prod_sel == "TODOS LOS PRODUCTOS (TOTAL)":
    pron_view = df_pron.groupby('Fecha_Pronostico')[['Pronostico_Ensemble_PedidoPiezas', 'Pronostico_Min', 'Pronostico_Max']].sum().reset_index()
    titulo_contexto = "VISIÓN GLOBAL: TOTAL EMPRESA"
    cluster_info = "Mix Global"
elif cliente_sel == "TODOS LOS CLIENTES (GLOBAL)":
    pron_view = df_pron[df_pron['Producto_Descripcion'] == prod_sel].groupby('Fecha_Pronostico')[['Pronostico_Ensemble_PedidoPiezas', 'Pronostico_Min', 'Pronostico_Max']].sum().reset_index()
    titulo_contexto = f"Global: {prod_sel}"
    cluster_info = df_pron[df_pron['Producto_Descripcion'] == prod_sel]['Cluster'].iloc[0]
elif prod_sel == "TODOS LOS PRODUCTOS (TOTAL)":
    pron_view = df_pron[df_pron['Cliente_Descripcion'] == cliente_sel].groupby('Fecha_Pronostico')[['Pronostico_Ensemble_PedidoPiezas', 'Pronostico_Min', 'Pronostico_Max']].sum().reset_index()
    titulo_contexto = f"Total Cliente: {cliente_sel}"
    cluster_info = "Mix Cliente"
else:
    pron_view = df_pron[(df_pron['Cliente_Descripcion'] == cliente_sel) & (df_pron['Producto_Descripcion'] == prod_sel)].copy()
    titulo_contexto = f"{cliente_sel} | {prod_sel}"
    cluster_info = pron_view['Cluster'].iloc[0] if not pron_view.empty else "N/A"

# B. Histórico
if cliente_sel == "TODOS LOS CLIENTES (GLOBAL)" and prod_sel == "TODOS LOS PRODUCTOS (TOTAL)":
    hist_view = df_hist.groupby('Fecha')[['Pedido_Piezas']].sum().reset_index()
elif cliente_sel == "TODOS LOS CLIENTES (GLOBAL)":
    hist_view = df_hist[df_hist['Producto_Descripcion'] == prod_sel].groupby('Fecha')[['Pedido_Piezas']].sum().reset_index()
elif prod_sel == "TODOS LOS PRODUCTOS (TOTAL)":
    hist_view = df_hist[df_hist['Cliente_Descripcion'] == cliente_sel].groupby('Fecha')[['Pedido_Piezas']].sum().reset_index()
else:
    hist_view = df_hist[(df_hist['Cliente_Descripcion'] == cliente_sel) & (df_hist['Producto_Descripcion'] == prod_sel)].copy()

pron_view = pron_view.sort_values('Fecha_Pronostico')
hist_view = hist_view.sort_values('Fecha')

# --- INFO EN SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.info(f"**Cluster:** {cluster_info}")
st.sidebar.success(f"**Vista:** {titulo_contexto}")

# --- KPIs ---
st.subheader(f"Resumen: {titulo_contexto}")

col1, col2, col3, col4 = st.columns(4)

if not pron_view.empty:
    suma_pron = pron_view['Pronostico_Ensemble_PedidoPiezas'].sum()
    suma_min = pron_view['Pronostico_Min'].sum()
    suma_max = pron_view['Pronostico_Max'].sum()
    prom_mensual = suma_pron / 12
else:
    suma_pron = 0; suma_min = 0; suma_max = 0; prom_mensual = 0

col1.metric("Demanda Total (12 Meses)", f"{suma_pron:,.0f} pzas")
col2.metric("Escenario Mínimo", f"{suma_min:,.0f} pzas")
col3.metric("Escenario Máximo", f"{suma_max:,.0f} pzas")
col4.metric("Promedio Mensual", f"{prom_mensual:,.0f} pzas")

st.markdown("---")

# --- GRÁFICA ---
st.subheader("📈 Tendencia Histórica y Proyección")

if not hist_view.empty or not pron_view.empty:
    fig = go.Figure()

    # Histórico
    if not hist_view.empty:
        fig.add_trace(go.Scatter(x=hist_view['Fecha'], y=hist_view['Pedido_Piezas'], mode='lines', name='Histórico Real', line=dict(color='#1f77b4', width=2)))

    # Pronóstico
    if not pron_view.empty:
        fig.add_trace(go.Scatter(x=pron_view['Fecha_Pronostico'], y=pron_view['Pronostico_Ensemble_PedidoPiezas'], mode='lines+markers', name='Pronóstico Ensemble', line=dict(color='#ff7f0e', width=3, dash='dash')))
        
        # Bandas
        fig.add_trace(go.Scatter(x=pron_view['Fecha_Pronostico'], y=pron_view['Pronostico_Max'], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=pron_view['Fecha_Pronostico'], y=pron_view['Pronostico_Min'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(255, 127, 14, 0.2)', name='Rango de Confianza'))

    # Layout
    fig.update_layout(
        title=dict(text=f"Análisis: {titulo_contexto}", font=dict(color="#0e2c4c", size=20)),
        xaxis=dict(title="Fecha", title_font=dict(color="#0e2c4c"), tickfont=dict(color="#0e2c4c")),
        yaxis=dict(title="Pedidos (Piezas)", title_font=dict(color="#0e2c4c"), tickfont=dict(color="#0e2c4c")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#0e2c4c")),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos para mostrar en esta selección.")

# --- TABLA ---
with st.expander(f"Ver Tabla de Datos: {titulo_contexto}"):
    if not pron_view.empty:
        cols_to_show = ['Fecha_Pronostico', 'Pronostico_Ensemble_PedidoPiezas', 'Pronostico_Min', 'Pronostico_Max']
        st.dataframe(pron_view[cols_to_show], use_container_width=True)
        
        csv = pron_view
