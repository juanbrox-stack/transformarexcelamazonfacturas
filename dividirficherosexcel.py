import streamlit as st
import pandas as pd
import io
import zipfile

# Configuración de la página
st.set_page_config(page_title="Divisor de Excel Pro", page_icon="✂️")

st.title("✂️ Divisor de Excel con Encabezados")
st.info("Este proceso mantendrá la fila 1 (nombres de columnas) en todos los archivos generados.")

# 1. Subida del archivo
uploaded_file = st.file_uploader("Sube tu archivo .xlsx o .xls", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Cargamos el Excel completo en memoria
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    columnas = df.columns.tolist() # Guardamos los nombres de las columnas
    
    st.write(f"✅ Archivo detectado con **{total_rows}** filas y **{len(columnas)}** columnas.")

    # 2. Parámetros de división
    rows_per_file = st.number_input(
        "Número de filas de datos por archivo:", 
        min_value=1, 
        max_value=total_rows, 
        value=500
    )

    if st.button("Generar Archivos"):
        # Creamos el contenedor para el ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Calculamos cuántos archivos saldrán
            for i in range(0, total_rows, rows_per_file):
                # Seleccionamos el bloque de filas actual
                chunk = df.iloc[i : i + rows_per_file]
                
                # Nombre del archivo individual
                chunk_idx = (i // rows_per_file) + 1
                filename = f"parte_{chunk_idx}.xlsx"
                
                # Guardamos el bloque en un buffer de Excel
                buffer_excel = io.BytesIO()
                with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
                    # 'header=True' asegura que la fila 1 se incluya siempre
                    chunk.to_excel(writer, index=False, header=True, sheet_name='Datos')
                
                # Metemos el Excel en el ZIP
                zf.writestr(filename, buffer_excel.getvalue())
        
        st.success(f"¡Listo! Se han creado {chunk_idx} archivos.")
        
        # 3. Botón para descargar el resultado
        st.download_button(
            label="📥 Descargar todos los archivos (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="excel_dividido.zip",
            mime="application/zip"
        )