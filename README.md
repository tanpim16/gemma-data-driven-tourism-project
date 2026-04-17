# ✈️ Gemma-Insight: Smart-Event Strategist for Thailand’s Secondary Cities

### 🌟 Project Overview
This project is a **Data-centric Web Application** designed to enhance tourism strategies for Thailand's 55 secondary cities. By integrating **Gemma 4 AI** with historical tourism data and a curated festival master dataset, the app provides actionable insights for local entrepreneurs and policymakers.

---

### 🚀 Key Features
- **Multi-page Interface:** Built with Streamlit for a seamless user experience.
- **2 Operational Modes:**
  - **Non-AI Mode (Analytics Dashboard):** Real-time data visualization using **DuckDB** and **Plotly**.
  - **AI Mode (Smart Consultant):** AI-driven strategic recommendations powered by **Gemma 4**.
- **Deep Event Analysis:** Correlates tourism revenue with a master dataset of 39+ national and provincial festivals.

---

### 📖 Methodology

**1. Issues & Motivation**
* **Goal:** Bridge the gap between raw tourism data and actionable strategies for 55 secondary cities.
* **Problem:** Revenue is concentrated in major cities; local stakeholders struggle to interpret complex statistics.

**2. Data-Centric Approach**
* **Curation:** Developed a **Master Festival Dataset (39+ events)** with Economic Impact scores to add context to revenue data.
* **Engine:** Used **DuckDB** for high-performance data joining and "Quality over Quantity" feature engineering.

**3. AI Integration**
* **Consultant:** Integrated **Gemma 4** to transform data slices into business recommendations.
* **Seamless Flow:** Used **Streamlit Session State** to pass data context from the Dashboard to the AI, ensuring personalized insights.

---

### 🛠️ Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Data Engine:** [DuckDB](https://duckdb.org/) / Pandas
- **Database:** [Supabase](https://supabase.com/) (External Database for User Logs/Feedback)
- **AI Model:** Google Gemma 4
- **Visualization:** Plotly

