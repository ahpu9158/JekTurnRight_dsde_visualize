import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time
import gdown
import os

# -----------------------------
# CONFIG
# -----------------------------
FILE_ID = "1tBAyy3PE_2LtqiY7-F1tj3wXIoNqGhXa"
DATA_PATH = "./tmp/data.csv"

# -----------------------------------------------
# Agent J Typing Function
# -----------------------------------------------
def agent_say(text, speed=0.02):
    with st.chat_message("agent"):
        msg = st.empty()
        display = ""

        for char in text:
            display += char
            msg.markdown(display + "▌")
            time.sleep(speed)

        msg.markdown(display)

# -----------------------------------------------
# Data Loader
# -----------------------------------------------
@st.cache_resource
def load_data():
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    if not os.path.exists(DATA_PATH):
        gdown.download(url, DATA_PATH, quiet=False)
    data = pd.read_csv(DATA_PATH)
    return data

# ------------------------------------------------
# PAGE START
# ------------------------------------------------
st.title("Data Insight")

df = load_data()
agent_say("Hello! I'm Agent JekTurnRight. Let's explore the data together. First, I'll load the data for us to analyze.")
agent_say("By the way, the data is from Traffy Fondue Resources (2022 - 2024), aggregated from Bangkok. Traffy Fondue is an open platform for collecting and analyzing public complaints about urban issues in Thailand.")
st.divider()
agent_say("Let look at tickets from 2022 to 2024.")

# Keep original df
df2 = df.copy()

# --------------------------------------------------
# SAFE TIMESTAMP PARSING (ISO8601)
# --------------------------------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce')
df.dropna(subset=['timestamp'], inplace=True)

# Filter for flood reports
df = df[df['type'].str.contains('น้ำท่วม')]

# -----------------------------------------------
# DAILY TREND (Matplotlib)
# -----------------------------------------------
daily_counts = df.set_index('timestamp').resample('D').size()

plt.figure(figsize=(12, 5))
daily_counts.plot(kind='line', color='teal')
plt.title('Daily Trend of Reports')
plt.ylabel('Number of Reports')
plt.grid(True, alpha=0.3)

# ------------------------------------------------
# TYPE CLEANING
# ------------------------------------------------
def parse_type_string(text):
    if not isinstance(text, str) or pd.isna(text):
        return []
    text = text.replace('{', '').replace('}', '').replace("'", "").replace('"', '')
    items = text.split(',')
    cleaned_items = [item.strip() for item in items if item.strip()]
    return cleaned_items

def clean_type_columns(df: pd.DataFrame, explode: bool = False) -> pd.DataFrame:
    df = df[df['type'] != '{}']
    df['type_list'] = df['type'].apply(parse_type_string)
    if explode:
        df = df.explode('type_list')
    return df

df_clean = clean_type_columns(df2, explode=False)

target_tag = "น้ำท่วม"

flood_rows = df_clean[df_clean['type_list'].apply(
    lambda x: target_tag in x if isinstance(x, list) else False
)].copy()

all_co_tags = flood_rows.explode('type_list')
co_occurrence = all_co_tags[all_co_tags['type_list'] != target_tag]

tag_counts = co_occurrence['type_list'].value_counts().reset_index()
tag_counts.columns = ['tag', 'count']

# ------------------------------------------------
# CO-OCCURRENCE BAR (Plotly)
# ------------------------------------------------
fig = px.bar(
    tag_counts.head(15),
    x='count',
    y='tag',
    orientation='h',
    title=f"Top Tags Co-occurring with '{target_tag}'",
    text='count',
    color='count',
    color_continuous_scale='Blues'
)
fig.update_layout(yaxis=dict(autorange="reversed"))

# -----------------------------------------------
# NEW: COMBINED TIME SERIES (ALL TYPES)
# -----------------------------------------------
df_ts = df_clean.copy()

# SAFE timestamp parsing (ISO8601)
df_ts['timestamp'] = pd.to_datetime(df_ts['timestamp'], format='ISO8601', errors='coerce')
df_ts.dropna(subset=['timestamp'], inplace=True)

# explode all types
df_ts = df_ts.explode('type_list')

# group by date and type
df_aggr = (
    df_ts
    .set_index('timestamp')
    .groupby([pd.Grouper(freq='D'), 'type_list'])
    .size()
    .reset_index(name='count')
)

# Combined line chart
fig_combined = px.line(
    df_aggr,
    x='timestamp',
    y='count',
    color='type_list',
    title="Daily Aggregation of Reports by Type (ALL TYPES)",
    labels={'timestamp': 'Date', 'count': 'Reports', 'type_list': 'Type'}
)
fig_combined.update_layout(hovermode='x unified', height=500)

# -----------------------------------------------
# LAYOUT
# -----------------------------------------------

st.plotly_chart(fig_combined, use_container_width=True)
