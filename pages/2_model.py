import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from utils.data_insight import agent_say
st.set_page_config(
    page_title="Flood Forecast Prediction Model",
    page_icon="🌊",  
    layout="wide" 
)
st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)
# --------------------------------
# config
# --------------------------------
API_URL = "https://sirasira-bangkok-flood-api.hf.space/predict_csv"
# --------------------------------
# Start of Page
# --------------------------------

st.markdown("# Flood Forecasting Model")
agent_say('''
    Our flood forecasting model integrates both Fondue reports and water level data 
    from the Drainage and Sewerage Department.
''', speed=0)
agent_say('''
    We use Traffy Fondue data because it provides hyper-local, ground-truth reports 
    directly from people in each area. 
    Sensor-based water level data alone cannot fully cover every location, 
    but Fondue reports help fill those gaps and give us a much more detailed 
    understanding of the situation on the ground.
''', speed=0)
st.divider()
# --------------------------------
# File Upload
# --------------------------------
agent_say('''
    To generate flood forecasts, please upload a CSV file containing these details below:
''', speed=0)
expander = st.expander("See Data Requirements", expanded=False)
with expander:
    st.markdown('''
        ### Data Requirements
        To generate a flood forecast, upload a CSV file containing at least 30 days of historical data.
        File Rules:
        1. Format: .csv (Comma Separated Values).
        2. Volume: Minimum 30 rows (to detect trends). Recommended 90 rows (for maximum accuracy).
        3. Order: Chronological (Oldest date at the top, newest at the bottom).
        ---

        Required Columns (Case-Sensitive) and Example Data:
        ''')
    data_requirements = {
        "year_timestamp": "2025",
        "month_timestamp": "10",
        "days_timestamp": "2",
        "subdistrict": "Lat Krabang",
        "water_level": "1.5",
        "total_report": "5.0",
        "latitude": "13.72",
        "longitude": "100.75"
    }
    req_df = pd.DataFrame([data_requirements])
    st.table(req_df)
            
    agent_say('''
        You can download an example CSV file from the link below to see the required format:
    ''', speed=0)
    with open("data/template.csv", "rb") as f:
        st.download_button(
            label="Download template CSV",
            data=f,
            file_name="data.csv",
            mime="text/csv",
            icon=":material/download:",
        )

uploaded_file = st.file_uploader(
    "Upload data", accept_multiple_files=False, type="csv"
)
df = pd.read_csv("data/example.csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    agent_say("File uploaded successfully! Now, let's send the data to our flood forecasting API for predictions.", speed=0)
else:
    agent_say("You can also use example data for clearer view first", speed=0)
st.write(df)
# --------------------------------
# API Call
# --------------------------------
if st.button("Get Flood Forecast"):
    st.markdown("## Flood Forecast Results")
    with open("data/example.csv", "rb") as f:
        files = {"file": f}
        if( uploaded_file is not None):
            files = {"file": uploaded_file}
        response = requests.post(API_URL, files=files).json()
    #st.json(response, expanded=True)

    lat = df[df["subdistrict"] == response["location"]]["latitude"].values[0]
    lon = df[df["subdistrict"] == response["location"]]["longitude"].values[0]
    col1, col2 = st.columns(2)
    with col1:
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12, height=400)
    with col2:
        st.markdown(f"### Location: {response['location']}")
        st.markdown(f"### Date: {response['date']}")
        st.metric(label="Risk Percentage", value=f"{response['risk_percentage']}")
        st.badge(label=response['status'], color="red" if response['status']=="FLOOD ALERT" else "green", width="stretch")
        
st.divider()
st.caption("JeckTurnRight © 2025")