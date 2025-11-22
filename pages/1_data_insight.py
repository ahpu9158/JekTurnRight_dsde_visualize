# -----------------------------
# imports
# -----------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time
import gdown
import os
from utils.data_insight import *
# -----------------------------
# CONFIG
# -----------------------------
FILE_ID = "1tBAyy3PE_2LtqiY7-F1tj3wXIoNqGhXa"
DATA_PATH = "./tmp/data.csv"
st.markdown("""
<style>
@font-face {
    font-family: 'Sarabun';
    src: url('fonts/THSarabunNew.ttf') format('truetype');
}
html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------
# PAGE START
# ------------------------------------------------
st.title("Data Insight")
load_data(FILE_ID, DATA_PATH)
df = setup_data()
shape = setup_shape()
# agent_say("Hello! I'm Agent JekTurnRight. Let's explore the data together. First, I'll load the data for us to analyze.")
# agent_say("By the way, the data is from Traffy Fondue Resources (2022 - 2024), aggregated from Bangkok. Traffy Fondue is an open platform for collecting and analyzing public complaints about urban issues in Thailand.")
# st.divider()
# agent_say("Let look at reports from 2022 to 2024.")
# ------------------------------------------------
# Step 0 -- Create daily report table, which contain amount of report in each date.
# ------------------------------------------------
st.markdown("## Daily Report Table")
daily_reports = create_daily_report_table(df)
# ------------------------------------------------
# Report 1 : Distribution of report
# ------------------------------------------------
# if 'my_chart' in st.session_state:
#     st.pyplot(st.session_state.my_chart)
# else:
#     all_report_distribution(df)
all_report_distribution(df)
all_report_interactive_distribution(df)
# ------------------------------------------------
tag_report_freq(df)
# ------------------------------------------------
tag_distribution(df, 'ถนน')
# ------------------------------------------------
tag_distribution(df, 'น้ำท่วม')
# ------------------------------------------------
co_occurrence_analysis(df, 'น้ำท่วม')
# ------------------------------------------------
df_complete = create_complete_daily_summary(df, shape)
#-------------------------------------------------
tag_heatmap(df_complete)
tag_heatmap_time_series(df_complete)
# -----------------------------------------------
# Report 7
# -----------------------------------------------
solved_df = get_completed_flood_reports(df)
tag_time_solve_distribution(solved_df)