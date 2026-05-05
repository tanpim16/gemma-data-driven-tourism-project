import streamlit as st

pg = st.navigation([
    st.Page("intro.py",                        title="Introduction",     icon="🧠", default=True),
    st.Page("pages/1_Market_Analysis.py",      title="Market Analysis",  icon="📈"),
    st.Page("pages/2_CitySmart_Planner.py",    title="CitySmart Planner",icon="🤖"),
        st.Page("pages/3_Business_planning.py", title="Business Planning", icon="💼"),
])
pg.run()