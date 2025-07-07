import streamlit as st
import duckdb
import tempfile
import os
import chardet
import io

st.set_page_config(layout="wide")
st.title("🚀 High-Performance SQL on Large Files with DuckDB")

# ---------------------- SIDEBAR CONTROLS ----------------------

# 📦 Delimiter for input
st.sidebar.markdown("### 🔧 Input File Delimiter")
delimiter_option = st.sidebar.selectbox(
    "Select Delimiter for Input File",
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

# ---------------------- FILE HANDLING ----------------------

# 🔍 Detect encoding
def detect_encoding(uploaded_file):
    raw_data = uploaded_file.read(100000)
    result = chardet.detect(raw_data)
    uploaded_file.seek(0)
    encoding = result.get("encoding")
    if not encoding or encoding.lower() not in ["utf-8", "latin1", "utf-16"]:
        encoding = "utf-8"
    return encoding

# 💾 Save uploaded file to disk
def save_to_disk(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name

# ---------------------- FILE UPLOAD ----------------------

st.markdown("### 📁 Upload One or Two Files")
file1 = st.file_uploader("Upload File 1", type=["csv", "dat", "parquet"], key="file1")
file2 = st.file_uploader("Upload File 2 (Optional)", type=["csv", "dat", "parquet"], key="file2")

table1_path = table2_path = None
table1_encoding = table2_encoding = None
con = duckdb.connect()

if file1:
    table1_path = save_to_disk(file1)
    table1_encoding = detect_encoding(file1)
    st.sidebar.write(f"📄 `{file1.name}` encoding: `{table1_encoding}`")
    st.success("✅ File 1 loaded as `table1`")

if file2:
    table2_path = save_to_disk(file2)
    table2_encoding = detect_encoding(file2)
    st.sidebar.write(f"📄 `{file2.name}` encoding: `{table2_encoding}`")
    st.success("✅ File 2 loaded as `table2`")

# ---------------------- SQL INTERFACE ----------------------

if table1_path or table2_path:
    st.subheader("📝 SQL Query Interface")
    st.markdown("""
    Use `table1` and `table2` in your SQL.  
    Examples:
    - `SELECT * FROM table1 LIMIT 100`
    - `SELECT DISTINCT department FROM table1`
    - `SELECT * FROM table1 JOIN table2 ON table1.id = table2.id`
    """)

    # SQL for loading files
    query_prefix = ""
    null_clause = ", nullstr=['NULL', '']"
    
    if table1_path:
        if table1_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table1 AS SELECT * FROM parquet_scan('{table1_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            query_prefix += f"""
            CREATE OR REPLACE TABLE table1 AS 
            SELECT * FROM read_csv_auto('{table1_path}', encoding='{table1_encoding}'{delim_clause}{null_clause});
            """

    if table2_path:
        if table2_path.endswith(".parquet"):
            query_prefix += f"CREATE OR REPLACE TABLE table2 AS SELECT * FROM parquet_scan('{table2_path}');\n"
        else:
            delim_clause = f", delim='{delimiter}'" if delimiter else ""
            query_prefix += f"""
            CREATE OR REPLACE TABLE table2 AS 
            SELECT * FROM read_csv_auto('{table2_path}', encoding='{table2_encoding}'{delim_clause}{null_clause});
            """

    user_query = st.text_area("Write your SQL query below", value="SELECT * FROM table1 LIMIT 100", height=120)

    if st.button("Run SQL Query"):
        try:
            full_query = query_prefix + "\n" + user_query
            result = con.execute(full_query).df()
            st.success("✅ Query executed successfully!")
            st.dataframe(result.head(1000), use_container_width=True)

            # ---------------------- DOWNLOAD BLOCK ----------------------
            st.markdown("### 📥 Download SQL Result")

            sep_option = st.selectbox("Select download delimiter", ["Comma (,)", "Tab (\\t)", "Pipe (|)", "Semicolon (;)"])
            sep_map = {
                "Comma (,)": ",",
                "Tab (\\t)": "\t",
                "Pipe (|)": "|",
                "Semicolon (;)": ";"
            }
            download_sep = sep_map.get(sep_option, ",")

            csv_buffer = io.StringIO()
            result.to_csv(csv_buffer, sep=download_sep, index=False)
            csv_bytes = csv_buffer.getvalue().encode("utf-8")

            st.download_button(
                label="⬇️ Download Result as CSV",
                data=csv_bytes,
                file_name="query_result.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

else:
    st.warning("👆 Upload at least one file to begin.")
