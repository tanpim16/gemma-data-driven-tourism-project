import streamlit as st
import mysql.connector
import pandas as pd

@st.cache_resource
def get_mysql_connection():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
    )

def _cursor():
    conn = get_mysql_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=1)
    except Exception:
        get_mysql_connection.clear()
        conn = get_mysql_connection()
    return conn, conn.cursor(dictionary=True)

def save_trip(trip_name, province, trip_date, num_days, travelers, budget, itinerary):
    conn, cur = _cursor()
    cur.execute(
        """INSERT INTO saved_trips
           (trip_name, province, trip_date, num_days, travelers, budget, itinerary)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (trip_name, province, trip_date, num_days, travelers, budget, itinerary)
    )
    conn.commit()
    cur.close()

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
