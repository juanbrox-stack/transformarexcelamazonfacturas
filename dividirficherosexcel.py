import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Divisor de Excel Pro", page_icon="📊")

st.title("📊 Procesador de Archivos Excel")

# Opciones justo debajo del título
opcion = st.radio(
    "¿Qué deseas hacer?",
    ("Dividir por número de filas", "Dividir por columnas (Manteniendo SKU)"),
    horizontal=True # Para que se vea más compacto
)

st.markdown("---")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Carga de datos
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    total_cols = len(df.columns)
    
    st.info(f"📋 Archivo detectado: {total_rows} filas y {total_cols} columnas.")

    # --- LÓGICA 1: DIVISIÓN POR FILAS ---
    if opcion == "Dividir por número de filas":
        rows_per_file = st.number_input("Filas por archivo:", min_value=1, value=500)
        
        if st.button("Generar y Preparar Descarga"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(0, total_rows, rows_per_file):
                    chunk = df.iloc[i : i + rows_per_file]
                    chunk_num = (i // rows_per_file) + 1
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        chunk.to_excel(writer, index=False)
                    zf.writestr(f"bloque_{chunk_num}.xlsx", output.getvalue())
            
            st.success("✅ ¡Archivos generados!")
            st.download_button("📥 Descargar ZIP de Filas", zip_buffer.getvalue(), "excel_filas.zip")

    # --- LÓGICA 2: DIVISIÓN POR COLUMNAS (MANTENIENDO SKU) ---
    else:
        # Según tu archivo, la columna 0 es el SKU
        col_sku = df.columns[0] 
        columnas_datos = df.columns[1:] # Las 13 columnas de contenido/idiomas
        
        st.write(f"Columna maestra: **{col_sku}**")
        st.write(f"Se crearán **{len(columnas_datos)}** archivos individuales.")

        if st.button("Generar un archivo por idioma"):
            zip_buffer = io.BytesIO()
            
            with st.spinner('Procesando columnas...'):
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for col_nombre in columnas_datos:
                        # Seleccionamos SKU + Columna actual (ej. Contenido EN)
                        df_temp = df[[col_sku, col_nombre]].copy()
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_temp.to_excel(writer, index=False)
                        
                        # Limpiamos el nombre para que el archivo sea válido
                        nombre_seguro = "".join([c for c in str(col_nombre) if c.isalnum() or c in (' ', '_')]).strip()
                        zf.writestr(f"{nombre_seguro}.xlsx", output.getvalue())
            
            st.success(f"✅ Procesadas {len(columnas_datos)} columnas correctamente.")
            st.download_button(
                label="📥 Descargar ZIP de Columnas",
                data=zip_buffer.getvalue(),
                file_name="excel_columnas_idiomas.zip",
                mime="application/zip"
            )