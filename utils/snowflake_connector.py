import streamlit as st
import snowflake.connector
import pandas as pd

@st.cache_resource
def get_snowflake_connection():
    cfg = st.secrets["snowflake"]
    return snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
    )

@st.cache_data(ttl=3600)
def query_snowflake(sql: str) -> pd.DataFrame:
    conn = get_snowflake_connection()
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)
