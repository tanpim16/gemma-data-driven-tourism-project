"""
รันครั้งเดียว: สร้าง database/table และ upload master_tourism_analysis.csv → Snowflake
"""
import pandas as pd
import snowflake.connector
import math

ACCOUNT   = "JHGQGLO-KF73185"
USER      = "pimkanit"
PASSWORD  = "Tanpim@160544!!"
WAREHOUSE = "COMPUTE_WH"
DATABASE  = "TOURISM_DB"
SCHEMA    = "PUBLIC"
TABLE     = "TOURISM_STATS"

def main():
    print("📡 Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=ACCOUNT, user=USER, password=PASSWORD, warehouse=WAREHOUSE
    )
    cur = conn.cursor()

    print("🏗️  Creating database / schema / table...")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cur.execute(f"USE DATABASE {DATABASE}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    cur.execute(f"USE SCHEMA {SCHEMA}")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            YEAR            INTEGER,
            MONTH           VARCHAR(10),
            PROVINCETHAI    VARCHAR(100),
            OCCUPANCY_RATE  FLOAT,
            TOTAL_GUESTS    FLOAT,
            TOTAL_VISITORS  FLOAT,
            THAI_VISITORS   FLOAT,
            FOREIGN_VISITORS FLOAT,
            TOTAL_REVENUE   FLOAT,
            THAI_REVENUE    FLOAT,
            FOREIGN_REVENUE FLOAT,
            NO              FLOAT,
            PROVINCEEN      VARCHAR(100),
            REGION_TH       VARCHAR(100),
            REGION_EN       VARCHAR(100),
            CITY_TYPE_TH    VARCHAR(100),
            CITY_TYPE_EN    VARCHAR(100),
            PRICE_INDEX     FLOAT,
            REAL_REVENUE    FLOAT
        )
    """)

    print("📂 Loading CSV...")
    df = pd.read_csv("data/master_tourism_analysis.csv")
    df.columns = [c.upper() for c in df.columns]

    cur.execute(f"TRUNCATE TABLE IF EXISTS {TABLE}")

    print(f"⬆️  Uploading {len(df)} rows in batches...")
    batch = 500
    for i in range(0, len(df), batch):
        chunk = df.iloc[i:i+batch]
        rows = []
        for _, row in chunk.iterrows():
            vals = []
            for v in row:
                if pd.isna(v):
                    vals.append("NULL")
                elif isinstance(v, str):
                    vals.append(f"'{v.replace(chr(39), chr(39)*2)}'")
                else:
                    vals.append("NULL" if (isinstance(v, float) and math.isnan(v)) else str(v))
            rows.append(f"({','.join(vals)})")
        cur.execute(f"INSERT INTO {TABLE} VALUES {','.join(rows)}")
        print(f"  ✅ {min(i+batch, len(df))}/{len(df)} rows")

    cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
    count = cur.fetchone()[0]
    print(f"\n🎉 Done! {count} rows in Snowflake {DATABASE}.{SCHEMA}.{TABLE}")
    conn.close()

if __name__ == "__main__":
    main()
