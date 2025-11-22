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
st.set_page_config(
    page_title="Data Insight from Traffy Fondue",
    page_icon="🌊",  
    layout="wide" 
)
st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)
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
agent_say("Hello! We're JekTurnRight. Today, we'll explore data from Traffy Fondue together.")
agent_say("The data is from Traffy Fondue Resources (2022 - 2024), aggregated from Bangkok. Traffy Fondue is an open platform for collecting and analyzing public complaints about urban issues in Thailand.")
st.divider()
# agent_say("Let look at reports from 2022 to 2024.")
# ------------------------------------------------
# Step 0 -- Create daily report table, which contain amount of report in each date.
# ------------------------------------------------
st.markdown("## Daily Report Trend")
daily_reports = create_daily_report_table(df)

# ------------------------------------------------
# Report 1 : Distribution of report
# ------------------------------------------------
# if 'my_chart' in st.session_state:
#     st.pyplot(st.session_state.my_chart)
# else:
#     all_report_distribution(df)
agent_say("In Traffy Fondue, citizens can report various issues. Let's first look at the overall trend of daily reports from 2022 to 2024.")
all_report_distribution(df)
agent_say('''
          From the chart on the left, June is the month with the most report. But why?
        ''')
agent_say('''we can see the peak area around June to August 2022, which is the period **the platform was first lanched.**
          And then, the number of reports gradually decreased over time, and then tuned up to around 500 - 750 reports a day.
          ''')
agent_say('''Though the total reports was effected by the platform launch, we can also see that there are some trend that repeat in the next two years.
            You can see the trend each years from the chart below.
          ''')
all_report_interactive_distribution(df)
# ------------------------------------------------
# Report 2 : Distribution of each tag
# ------------------------------------------------
st.markdown("## Distribution of each tag")
agent_say('''Traffy Fondue allows users to tag their reports with relevant keywords. Let's explore the frequency of these tags to understand the common issues reported by citizens.
          ''')
tag_report_freq(df)
agent_say('''The most frequently used tags are related to road issues, pavement problems, flooding, polution and others.
          ''')
agent_say('''But here is what we see saw interesting. 
          ''')
# ------------------------------------------------
# Report 3 : Distribution of specific tag
# ------------------------------------------------
agent_say('''The road-related issues are the most frequently reported problems. But its trend is quite stable over time.
          ''')
tag_distribution(df, 'ถนน')
agent_say('''On the other hand, the flooding-related issues show a different pattern. Let's take a closer look at the trend of flooding reports over time.
          ''')
tag_distribution(df, 'น้ำท่วม')
agent_say('''We can see that the flooding reports have several peaks, especially during the rainy season. This indicates that flooding is a seasonal issue that affects many citizens.
          **For this reason, we will focus on the flooding-related reports for the rest of this analysis.**
          ''')
# ------------------------------------------------
# Report 4 : Distribution of co-occurrence tag with tag 'น้ำท่วม'
# ------------------------------------------------
st.markdown("## Analysis of flooding-related reports")
agent_say(''' First, let's explore the co-occurrence of tags with the flooding tag.
          ''')
co_occurrence_analysis(df, 'น้ำท่วม')
agent_say(''' Road, drain and canal are the top 3 co-occurrence tags with flooding tag. 
          ''')
# ------------------------------------------------
# Report 5 : Table number of reports
# ------------------------------------------------
### Report 5.1 : Table number of reports with tag 'น้ำท่วม' (all data)
agent_say(''' This is the total reports with flooding tag by each date from 2022 to 2024.
          ''')
df_complete = create_complete_daily_summary(df, shape)
with st.container():
    agent_say(''' Additional: This is the news from 21st June 2022 about flooding issue in Bangkok.
                ''')
    VIDEO_URL = "https://www.youtube.com/watch?v=N7Fvv2BQ3EU"
    st.video(VIDEO_URL)

#-------------------------------------------------
# Report 6 : Heat map of tag 'น้ำท่วม' in each subdistrict
#-------------------------------------------------
agent_say(''' Now, let's visualize the distribution of flooding reports across different subdistricts in Bangkok using a heatmap.
          ''')
tag_heatmap(df_complete)
agent_say(''' For better understanding, we can also see the time series heatmap of flooding reports in each subdistrict.
          ''')
tag_heatmap_time_series(df_complete)
# -----------------------------------------------
# Report 7 : Distribution of time-range to solve 'น้ำท่วม' problem
# -----------------------------------------------
agent_say(''' Lastly, let's look at the time taken to resolve flooding-related reports.
          ''')
solved_df = get_completed_flood_reports(df)
tag_time_solve_distribution(solved_df)
st.divider()
agent_say(''' Thank you for exploring the data with us! Next, you can proceed to the Model Prediction page to see our prediction flooding using machine learning models.
          ''')
# -----------------------------------------------
# Page Ends
# -----------------------------------------------
st.divider()
st.caption("JeckTurnRight © 2025")