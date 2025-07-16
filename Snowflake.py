import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# ---- CONFIGURATION ----
SNOWFLAKE_USER = 'your_username'
SNOWFLAKE_ACCOUNT = 'your_account_identifier'  # e.g., 'abcde-xy12345'
SNOWFLAKE_WAREHOUSE = 'your_warehouse'
SNOWFLAKE_DATABASE = 'your_database'
SNOWFLAKE_SCHEMA = 'your_schema'
PRIVATE_KEY_PATH = 'rsa_key.p8'
PRIVATE_KEY_PASSPHRASE = b'your_private_key_password'  # Use b"" if no password

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

try:
    # Connect to Snowflake using private key
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        account=SNOWFLAKE_ACCOUNT,
        private_key=get_private_key(),
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    # Run a simple query to test
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_USER(), CURRENT_VERSION()")
    for row in cursor:
        print("✅ Connected to Snowflake as:", row[0])
        print("🔢 Snowflake version:", row[1])
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed.")
    print("Error:", str(e))
