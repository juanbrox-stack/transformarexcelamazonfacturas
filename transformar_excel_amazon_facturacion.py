import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Amazon Excel Transformer", layout="wide")

st.title("🔄 Amazon Data Transformer (Versión Excel)")
st.markdown("""
Sube el fichero de Amazon en formato **.xlsx** para evitar errores de columnas movidas.
""")

def transform_excel_data(df):
    # 1. Limpiar nombres de columnas por si acaso (quitar espacios o comillas)
    df.columns = [str(col).strip().replace('"', '') for col in df.columns]
    
    # 2. Definición de las columnas de precio para calcular el IMPORTE TOTAL
    # Amazon en Excel ya suele traer los números como formato numérico
    price_cols = [
        'OUR_PRICE Tax Inclusive Selling Price',
        'OUR_PRICE Tax Inclusive Promo Amount',
        'SHIPPING Tax Inclusive Selling Price',
        'SHIPPING Tax Inclusive Promo Amount',
        'GIFTWRAP Tax Inclusive Selling Price',
        'GIFTWRAP Tax Inclusive Promo Amount'
    ]
    
    # Asegurar que son números (por si vienen como texto)
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular Importe Total
    df['IMPORTE TOTAL'] = df[price_cols].sum(axis=1)

    # 3. Mapeo de columnas según tu necesidad
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

    # Crear dataframe final
    df_final = pd.DataFrame()
    for original, final in mapping.items():
        if original in df.columns:
            df_final[final] = df[original]
        else:
            df_final[final] = ""

    return df_final

# --- Interfaz de Usuario ---
uploaded_file = st.file_uploader("Elige el archivo EXCEL de Amazon (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        # Leer el Excel
        df_original = pd.read_excel(uploaded_file)
        
        st.success("Archivo leído correctamente.")
        
        # Procesar
        df_transformed = transform_excel_data(df_original)

        st.subheader("📊 Vista previa del fichero final")
        st.dataframe(df_transformed.head(10))

        # Botón para descargar de nuevo en Excel (es mejor para tus compañeros)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_transformed.to_excel(writer, index=False, sheet_name='Facturacion')
        
        st.download_button(
            label="📥 Descargar Resultado en Excel",
            data=buffer.getvalue(),
            file_name="amazon_final_procesado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al procesar el Excel: {e}")