import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Divisor de Excel Pro", page_icon="📊")

st.title("📊 Procesador de Archivos Excel")

# Selector de funcionalidad en el cuerpo principal
opcion = st.radio(
    "¿Qué deseas hacer?",
    ("Dividir por número de filas", "Dividir por categorías", "Dividir por columnas (Manteniendo SKU)"),
    horizontal=True
)

st.markdown("---")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Lectura del archivo
    df = pd.read_excel(uploaded_file)
    total_rows = len(df)
    columnas_disponibles = df.columns.tolist()
    
    st.info(f"📋 Archivo cargado: {total_rows} filas detectadas.")

    # --- LÓGICA 1: DIVISIÓN POR FILAS ---
    if opcion == "Dividir por número de filas":
        rows_per_file = st.number_input("Filas por archivo:", min_value=1, value=500)
        
        if st.button("Generar archivos por filas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i in range(0, total_rows, rows_per_file):
                    chunk = df.iloc[i : i + rows_per_file]
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        chunk.to_excel(writer, index=False)
                    zf.writestr(f"parte_{(i//rows_per_file)+1}.xlsx", output.getvalue())
            
            st.success("✅ Fragmentos listos.")
            st.download_button("📥 Descargar ZIP", zip_buffer.getvalue(), "filas.zip")

    # --- LÓGICA 2: DIVISIÓN POR CATEGORÍAS (Columna específica) ---
    elif opcion == "Dividir por categorías":
        nombre_esperado = "Categories (x,y,z...)"
        
        # Verificamos si la columna existe, si no, dejamos que el usuario la elija
        if nombre_esperado in columnas_disponibles:
            col_cat = nombre_esperado
        else:
            st.warning(f"No se encontró la columna exacta '{nombre_esperado}'")
            col_cat = st.selectbox("Selecciona la columna que contiene las categorías:", columnas_disponibles)

        categorias = df[col_cat].unique()
        st.write(f"Se han detectado **{len(categorias)}** categorías en la columna **'{col_cat}'**.")
        
        if st.button("Generar un archivo por categoría"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for cat in categorias:
                    # Filtrar datos
                    if pd.isna(cat):
                        df_cat = df[df[col_cat].isna()]
                        nombre_archivo = "Sin_Categoria"
                    else:
                        df_cat = df[df[col_cat] == cat]
                        # Limpiar nombre para el nombre del archivo
                        nombre_archivo = "".join([c for c in str(cat) if c.isalnum() or c in (' ', '_')]).strip()
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_cat.to_excel(writer, index=False)
                    zf.writestr(f"{nombre_archivo}.xlsx", output.getvalue())
            
            st.success(f"✅ Se han generado {len(categorias)} archivos.")
            st.download_button("📥 Descargar ZIP de Categorías", zip_buffer.getvalue(), "categorias.zip")

    # --- LÓGICA 3: DIVISIÓN POR COLUMNAS (MANTENIENDO SKU) ---
    else:
        col_sku = columnas_disponibles[0]
        columnas_datos = columnas_disponibles[1:]
        
        st.write(f"Columna fija: **{col_sku}** | Columnas a separar: **{len(columnas_datos)}**")

        if st.button("Generar archivos por columnas"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for col_nombre in columnas_datos:
                    df_temp = df[[col_sku, col_nombre]].copy()
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_temp.to_excel(writer, index=False)
                    
                    nombre_seguro = "".join([c for c in str(col_nombre) if c.isalnum() or c in (' ', '_')]).strip()
                    zf.writestr(f"{nombre_seguro}.xlsx", output.getvalue())
            
            st.success("✅ Procesado correctamente.")
            st.download_button("📥 Descargar ZIP de Columnas", zip_buffer.getvalue(), "columnas_idiomas.zip")