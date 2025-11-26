import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from streamlit_calendar import calendar
from utils.data_insight import agent_say

st.set_page_config(
    page_title="Flood Forecast Prediction Model",
    page_icon="🌊",  
    layout="wide"
)

st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)

# --------------------------------
# Config
# --------------------------------
API_URL = "https://sirasira-bangkok-flood-api.hf.space/predict"

# --------------------------------
# Start of Page
# --------------------------------
st.markdown("# Flood Forecasting Model")
agent_say('''
    Our flood forecasting model integrates both Fondue reports and drainage sensor levels 
    from the Drainage and Sewerage Department.
''', speed=0)
agent_say('''
    People-powered data from Traffy Fondue helps us map risk more precisely at a district level, 
    ensuring our model understands what’s actually happening—street by street, community by community, 
    and not just where we have sensors installed.
''', speed=0)

st.divider()

# --------------------------------
# File Upload Section
# --------------------------------
agent_say('''
    To generate flood forecasts, please upload a CSV file containing these details:
''', speed=0)

with st.expander("See Data Requirements", expanded=False):
    st.markdown('''
        ### Data Requirements
        1. Format: .csv  
        2. Volume: 90 rows per area. The further date after the first 90 will be predicted.
        3. Order: Chronological (Oldest to Newest)
        ---
        Required Columns (Case-Sensitive):
        `subdistrict`, `rainfall`, `total_report`, `latitude`, `longitude`, `date`
    ''')
    template = {
        "subdistrict": "ลาดกระบัง",
        "rainfall": "0.11",
        "total_report": "3.4",
        "latitude": "13.72",
        "longitude": "100.75",
        "date": "2025-08-01"
    }
    st.table(pd.DataFrame([template]))

uploaded_file = st.file_uploader("Upload data", type="csv")

df = pd.read_csv("data/example.csv")  # default fallback
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    agent_say("File uploaded successfully! Ready for prediction.", speed=0)
else:
    agent_say("Example data loaded—feel free to explore before uploading your own.", speed=0)

st.write(df)

# --------------------------------
# Prediction Button
# --------------------------------


if st.button("Get Flood Forecast"):
    st.markdown("## Flood Forecast Results")

    # Use uploaded data if available, otherwise fallback to example
    if uploaded_file:
        files = {"file": uploaded_file}
    else:
        files = {"file": open("data/example.csv", "rb")}

    response = requests.post(API_URL, files=files).json()

    # Preserve the result under correct key logic
    st.session_state['forecast'] = response

# Render cached forecast so UI does NOT disappear
if 'forecast' in st.session_state:
    res_df = pd.DataFrame(st.session_state['forecast'])
    res_df['risk_score'] = res_df['risk_score'].str.replace("%", "").astype(float)

    # --- ensure your res_df exists and has proper types ---
    res_df['date'] = pd.to_datetime(res_df['date'])
    res_df = res_df.sort_values(['location', 'date']).reset_index(drop=True)
    res_df['risk_score'] = res_df['risk_score'].astype(float)

    # --- District/Subdistrict Sections ---
    for district, group in res_df.groupby("location"):
        st.markdown(f"### 🌊 Subdistrict Overview: {district}")

        # Collect district coordinate points (if exist)
        district_points = df[
            df['subdistrict'].str.contains(district, na=False)
        ][['latitude', 'longitude']].drop_duplicates()

        # Split layout into 2 columns
        col1, col2 = st.columns([1, 1])  # equal width split

        with col1:
            if not district_points.empty:
                # Map center
                center_lat = district_points['latitude'].astype(float).mean()
                center_lon = district_points['longitude'].astype(float).mean()

                m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
                for _, loc_row in district_points.iterrows():
                    folium.Marker([
                        float(loc_row['latitude']),
                        float(loc_row['longitude'])
                    ]).add_to(m)

                st_folium(m, use_container_width=True, key=f"map_{district}")
            else:
                st.info("No coordinate data for this subdistrict.")

        with col2:
            # Build calendar events for this subdistrict only
            calendar_events = []
            for _, day_row in group.iterrows():
                score = day_row['risk_score']
                if score >= 90:
                    title = f"🚨 {score:.1f}%"
                    color = "red"
                elif score >= 70:
                    title = f"🔴 {score:.1f}%"
                    color = "orange"
                elif score >= 50:
                    title = f"⚠️ {score:.1f}%"
                    color = "yellow"
                else:
                    continue  # below threshold → no calendar alert

                calendar_events.append({
                    "id": f"{district}_{day_row['date'].strftime('%Y%m%d')}",
                    "title": title,
                    "start": day_row['date'].strftime("%Y-%m-%d"),
                    "end": day_row['date'].strftime("%Y-%m-%d"),
                    "color": color,
                    "extendedProps": {
                        "location": district,
                        "status": day_row.get("status", "")
                    }
                })

            if calendar_events:
                calendar(
                    events=calendar_events,
                    key=f"calendar_{district}"  # 🔑 unique key per district
                )
            else:
                st.info("No flood alerts for this subdistrict.")

        st.divider()
