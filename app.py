# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="COVID-19 Country Dashboard", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    # OWID country-level COVID dataset (CSV)
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url, parse_dates=["date"])
    return df

df = load_data()

st.title("🌍 COVID-19 Country Dashboard")
st.markdown("Source: Our World in Data — updated automatically.")

# Sidebar filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect(
    "Select countries (max 8)", 
    options=sorted(df['location'].unique()), 
    default=["India", "United States"]
)
metric = st.sidebar.selectbox(
    "Metric", 
    ["new_cases", "new_deaths", "total_cases", "total_deaths", "people_vaccinated", "people_fully_vaccinated"]
)
start_date = st.sidebar.date_input("Start date", value=df['date'].min().date())
end_date = st.sidebar.date_input("End date", value=df['date'].max().date())

if start_date > end_date:
    st.sidebar.error("Start date must be before end date")

# Filter data
mask = (
    (df['location'].isin(countries)) &
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date))
)
plot_df = df.loc[mask, ["date", "location", metric, "total_cases", "total_deaths", "new_cases", "new_deaths", "people_vaccinated", "people_fully_vaccinated"]].copy()
plot_df = plot_df.sort_values(["location", "date"])

# Basic KPIs for selected countries (latest date)
st.subheader("Key indicators (latest)")
latest = plot_df.groupby("location").apply(lambda g: g.loc[g['date'].idxmax()]).reset_index(drop=True)
kpi_cols = st.columns(len(latest))
for col, (_, row) in zip(kpi_cols, latest.iterrows()):
    col.metric(label=f"{row['location']}", value=f"Total cases: {int(row['total_cases']):,}" if not pd.isna(row['total_cases']) else "N/A",
               delta=f"New cases: {int(row['new_cases']):,}" if not pd.isna(row['new_cases']) else "")

# Time series line chart for metric
st.subheader(f"Time series — {metric}")
fig = px.line(plot_df, x="date", y=metric, color="location", labels={"date":"Date", metric:metric})
fig.update_layout(height=450, legend_title_text=None, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# Rolling average option
if st.checkbox("Show 7-day rolling average", value=True):
    roll_df = plot_df.copy()
    roll_df[metric + "_7d"] = roll_df.groupby("location")[metric].transform(lambda x: x.rolling(7, min_periods=1).mean())
    fig2 = px.line(roll_df, x="date", y=metric + "_7d", color="location", labels={"date":"Date", metric + "_7d":f"{metric} (7d avg)"})
    fig2.update_layout(height=400, hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

# Country comparison bar (latest)
st.subheader("Comparison (latest date selected)")
bar_df = latest[['location', metric]].sort_values(metric, ascending=False)
fig3 = px.bar(bar_df, x=metric, y='location', orientation='h', labels={metric: metric, 'location':'Country'})
st.plotly_chart(fig3, use_container_width=True)

# Map (cases per million at latest date)
if "iso_code" in df.columns and "total_cases_per_million" in df.columns:
    st.subheader("World map — total cases per million (latest available)")
    map_df = df.loc[df['date'] == df['date'].max(), ['iso_code', 'location', 'total_cases_per_million', 'total_deaths_per_million', 'new_cases_per_million']].dropna(subset=['iso_code'])
    fig_map = px.choropleth(map_df, locations="iso_code", color="total_cases_per_million", hover_name="location", projection="natural earth", labels={"total_cases_per_million":"Cases per million"})
    fig_map.update_layout(height=500)
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Map not available: dataset missing iso codes or per-million metrics.")

# Data table + download
st.subheader("Data — table and download")
show_table = st.checkbox("Show raw data table", value=False)
if show_table:
    st.dataframe(plot_df)

csv = plot_df.to_csv(index=False)
st.download_button("Download filtered CSV", data=csv, file_name=f"covid_filtered_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Plotly. Fork on GitHub and improve!")
