import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Herramienta de División Excel", page_icon="✂️")

st.title("✂️ Procesador y Divisor de Excel")

# Sidebar para elegir la funcionalidad
st.sidebar.header("Configuración")
modo = st.sidebar.radio(
    "Selecciona el modo de división:",
    ("Por Filas (Fragmentos)", "Por Columnas (Específico por SKU)")
)

uploaded_file = st.file_uploader("Sube tu archivo .xlsx", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    total_cols = len(df.columns)
    
    st.write(f"📊 Archivo cargado: **{total_rows}** filas y **{total_cols}** columnas.")

    # --- LÓGICA MODO FILAS ---
    if modo == "Por Filas (Fragmentos)":
        st.subheader("División por número de filas")
        rows_per_file = st.number_input("Filas por archivo:", min_value=1, value=500)
        
        if st.button("Generar Archivos por Filas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(0, total_rows, rows_per_file):
                    chunk = df.iloc[i : i + rows_per_file]
                    idx = (i // rows_per_file) + 1
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        chunk.to_excel(writer, index=False)
                    zf.writestr(f"division_filas_{idx}.xlsx", output.getvalue())
            
            st.download_button("📥 Descargar ZIP (Filas)", zip_buffer.getvalue(), "excel_filas.zip")

    # --- LÓGICA MODO COLUMNAS ---
    else:
        st.subheader("División por columnas (SKU + Columna)")
        st.info("Se creará un archivo por cada columna, manteniendo siempre la primera columna (SKUs).")
        
        col_sku = df.columns[0]
        otras_columnas = df.columns[1:]
        
        st.write(f"Columna fija: **{col_sku}**")
        st.write(f"Se generarán **{len(otras_columnas)}** archivos.")

        if st.button("Generar Archivos por Columnas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for col_name in otras_columnas:
                    # Seleccionamos la columna de SKU (0) y la columna actual
                    columnas_a_guardar = [col_sku, col_name]
                    df_temp = df[columnas_a_guardar]
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_temp.to_excel(writer, index=False)
                    
                    # Usamos el nombre de la columna para el nombre del archivo
                    safe_name = "".join([c for c in col_name if c.isalnum() or c in (' ', '_')]).strip()
                    zf.writestr(f"columna_{safe_name}.xlsx", output.getvalue())
            
            st.download_button("📥 Descargar ZIP (Columnas)", zip_buffer.getvalue(), "excel_columnas.zip")