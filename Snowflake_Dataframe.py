import snowflake.connector
import pandas as pd
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# ---- CONFIGURATION ----
SNOWFLAKE_USER = 'your_username'
SNOWFLAKE_ACCOUNT = 'your_account_identifier'  # e.g., 'abcde-xy12345'
SNOWFLAKE_WAREHOUSE = 'your_warehouse'
SNOWFLAKE_DATABASE = 'your_database'
SNOWFLAKE_SCHEMA = 'your_schema'
PRIVATE_KEY_PATH = 'rsa_key.p8'
PRIVATE_KEY_PASSPHRASE = None  # Set to None if key is not encrypted

# ---- LOAD PRIVATE KEY ----
def get_private_key():
    with open(PRIVATE_KEY_PATH, 'rb') as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=PRIVATE_KEY_PASSPHRASE,
            backend=default_backend()
        )
    return p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

# ---- CONNECT AND FETCH DATA ----
try:
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        account=SNOWFLAKE_ACCOUNT,
        private_key=get_private_key(),
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    print("✅ Connected to Snowflake")

    # ---- QUERY DATA ----
    query = "SELECT * FROM your_table_name LIMIT 100"  # Replace with your actual query

    # Fetch into DataFrame
    df = pd.read_sql(query, conn)

    # Preview
    print("📄 Sample Data:")
    print(df.head())

    # Example: Read from DataFrame
    print("\n🔍 First row, first column:", df.iloc[0, 0])
    print("🔍 Column names:", df.columns.tolist())

    conn.close()

except Exception as e:
    print("❌ Connection or fetch failed.")
    print("Error:", str(e))
