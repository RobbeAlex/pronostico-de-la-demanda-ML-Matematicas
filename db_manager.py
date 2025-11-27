import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Nombre del archivo de base de datos
DB_NAME = "Collins_Demand_DB.db"

def get_connection():
    """Crea y devuelve una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_tablas():
    """Crea las tablas necesarias si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabla de Ventas Históricas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_historicas (
            Fecha DATETIME,
            Producto_Descripcion TEXT,
            Cliente_Descripcion TEXT,
            Pedido_Piezas REAL
        )
    ''')

    # 2. Tabla de Pronósticos Activos (con las columnas exactas de tu PDF)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pronosticos_activos (
            Fecha_Pronostico DATETIME,
            Producto_Descripcion TEXT,
            Cliente_Descripcion TEXT,
            Cluster INTEGER,
            Pronostico_Ensemble_PedidoPiezas REAL,
            Pronostico_Min REAL,
            Pronostico_Max REAL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Base de datos '{DB_NAME}' y tablas verificadas.")

def guardar_datos_reales(df_historico, df_pronostico):
    """
    Función para guardar tus DataFrames reales del Challenge.
    Usa esta función en tu script principal 'SOLUTION_CHALLENGE'.
    """
    conn = get_connection()

    # Reemplazamos la historia y el pronóstico anterior con lo nuevo
    if df_historico is not None:
        df_historico.to_sql('ventas_historicas', conn, if_exists='replace', index=False)
        print(f"--> Guardados {len(df_historico)} registros históricos.")

    if df_pronostico is not None:
        df_pronostico.to_sql('pronosticos_activos', conn, if_exists='replace', index=False)
        print(f"--> Guardados {len(df_pronostico)} registros de pronóstico.")

    conn.close()
    print("✅ Carga de datos a SQL completada.")

# --- GENERADOR DE DATOS DE PRUEBA (SOLO PARA QUE PRUEBES LA APP YA) ---
def generar_datos_dummy():
    print("⚠️ Generando datos de prueba para demostración...")
    fechas_hist = pd.date_range(start="2023-01-01", end="2025-08-01", freq="MS")
    fechas_fut = pd.date_range(start="2025-09-01", periods=12, freq="MS")

    productos = ["ANALGESICO + ANTIPERETICO TABLETAS 1", "ANTIBIOTICO SOLUCIONES INYECTABLE 2"]
    clientes = ["Cliente 1", "Cliente 2"]

    lista_hist = []
    lista_pron = []

    for prod in productos:
        for cli in clientes:
            # Datos Históricos Dummy
            base_val = np.random.randint(50000, 150000)
            for fecha in fechas_hist:
                val = base_val + np.random.randint(-10000, 10000)
                lista_hist.append([fecha, prod, cli, val])

            # Datos Pronóstico Dummy
            for fecha in fechas_fut:
                pred = base_val * 1.05 # Leve crecimiento
                lista_pron.append([
                    fecha, prod, cli,
                    np.random.choice([0, 1, 2, 3]), # Cluster aleatorio
                    pred,
                    pred * 0.8, # Min
                    pred * 1.2  # Max
                ])

    df_h = pd.DataFrame(lista_hist, columns=['Fecha', 'Producto_Descripcion', 'Cliente_Descripcion', 'Pedido_Piezas'])
    df_p = pd.DataFrame(lista_pron, columns=['Fecha_Pronostico', 'Producto_Descripcion', 'Cliente_Descripcion', 'Cluster',
                                             'Pronostico_Ensemble_PedidoPiezas', 'Pronostico_Min', 'Pronostico_Max'])

    guardar_datos_reales(df_h, df_p)

if __name__ == "__main__":
    # Al ejecutar este script directamente, se crea la BD y se llena con datos falsos
    inicializar_tablas()
    generar_datos_dummy()
    print("\nLISTO: Ahora ejecuta 'streamlit run app_dashboard.py' en tu terminal.")