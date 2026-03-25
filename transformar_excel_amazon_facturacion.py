import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Amazon Data Transformer", layout="wide")

st.title("🔄 Transformador de Facturación Amazon")
st.markdown("""
Sube el fichero CSV original de Amazon y descarga la versión procesada lista para contabilidad.
""")

def transform_data(df):
    # 1. Limpieza de nombres de columnas (eliminar comillas dobles extras si existen)
    df.columns = [col.replace('"', '') for col in df.columns]
    
    # 2. Definición de las columnas de precio para calcular el IMPORTE TOTAL
    # Sumamos el precio y las promociones (que suelen venir en negativo)
    # Columnas: OUR_PRICE, SHIPPING y GIFTWRAP (Tax Inclusive)
    price_cols = [
        'OUR_PRICE Tax Inclusive Selling Price',
        'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price',
        'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price',
        'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    
    # Asegurarnos de que son numéricas
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular Importe Total
    df['IMPORTE TOTAL'] = df[price_cols].sum(axis=1)

    # 3. Mapeo de columnas según el formato final solicitado
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

    # Seleccionar solo las columnas que existen en el dataframe y renombrarlas
    # Si alguna columna falta en el origen, se crea vacía
    final_cols = []
    df_final = pd.DataFrame()
    
    for original, final in mapping.items():
        if original in df.columns:
            df_final[final] = df[original]
        else:
            df_final[final] = ""

    return df_final

# --- Interfaz de Usuario ---
uploaded_file = st.file_uploader("Elige el archivo CSV de Amazon", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo. Amazon suele usar codificación especial o delimitadores según el marketplace
        # Probamos con coma, si falla el usuario verá el error
        df_original = pd.read_csv(uploaded_file, quoting=0)
        
        st.success("Archivo cargado correctamente.")
        
        with st.expander("Ver datos originales (primeras 5 filas)"):
            st.write(df_original.head())

        # Transformación
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
            file_name="amazon_facturacion_final.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo es el CSV original descargado de Amazon Seller Central.")