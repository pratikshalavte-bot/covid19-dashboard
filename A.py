import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    df = pd.read_excel("countrywise_covid_60rows.xlsx")
    return df

df = load_data()

st.title("🌍 Countrywise COVID-19 Dashboard")
st.markdown("Dashboard created using uploaded dataset (**60 rows**).")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())[:5]
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["cases", "deaths", "recovered"]
)

# Filter dataset
filtered_df = df[df["country"].isin(countries)]

# ---------- KPI CARDS ----------
st.subheader("📌 Key Highlights")

kpi_cols = st.columns(3)

kpi_cols[0].metric("Total Cases", f"{filtered_df['cases'].sum():,}")
kpi_cols[1].metric("Total Deaths", f"{filtered_df['deaths'].sum():,}")
kpi_cols[2].metric("Total Recovered", f"{filtered_df['recovered'].sum():,}")

# ---------- LINE CHART ----------
st.subheader(f"📈 Trend of {metric.capitalize()}")

fig_line = px.line(
    filtered_df,
    x="date",
    y=metric,
    color="country",
    markers=True,
    labels={metric: metric.capitalize(), "date": "Date"}
)
st.plotly_chart(fig_line, use_container_width=True)

# ---------- BAR CHART ----------
st.subheader(f"📊 Country Comparison — {metric.capitalize()}")

fig_bar = px.bar(
    filtere
