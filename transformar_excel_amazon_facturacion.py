import streamlit as st
import pandas as pd
import io
import csv

st.set_page_config(page_title="Amazon Converter PRO", layout="wide")

st.title("🔄 Transformador de Facturación Amazon")
st.info("Esta versión corrige el desplazamiento de columnas y descuadres.")

def process_amazon_file(uploaded_file):
    # Leer el contenido bruto
    raw_text = uploaded_file.read().decode("utf-8")
    
    # 1. Limpieza de las filas "envueltas" en comillas
    cleaned_lines = []
    for line in raw_text.splitlines():
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1] # Quitar comillas de los extremos
        line = line.replace('""', '"') # Convertir dobles comillas en simples
        cleaned_lines.append(line)
    
    # 2. Convertir a DataFrame usando el motor de python para mayor precisión
    final_io = io.StringIO("\n".join(cleaned_lines))
    df = pd.read_csv(final_io, sep=',', quoting=csv.QUOTE_MINIMAL)
    
    # Limpiar posibles espacios en los nombres de columnas
    df.columns = [c.strip().replace('"', '') for c in df.columns]
    return df

def transform_logic(df):
    # Columnas necesarias para el cálculo del total
    cols_money = [
        'OUR_PRICE Tax Inclusive Selling Price', 'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price', 'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price', 'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    
    # Convertir a numérico asegurando que el punto es el decimal
    for col in cols_money:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Cálculo del IMPORTE TOTAL
    df['IMPORTE TOTAL'] = df[cols_money].sum(axis=1)

    # Diccionario de Mapeo Exacto (Origen: Destino)
    mapping = {
        'Order Date': 'Order Date',
        'Transaction Type': 'Transaction Type',
        'Order ID': 'Order ID',
        'Shipment Date': 'Shipment Date',
        'SKU': 'SKU',
        'Quantity': 'Quantity',
        'Tax Rate': 'Tax Rate',
        'Tax Reporting Scheme': 'Tax Reporting Scheme',
        'Jurisdiction Name': 'Jurisdiction Name',
        'IMPORTE TOTAL': 'IMPORTE TOTAL',
        'Buyer Tax Registration': 'Buyer Tax Registration',
        'Buyer Tax Registration Jurisdiction': 'Buyer Tax Registration Jurisdiction',
        'VAT Invoice Number': 'VAT Invoice Number',
        'Ship To Country': 'Ship To Country'
    }

    # Crear el dataframe final manteniendo solo las columnas del mapeo
    res_df = pd.DataFrame()
    for ori, dest in mapping.items():
        if ori in df.columns:
            res_df[dest] = df[ori]
        else:
            res_df[dest] = "" # Columna vacía si no existe
            
    return res_df

# --- UI ---
file = st.file_uploader("Sube el archivo CSV", type=["csv"])

if file:
    try:
        df_raw = process_amazon_file(file)
        df_final = transform_logic(df_raw)
        
        st.success(f"Procesadas {len(df_final)} filas.")
        
        st.subheader("Vista previa del resultado")
        st.dataframe(df_final.head(10))
        
        # Preparar descarga
        csv_buffer = io.StringIO()
        df_final.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig') # Usamos ; para que Excel lo abra bien
        
        st.download_button(
            label="📥 Descargar CSV Final (Formato Excel)",
            data=csv_buffer.getvalue(),
            file_name="Facturacion_Amazon_Final.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error en el procesado: {e}")