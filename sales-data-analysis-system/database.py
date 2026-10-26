import hashlib
import mysql.connector
import pandas as pd
from config import Config

def get_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )

def init_db():
    # Create the database first (CREATE DATABASE is handled without selecting it).
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}`")
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(150) NOT NULL,
            category VARCHAR(100) NOT NULL,
            UNIQUE KEY uq_product_name_category (product_name, category)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            sale_date DATE NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(12,2) NOT NULL,
            region VARCHAR(100) NOT NULL,
            import_hash CHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_sales_import_hash (import_hash),
            CONSTRAINT fk_sales_product FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def row_hash(row):
    # Duplicate policy: exact same normalized product/category/date/quantity/price/region
    # is imported only once, even if it appears in a later CSV file.
    raw = "|".join([
        str(row["product_name"]).strip().casefold(),
        str(row["category"]).strip().casefold(),
        pd.Timestamp(row["sale_date"]).strftime("%Y-%m-%d"),
        str(int(row["quantity"])),
        f'{float(row["unit_price"]):.2f}',
        str(row["region"]).strip().casefold(),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def insert_sales(df):
    if df.empty:
        return 0, 0
    conn = get_connection()
    cursor = conn.cursor()
    inserted = duplicates = 0
    try:
        for _, row in df.iterrows():
            product_name = str(row["product_name"]).strip()
            category = str(row["category"]).strip()
            cursor.execute(
                "INSERT INTO products (product_name, category) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE product_id=LAST_INSERT_ID(product_id)",
                (product_name, category),
            )
            product_id = cursor.lastrowid
            digest = row_hash(row)
            cursor.execute("""
                INSERT IGNORE INTO sales
                    (product_id, sale_date, quantity, unit_price, region, import_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                product_id,
                pd.Timestamp(row["sale_date"]).date(),
                int(row["quantity"]),
                float(row["unit_price"]),
                str(row["region"]).strip(),
                digest,
            ))
            if cursor.rowcount == 1:
                inserted += 1
            else:
                duplicates += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
    return inserted, duplicates

def fetch_sales():
    conn = get_connection()
    try:
        query = """
            SELECT s.sale_id, p.product_name, p.category, s.sale_date,
                   s.quantity, CAST(s.unit_price AS DECIMAL(12,2)) AS unit_price,
                   s.region, (s.quantity * s.unit_price) AS revenue
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            ORDER BY s.sale_date, s.sale_id
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            df["sale_date"] = pd.to_datetime(df["sale_date"])
            df["revenue"] = pd.to_numeric(df["revenue"])
        return df
    finally:
        conn.close()
