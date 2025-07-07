import streamlit as st
import duckdb
import tempfile
import os
import chardet

st.set_page_config(layout="wide")
st.title("🚀 High-Performance SQL on Large Files with DuckDB")

# 📦 Delimiter options
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

# 🧠 Detect encoding with fallback
def detect_encoding(uploaded_file):
    raw_data = uploaded_file.read(100000)  # Read first 100 KB
    result = chardet.detect(raw_data)
    uploaded_file.seek(0)  # Reset pointer
    encoding = result.get("encoding")
    if not encoding or encoding.lower() not in ["utf-8", "latin1", "utf-16"]:
        encoding = "utf-8"  # Fallback
    return encoding

# 🧠 Save file to disk (temp, cross-platform)
def save_to_disk(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name

# 📁 File upload
st.markdown("### 📁 Upload One or Two Files")
file1 = st.file_uploader("Upload File 1", type=["csv", "dat", "parquet"], key="file1")
file2 = st.file_uploader("Upload File 2 (Optional)", type=["csv", "dat", "parquet"], key="file2")

table1_path = table2_path = None
table1_encoding = table2_encoding = None
con = duckdb.connect()

# Save files to temp dir
if file1:
    table1_path = save_to_disk(file1)
    table1_encoding = detect_encoding(file1)
    st.sidebar.write(f"📄 `{file1.name}` encoding: `{table1_encoding}`")
    st.success(f"✅ File 1 loaded as `table1`")

if file2:
    table2_path = save_to_disk(file2)
    table2_encoding = detect_encoding(file2)
    st.sidebar.write(f"📄 `{file2.name}` encoding: `{table2_encoding}`")
    st.success(f"✅ File 2 loaded as `table2`")

# SQL Section
if table1_path or table2_path:
    st.subheader("📝 SQL Query Interface")
    st.markdown("""
    Use `table1` and `table2` in your SQL. Example:
    ```sql
    SELECT * FROM table1 LIMIT 100
    SELECT * FROM table1 JOIN table2 ON table1.id = table2.id
    ```
    """)

    # Generate DuckDB SQL to load files
    query_prefix = ""

    if table1_path:
        if table1_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table1 AS SELECT * FROM parquet_scan('{table1_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            query_prefix += f"""
            CREATE OR REPLACE TABLE table1 AS 
            SELECT * FROM read_csv_auto('{table1_path}', encoding='{table1_encoding}'{delim_clause});
            """

    if table2_path:
        if table2_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table2 AS SELECT * FROM parquet_scan('{table2_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            query_prefix += f"""
            CREATE OR REPLACE TABLE table2 AS 
            SELECT * FROM read_csv_auto('{table2_path}', encoding='{table2_encoding}'{delim_clause});
            """

    default_query = "SELECT * FROM table1 LIMIT 100"
    user_query = st.text_area("Write your SQL query below", value=default_query, height=120)

    if st.button("Run SQL Query"):
        try:
            full_query = query_prefix + "\n" + user_query
            result = con.execute(full_query).df()
            st.success("✅ Query executed successfully!")
            st.dataframe(result.head(1000), use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")
else:
    st.warning("👆 Please upload at least one file to begin.")
