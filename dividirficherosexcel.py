import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Divisor de Excel Pro", page_icon="📊")

st.title("📊 Procesador de Archivos Excel")
st.write("Sube un archivo y elige cómo quieres fragmentarlo.")

# 1. Selector de funcionalidad principal
opcion = st.radio(
    "¿Qué deseas hacer?",
    ("Dividir por número de filas", "Dividir por columnas (Manteniendo SKU)")
)

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Leemos el archivo
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    total_cols = len(df.columns)
    
    st.info(f"Archivo cargado: {total_rows} filas y {total_cols} columnas.")

    # --- OPCIÓN 1: DIVIDIR POR FILAS ---
    if opcion == "Dividir por número de filas":
        st.subheader("Configuración de Filas")
        rows_per_file = st.number_input("Filas de datos por cada archivo:", min_value=1, max_value=total_rows, value=500)
        
        if st.button("Generar archivos por filas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(0, total_rows, rows_per_file):
                    # Cortamos el grupo de filas
                    chunk = df.iloc[i : i + rows_per_file]
                    chunk_num = (i // rows_per_file) + 1
                    
                    # Generamos el Excel (Pandas mantiene la fila 1 de encabezados por defecto)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        chunk.to_excel(writer, index=False)
                    
                    zf.writestr(f"parte_filas_{chunk_num}.xlsx", output.getvalue())
            
            st.success("✅ División por filas completada.")
            st.download_button("📥 Descargar ZIP", zip_buffer.getvalue(), "excel_por_filas.zip")

    # --- OPCIÓN 2: DIVIDIR POR COLUMNAS (MANTENIENDO COLUMNA 1) ---
    else:
        st.subheader("Configuración de Columnas")
        col_fija = df.columns[0] # La primera columna (SKU)
        columnas_restantes = df.columns[1:] # Todas las demás
        
        st.warning(f"Se crearán {len(columnas_restantes)} archivos. Todos incluirán la columna: **{col_fija}**")

        if st.button("Generar archivos por columnas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for col_nombre in columnas_restantes:
                    # Creamos un nuevo DataFrame con la columna 1 + la columna actual
                    df_resultado = df[[col_fija, col_nombre]]
                    
                    # Generamos el Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_resultado.to_excel(writer, index=False)
                    
                    # Limpiamos el nombre de la columna para el nombre del archivo
                    nombre_archivo = f"columna_{col_nombre}".replace(" ", "_")[:30]
                    zf.writestr(f"{nombre_archivo}.xlsx", output.getvalue())
            
            st.success("✅ División por columnas completada.")
            st.download_button("📥 Descargar ZIP", zip_buffer.getvalue(), "excel_por_columnas.zip")