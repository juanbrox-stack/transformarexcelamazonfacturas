import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Divisor de Excel Pro", page_icon="📊")

st.title("📊 Procesador de Archivos Excel")

opcion = st.sidebar.radio(
    "Selecciona Modo:",
    ("Dividir por número de filas", "Dividir por columnas (Manteniendo SKU)")
)

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Leemos el archivo una sola vez
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    total_cols = len(df.columns)
    
    st.info(f"Archivo: {total_rows} filas | {total_cols} columnas detectadas.")

    # --- MODO FILAS ---
    if opcion == "Dividir por número de filas":
        rows_per_file = st.number_input("Filas por archivo:", min_value=1, value=500)
        
        if st.button("Preparar descarga por filas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(0, total_rows, rows_per_file):
                    chunk = df.iloc[i : i + rows_per_file]
                    chunk_num = (i // rows_per_file) + 1
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        chunk.to_excel(writer, index=False)
                    zf.writestr(f"parte_{chunk_num}.xlsx", output.getvalue())
            
            st.success("✅ ZIP generado con éxito.")
            st.download_button("📥 Descargar ZIP de Filas", zip_buffer.getvalue(), "filas.zip")

    # --- MODO COLUMNAS (CORREGIDO) ---
    else:
        col_fija = df.columns[0] # "SKU"
        columnas_restantes = df.columns[1:] # Los 13 idiomas
        
        st.write(f"Columna fija: **{col_fija}**")
        st.write(f"Columnas a procesar: **{len(columnas_restantes)}**")

        if st.button("Preparar descarga por columnas"):
            zip_buffer = io.BytesIO()
            
            # Usamos un spinner para que el usuario vea que está trabajando
            with st.spinner('Generando todos los archivos...'):
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for col_nombre in columnas_restantes:
                        # Creamos el dataframe con SKU + Columna de idioma actual
                        df_temp = df[[col_fija, col_nombre]].copy()
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_temp.to_excel(writer, index=False)
                        
                        # Limpieza del nombre del archivo
                        nombre_limpio = "".join([c for c in str(col_nombre) if c.isalnum() or c in (' ', '_')]).strip()
                        zf.writestr(f"{nombre_limpio}.xlsx", output.getvalue())
            
            st.success(f"✅ Se han procesado las {len(columnas_restantes)} columnas.")
            st.download_button(
                label="📥 Descargar ZIP con todos los idiomas",
                data=zip_buffer.getvalue(),
                file_name="contenido_por_idiomas.zip",
                mime="application/zip"
            )