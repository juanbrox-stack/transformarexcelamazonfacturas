import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Amazon Data Transformer", layout="wide")

st.title("🔄 Transformador de Facturación Amazon")
st.markdown("""
Sube el fichero CSV original de Amazon. Esta versión corrige el error de formato de comillas dobles.
""")

def clean_amazon_csv(file_content):
    """
    Amazon envuelve cada fila en comillas extras. 
    Esta función limpia el texto para que sea un CSV estándar.
    """
    lines = file_content.decode("utf-8").splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Eliminar comilla inicial y final si existen
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        # Reemplazar las dobles comillas internas ("") por comillas simples (")
        line = line.replace('""', '"')
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def transform_data(df):
    # 1. Asegurar que los nombres de columnas no tengan espacios extra
    df.columns = [col.strip() for col in df.columns]
    
    # 2. Definición de las columnas de precio para calcular el IMPORTE TOTAL
    price_cols = [
        'OUR_PRICE Tax Inclusive Selling Price',
        'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price',
        'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price',
        'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    
    # Convertir a numérico (Amazon usa punto como decimal en estos ficheros)
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular Importe Total (Suma de precios y promociones)
    df['IMPORTE TOTAL'] = df[price_cols].sum(axis=1)

    # 3. Mapeo de columnas solicitado
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

    df_final = pd.DataFrame()
    for original, final in mapping.items():
        if original in df.columns:
            df_final[final] = df[original]
        else:
            df_final[final] = "" # Crear columna vacía si no existe en origen

    return df_final

# --- Interfaz de Usuario ---
uploaded_file = st.file_uploader("Elige el archivo CSV de Amazon", type="csv")

if uploaded_file is not None:
    try:
        # Paso 1: Leer el contenido bruto y limpiarlo
        raw_content = uploaded_file.read()
        cleaned_csv_str = clean_amazon_csv(raw_content)
        
        # Paso 2: Cargar en Pandas
        df_original = pd.read_csv(io.StringIO(cleaned_csv_str))
        
        st.success("Archivo procesado y limpiado con éxito.")
        
        # Paso 3: Transformar
        df_transformed = transform_data(df_original)

        st.subheader("📊 Vista previa del fichero final")
        st.dataframe(df_transformed.head(10))

        # Botón de descarga
        output = io.StringIO()
        df_transformed.to_csv(output, index=False)
        csv_data = output.getvalue()

        st.download_button(
            label="📥 Descargar CSV Transformado",
            data=csv_data,
            file_name="amazon_procesado.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Error crítico al procesar el archivo: {e}")
        st.info("Asegúrate de que estás subiendo el archivo CSV sin haberlo modificado antes en Excel.")