import os
from pathlib import Path

import psycopg2


def load_env_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = [part.strip() for part in line.split("=", 1)]
            if key and value and key not in os.environ:
                os.environ[key] = value


def get_connection_string():
    load_env_file()
    conn_string = os.getenv("CONNECTION_STRING")
    if not conn_string:
        raise RuntimeError("CONNECTION_STRING is not set in the environment or .env file.")
    return conn_string


def ensure_raw_schema(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")


def ensure_tables_exist(cursor):
    ddl_path = Path(__file__).resolve().parent / "ddl" / "walmart_schema.sql"
    if not ddl_path.exists():
        return

    ddl_sql = ddl_path.read_text(encoding="utf-8")
    replacements = {
        "CREATE TABLE customers (": "CREATE TABLE raw.customers (",
        "CREATE TABLE stores (": "CREATE TABLE raw.stores (",
        "CREATE TABLE products (": "CREATE TABLE raw.products (",
        "CREATE TABLE employees (": "CREATE TABLE raw.employees (",
        "CREATE TABLE orders (": "CREATE TABLE raw.orders (",
        "CREATE TABLE order_items (": "CREATE TABLE raw.order_items (",
    }

    for old, new in replacements.items():
        ddl_sql = ddl_sql.replace(old, new)

    cursor.execute(ddl_sql)


# CSV files mapping to tables
csv_files = {
    "customers.csv": "raw.customers",
    "stores.csv": "raw.stores",
    "products.csv": "raw.products",
    "employees.csv": "raw.employees",
    "orders.csv": "raw.orders",
    "order_items.csv": "raw.order_items",
}

base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "data"

conn = None
try:
    conn_string = get_connection_string()
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    ensure_raw_schema(cursor)
    ensure_tables_exist(cursor)

    for csv_file, table_name in csv_files.items():
        csv_path = data_dir / csv_file

        if csv_path.exists():
            print(f"Loading {csv_file} into {table_name}...")

            with csv_path.open("r", encoding="utf-8", newline="") as f:
                cursor.copy_expert(
                    f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                    f,
                )

            conn.commit()
            print(f"✓ Successfully loaded {csv_file}")
        else:
            print(f"✗ File not found: {csv_path}")

    cursor.close()
    conn.close()
    print("\n✓ All data loaded successfullyss.!")

except Exception as e:
    print(f"Error: {e}")
    if conn is not None:
        conn.rollback()
        conn.close()
