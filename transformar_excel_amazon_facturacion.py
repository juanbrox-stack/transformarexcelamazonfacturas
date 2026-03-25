import streamlit as st
import pandas as pd
import io
import csv

st.set_page_config(page_title="Amazon Universal Transformer", layout="wide")

st.title("🔄 Amazon Data Transformer")
st.markdown("Sube el fichero de Amazon (ya sea .xlsx o .csv). La app detectará el formato automáticamente.")

def transform_logic(df):
    # Limpiar nombres de columnas (quitar comillas y espacios)
    df.columns = [str(col).strip().replace('"', '') for col in df.columns]
    
    # Columnas para el cálculo del total
    price_cols = [
        'OUR_PRICE Tax Inclusive Selling Price', 'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price', 'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price', 'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    
    # Convertir a numérico
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular TOTAL
    df['IMPORTE TOTAL'] = df[price_cols].sum(axis=1)

    # Mapeo final
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

uploaded_file = st.file_uploader("Sube el archivo aquí", type=["xlsx", "csv", "txt"])

if uploaded_file is not None:
    df = None
    
    # INTENTO 1: Leer como Excel Real
    if uploaded_file.name.endswith('.xlsx'):
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except Exception:
            st.warning("No parece un Excel real. Intentando leer como archivo de texto...")

    # INTENTO 2: Si el primero falla o es CSV, leer como Texto/CSV con limpieza
    if df is None:
        try:
            uploaded_file.seek(0) # Volver al inicio del archivo
            raw_content = uploaded_file.read().decode("utf-8")
            
            # Limpiar el formato extraño de Amazon (comillas envolventes)
            cleaned_lines = []
            for line in raw_content.splitlines():
                line = line.strip()
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1]
                line = line.replace('""', '"')
                cleaned_lines.append(line)
            
            df = pd.read_csv(io.StringIO("\n".join(cleaned_lines)), sep=',', quoting=csv.QUOTE_MINIMAL)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    # Si logramos cargar el DataFrame, lo transformamos
    if df is not None:
        try:
            df_final = transform_logic(df)
            st.success(f"¡Hecho! Procesadas {len(df_final)} filas.")
            st.dataframe(df_final.head(10))

            # Descarga siempre en Excel para evitar problemas de comas
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Amazon_Procesado')
            
            st.download_button(
                label="📥 Descargar Resultado en Excel",
                data=output.getvalue(),
                file_name="amazon_final.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error en la transformación de datos: {e}")