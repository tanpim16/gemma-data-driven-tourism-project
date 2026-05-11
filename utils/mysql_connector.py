import streamlit as st
import mysql.connector
import pandas as pd

@st.cache_resource
def get_mysql_connection():
    cfg = st.secrets["mysql"]
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
    )
    _ensure_table(conn)
    return conn

def _ensure_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_trips (
            id                    INT AUTO_INCREMENT PRIMARY KEY,
            trip_name             VARCHAR(200),
            province              VARCHAR(100),
            trip_date             DATE,
            num_days              INT,
            travelers             INT,
            budget                VARCHAR(50),
            itinerary             LONGTEXT,
            loop_route            VARCHAR(500),
            loop_highlights       LONGTEXT,
            estimated_budget_thb  INT,
            created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    # migrate เผื่อ table เก่าที่ยังไม่มี column ใหม่
    cur.execute("DESCRIBE saved_trips")
    existing = {r[0] for r in cur.fetchall()}
    for col, typ in [
        ('loop_route',           'VARCHAR(500)'),
        ('loop_highlights',      'LONGTEXT'),
        ('estimated_budget_thb', 'INT'),
    ]:
        if col not in existing:
            cur.execute(f'ALTER TABLE saved_trips ADD COLUMN {col} {typ}')
    conn.commit()
    cur.close()

def _cursor():
    conn = get_mysql_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=1)
    except Exception:
        get_mysql_connection.clear()
        conn = get_mysql_connection()
    return conn, conn.cursor(dictionary=True)

def save_trip(province, trip_date, num_days, travelers, budget,
              itinerary, loop_route=None, loop_highlights=None, estimated_budget_thb=None):
    trip_name = f"{province} · {trip_date.strftime('%d/%m/%Y') if hasattr(trip_date, 'strftime') else trip_date}"
    conn, cur = _cursor()
    cur.execute(
        """INSERT INTO saved_trips
           (trip_name, province, trip_date, num_days, travelers, budget,
            itinerary, loop_route, loop_highlights, estimated_budget_thb)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (trip_name, province, trip_date, num_days, travelers, budget,
         itinerary, loop_route, loop_highlights, estimated_budget_thb)
    )
    conn.commit()
    cur.close()

@st.cache_data(ttl=60)
def get_all_trips() -> pd.DataFrame:
    _, cur = _cursor()
    cur.execute("SELECT * FROM saved_trips ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows) if rows else pd.DataFrame()

def delete_trip(trip_id: int):
    conn, cur = _cursor()
    cur.execute("DELETE FROM saved_trips WHERE id = %s", (trip_id,))
    conn.commit()
    cur.close()
