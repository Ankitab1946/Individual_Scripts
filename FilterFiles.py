import streamlit as st
import duckdb
import os
import chardet

st.set_page_config(layout="wide")
st.title("🚀 High-Performance SQL on Large Files with DuckDB")

# 📦 Delimiter input
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
file1 = st.file_uploader("Upload File 1", type=["csv", "dat", "parquet"], key="file1")
file2 = st.file_uploader("Upload File 2 (Optional)", type=["csv", "dat", "parquet"], key="file2")

con = duckdb.connect()

# 🧠 Save uploaded file to disk (temp)
def save_to_disk(uploaded_file):
    file_path = os.path.join("/tmp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

# 🧠 Detect encoding
def detect_encoding(uploaded_file):
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    uploaded_file.seek(0)
    return result['encoding']

table1_path = table2_path = None

if file1:
    table1_path = save_to_disk(file1)
    st.success(f"✅ File 1 loaded as `table1`")
    st.text(f"Path: {table1_path}")

if file2:
    table2_path = save_to_disk(file2)
    st.success(f"✅ File 2 loaded as `table2`")
    st.text(f"Path: {table2_path}")

# 👇 SQL Section
if table1_path or table2_path:
    st.subheader("📝 SQL Query Interface")
    st.markdown("""
    Use `table1` and `table2` in SQL. Example:
    ```sql
    SELECT * FROM table1 LIMIT 100
    ```
    """)

    # Auto SQL setup using DuckDB's read_csv/read_parquet
    query_prefix = ""
    if table1_path:
        if table1_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table1 AS SELECT * FROM parquet_scan('{table1_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            encoding = detect_encoding(file1)
            query_prefix += f"CREATE OR REPLACE TABLE table1 AS SELECT * FROM read_csv_auto('{table1_path}', encoding='{encoding}'{delim_clause});\n"

    if table2_path:
        if table2_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table2 AS SELECT * FROM parquet_scan('{table2_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            encoding = detect_encoding(file2)
            query_prefix += f"CREATE OR REPLACE TABLE table2 AS SELECT * FROM read_csv_auto('{table2_path}', encoding='{encoding}'{delim_clause});\n"

    user_query = st.text_area("Enter SQL query below", value="SELECT * FROM table1 LIMIT 100", height=120)

    if st.button("Run SQL Query"):
        try:
            full_query = query_prefix + "\n" + user_query
            result = con.execute(full_query).df()
            st.success("✅ Query executed successfully!")
            st.dataframe(result.head(1000), use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")
else:
    st.warning("👆 Upload at least one file to begin.")
