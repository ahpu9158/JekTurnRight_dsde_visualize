import streamlit as st
import pandas as pd

# --------------------------------
# config
# --------------------------------
st.set_page_config(
    page_title="Flooding Prediction in Bangkok",
    page_icon="🌊",  
    layout="wide" 
)
st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)

# --------------------------------
# Start of Page
# --------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #1f77b4; font-size: 2.5em;'>
        Integrating Traffy Fondue Reports for Flooding Prediction in Bangkok (2022–2024)
    </h1>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <div>
        <p style='font-size: 1.1em;'>
        This project is a submission by the <a href="/about_us" style='color: #d62728; text-decoration: none;'><strong>JekTurnRight</strong></a> team for the course:
        </p>
        <p style='font-size: 1.2em; font-weight: bold; color: #333333; margin-left: 10px;'>
        2110403 Data Science and Data Engineering (DSDE-CEDT) at Chulalongkorn University.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# -----------------------------------------------
# Page Ends
# -----------------------------------------------
st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("Data Insight Page", use_container_width=True, type="primary"):
        st.switch_page("pages/1_example.py")

with col2:
    if st.button("Flood Forecast Model Page", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_model.py")
st.markdown(
    """
    <style>
    div.stButton > button {
        font-size: 1.2em;
        height: 3em; 
        border-radius: 10px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.divider()
st.caption("JeckTurnRight © 2025")