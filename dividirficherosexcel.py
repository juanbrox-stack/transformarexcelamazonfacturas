import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="Excel Master Tool", page_icon="📊", layout="wide")

st.title("📊 Procesador Avanzado de Excel")

# Selector de funcionalidad con la nueva opción de Unificar
opcion = st.radio(
    "¿Qué deseas hacer?",
    ("Dividir por número de filas", "Dividir por categorías", "Dividir por columnas (SKU + 1)", "Unificar varios Excel en uno"),
    horizontal=True
)

st.markdown("---")

# --- LÓGICA PARA UNIFICAR (LA INVERSA) ---
if opcion == "Unificar varios Excel en uno":
    st.subheader("🔗 Unificar archivos (Pegar uno debajo de otro)")
    st.info("Sube todos los archivos que quieras juntar. Se unirán respetando las columnas que tengan en común.")
    
    uploaded_files = st.file_uploader("Sube tus archivos Excel", type=["xlsx"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"📂 Archivos seleccionados: {len(uploaded_files)}")
        
        if st.button("Combinar todos los archivos"):
            lista_df = []
            with st.spinner('Leyendo y unificando...'):
                for f in uploaded_files:
                    temp_df = pd.read_excel(f)
                    lista_df.append(temp_df)
                
                # Concatenamos todos los dataframes de la lista
                df_unificado = pd.concat(lista_df, ignore_index=True)
            
            st.success(f"✅ ¡Unificación completada! Total de filas resultantes: {len(df_unificado)}")
            
            # Preparar la descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_unificado.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Descargar Excel Unificado",
                data=output.getvalue(),
                file_name="excel_unificado_total.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# --- LÓGICA PARA LAS DIVISIONES (IGUAL QUE ANTES) ---
else:
    uploaded_file = st.file_uploader("Sube tu archivo Excel principal", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        columnas_disponibles = df.columns.tolist()
        st.info(f"📋 Archivo cargado: {len(df)} filas.")

        # 1. División por filas
        if opcion == "Dividir por número de filas":
            rows_per_file = st.number_input("Filas por archivo:", min_value=1, value=500)
            if st.button("Generar archivos por filas"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for i in range(0, len(df), rows_per_file):
                        chunk = df.iloc[i : i + rows_per_file]
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            chunk.to_excel(writer, index=False)
                        zf.writestr(f"bloque_{(i//rows_per_file)+1}.xlsx", output.getvalue())
                st.download_button("📥 Descargar ZIP", zip_buffer.getvalue(), "filas.zip")

        # 2. División por categorías
        elif opcion == "Dividir por categorías":
            nombre_esp = "Categories (x,y,z...)"
            col_cat = nombre_esp if nombre_esp in columnas_disponibles else st.selectbox("Selecciona columna:", columnas_disponibles)
            
            if st.button("Generar archivos por categoría"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for cat in df[col_cat].unique():
                        df_cat = df[df[col_cat].isna()] if pd.isna(cat) else df[df[col_cat] == cat]
                        nombre_arc = "Sin_Cat" if pd.isna(cat) else "".join([c for c in str(cat) if c.isalnum() or c in (' ', '_')]).strip()
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_cat.to_excel(writer, index=False)
                        zf.writestr(f"{nombre_arc}.xlsx", output.getvalue())
                st.download_button("📥 Descargar ZIP Categorías", zip_buffer.getvalue(), "categorias.zip")

        # 3. División por columnas
        elif opcion == "Dividir por columnas (SKU + 1)":
            col_sku = columnas_disponibles[0]
            if st.button("Generar archivos por columnas"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for col_nombre in columnas_disponibles[1:]:
                        df_temp = df[[col_sku, col_nombre]].copy()
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_temp.to_excel(writer, index=False)
                        nombre_seguro = "".join([c for c in str(col_nombre) if c.isalnum() or c in (' ', '_')]).strip()
                        zf.writestr(f"{nombre_seguro}.xlsx", output.getvalue())
                st.download_button("📥 Descargar ZIP Columnas", zip_buffer.getvalue(), "columnas.zip")