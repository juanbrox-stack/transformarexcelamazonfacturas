import streamlit as st
import pandas as pd
import io
import csv

st.set_page_config(page_title="Amazon Multi-Sheet Transformer", layout="wide")

st.title("🔄 Amazon Transformer: Pestañas por Tax Scheme")
st.markdown("El archivo final tendrá una pestaña diferente para cada tipo de **Tax Reporting Scheme**.")

def clean_and_load(uploaded_file):
    """Detecta el formato y limpia las comillas de Amazon."""
    df = None
    # Intento como Excel
    if uploaded_file.name.endswith('.xlsx'):
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except:
            pass
    
    # Intento como Texto (CSV/TXT) si falla Excel
    if df is None:
        uploaded_file.seek(0)
        try:
            raw = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            raw = uploaded_file.read().decode("latin-1")
            
        cleaned = []
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            line = line.replace('""', '"')
            cleaned.append(line)
        df = pd.read_csv(io.StringIO("\n".join(cleaned)), sep=',', quoting=csv.QUOTE_MINIMAL)
    
    return df

def transform_logic(df):
    # Limpieza de nombres de columnas
    df.columns = [str(col).strip().replace('"', '') for col in df.columns]
    
    # Cálculo de Importe
    price_cols = [
        'OUR_PRICE Tax Inclusive Selling Price', 'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price', 'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price', 'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['IMPORTE TOTAL'] = df[price_cols].sum(axis=1)

    # Mapeo de columnas solicitado
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

    res_df = pd.DataFrame()
    for ori, dest in mapping.items():
        if ori in df.columns:
            res_df[dest] = df[ori]
        else:
            res_df[dest] = ""
    return res_df

uploaded_file = st.file_uploader("Sube el fichero original de Amazon", type=["xlsx", "csv", "txt"])

if uploaded_file:
    df_raw = clean_and_load(uploaded_file)
    
    if df_raw is not None:
        df_final = transform_logic(df_raw)
        
        # --- Lógica de Pestañas ---
        # Reemplazamos valores nulos por "VACIO" para poder agrupar
        df_final['Tax Reporting Scheme'] = df_final['Tax Reporting Scheme'].fillna('VACIO').replace('', 'VACIO')
        grupos = df_final.groupby('Tax Reporting Scheme')

        st.success(f"Procesadas {len(df_final)} líneas en total.")
        
        # Mostrar resumen en la web
        for name, group in grupos:
            st.write(f"Pestaña **{name}**: {len(group)} registros")

        # Crear el archivo Excel con múltiples pestañas
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for name, group in grupos:
                # El nombre de la pestaña no puede tener más de 31 caracteres
                sheet_name = str(name)[:31]
                group.to_excel(writer, index=False, sheet_name=sheet_name)
        
        st.download_button(
            label="📥 Descargar Excel con Pestañas",
            data=output.getvalue(),
            file_name="Amazon_Facturacion_Organizado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )