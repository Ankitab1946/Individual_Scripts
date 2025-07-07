import streamlit as st
import pandas as pd
import duckdb
import os
import chardet

st.set_page_config(layout="wide")
st.title("🧠 SQL Query on Uploaded File(s) with Join Support & Large File Handling")

# 🔍 Detect file encoding
def detect_encoding(uploaded_file):
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    uploaded_file.seek(0)
    return result['encoding']

# 🧠 Read uploaded file with delimiter and encoding
def read_file(uploaded_file, sep=None):
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    try:
        encoding = detect_encoding(uploaded_file)
        st.sidebar.write(f"📄 `{filename}` detected encoding: `{encoding}`")

        if ext in [".csv", ".dat", ".icr"]:
            df = pd.read_csv(uploaded_file, sep=sep, engine="python", encoding=encoding, on_bad_lines="warn")
        elif ext == ".json":
            df = pd.read_json(uploaded_file)
        elif ext == ".parquet":
            df = pd.read_parquet(uploaded_file)
        else:
            st.error(f"Unsupported file type: {ext}")
            return None
    except Exception as e:
        st.error(f"❌ Error reading file `{filename}`: {e}")
        return None

    return df

# 📦 UI: Delimiter selection
st.sidebar.markdown("### 🔧 Delimiter Options")
delimiter_option = st.sidebar.selectbox(
    "Select Delimiter",
    ["Auto-detect", "Comma (,)", "Tab (\\t)", "Pipe (|)", "Semicolon (;)", "Space", "Custom"]
)
delimiter_map = {
    "Auto-detect": None,
    "Comma (,)": ",",
    "Tab (\\t)": "\t",
    "Pipe (|)": "|",
    "Semicolon (;)": ";",
    "Space": " "
}
delimiter = delimiter_map.get(delimiter_option, None)
if delimiter_option == "Custom":
    custom_delim = st.sidebar.text_input("Enter custom delimiter", value="")
    delimiter = custom_delim if custom_delim else None

# 📁 Upload files
st.markdown("### 📁 Upload One or Two Files")
file1 = st.file_uploader("Upload File 1", type=["csv", "dat", "json", "parquet", "icr"], key="file1")
file2 = st.file_uploader("Upload File 2 (Optional)", type=["csv", "dat", "json", "parquet", "icr"], key="file2")

df1 = df2 = None
if file1:
    df1 = read_file(file1, sep=delimiter)
    if df1 is not None:
        st.success("✅ File 1 loaded as `table1`")
        st.subheader("📄 Preview of File 1 (first 100 rows)")
        st.dataframe(df1.head(100), use_container_width=True)

if file2:
    df2 = read_file(file2, sep=delimiter)
    if df2 is not None:
        st.success("✅ File 2 loaded as `table2`")
        st.subheader("📄 Preview of File 2 (first 100 rows)")
        st.dataframe(df2.head(100), use_container_width=True)

# 🔍 SQL Section
if df1 is not None or df2 is not None:
    st.subheader("📝 SQL Query Interface")
    st.markdown("""
    - Use `table1` and `table2` in your SQL.
    - Examples:
        - `SELECT * FROM table1 LIMIT 5`
        - `SELECT * FROM table1 JOIN table2 ON table1.id = table2.id`
        - `SELECT department, COUNT(*) FROM table1 GROUP BY department`
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
            st.dataframe(result.head(1000), use_container_width=True)  # Limit large output
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")
else:
    st.warning("👆 Upload at least one file to begin.")
