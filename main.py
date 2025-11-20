import streamlit as st
import pandas as pd
st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)

st.title("Rain Water Visualization -- JekTurnRight")
st.markdown('''
Traffy Fondue Dataset
2110403 Data Science and Data Engineering (DSDE-CEDT)

## Background
Data from Traffy Fondue Resources (Aug 2021 - Jan 2025),
Data consists of complaint reports submitted by citizens, primarily aggregated from Bangkok. The data are in CSV format

''')

if st.button("See example"):
    st.switch_page("pages/1_example.py")