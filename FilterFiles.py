import streamlit as st
import pandas as pd
import duckdb
import os

st.set_page_config(layout="wide")
st.title("🧠 SQL Query on Uploaded File(s) with Join Support")

# Function to read uploaded file
def read_file(uploaded_file):
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".csv":
            df = pd.read_csv(uploaded_file)
        elif ext == ".dat":
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        elif ext == ".json":
            df = pd.read_json(uploaded_file)
        elif ext == ".parquet":
            df = pd.read_parquet(uploaded_file)
        elif ext == ".icr":
            df = pd.read_csv(uploaded_file)
        else:
            st.error(f"Unsupported file type: {ext}")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

    return df

# File Uploaders
st.markdown("### 📁 Upload One or Two Files to Query")
file1 = st.file_uploader("Upload File 1 (e.g., CSV/DAT)", type=["csv", "dat", "json", "parquet", "icr"], key="file1")
file2 = st.file_uploader("Upload File 2 (Optional)", type=["csv", "dat", "json", "parquet", "icr"], key="file2")

df1 = df2 = None
if file1:
    df1 = read_file(file1)
    if df1 is not None:
        st.success("✅ File 1 loaded as `table1`")
        st.subheader("📄 Preview of File 1 (table1)")
        st.dataframe(df1, use_container_width=True)

if file2:
    df2 = read_file(file2)
    if df2 is not None:
        st.success("✅ File 2 loaded as `table2`")
        st.subheader("📄 Preview of File 2 (table2)")
        st.dataframe(df2, use_container_width=True)

# Proceed only if at least one file is loaded
if df1 is not None or df2 is not None:
    st.subheader("📝 SQL Query Interface")

    st.markdown("""
    - Use `table1` to refer to the first file
    - Use `table2` to refer to the second file (if uploaded)
    - Examples:
        - `SELECT * FROM table1 LIMIT 5`
        - `SELECT * FROM table1 JOIN table2 ON table1.id = table2.id`
    """)

    default_query = "SELECT * FROM table1 LIMIT 10" if df1 is not None else "SELECT * FROM table2 LIMIT 10"
    query = st.text_area("Write your SQL query below:", value=default_query, height=100)

    if st.button("Run SQL Query"):
        try:
            con = duckdb.connect()
            if df1 is not None:
                con.register("table1", df1)
            if df2 is not None:
                con.register("table2", df2)

            result = con.execute(query).df()
            st.success("✅ Query executed successfully!")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")
else:
    st.warning("👆 Please upload at least one file to begin.")
