import streamlit as st
import requests
import pandas as pd
import plotly.express as px 
import folium
from folium.plugins import HeatMap # Senior Feature: Heatmaps
from streamlit_folium import st_folium
from streamlit_calendar import calendar
from utils.data_insight import agent_say

# ---------------------------------------------------------
# 1. SETUP & CONFIG 
# ---------------------------------------------------------
st.set_page_config(
    page_title="Flood Forecast Prediction Model",
    page_icon="🌊",    
    layout="wide"
)

# Load custom CSS if available
try:
    st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)
except:
    pass 

API_URL = "https://sirasira-bangkok-flood-api.hf.space/predict"

# ---------------------------------------------------------
# 2. TOP SECTION: INTRO
# ---------------------------------------------------------
st.markdown("# Flood Forecasting Model")

agent_say('''
    Our flood forecasting model integrates both Fondue reports and drainage sensor levels 
    from the Drainage and Sewerage Department.
''', speed=0)

agent_say('''
    People-powered data from Traffy Fondue helps us map risk more precisely at a district level, 
    ensuring our model understands what’s actually happening—street by street.
''', speed=0)

st.divider()

# ---------------------------------------------------------
# 3. FILE UPLOAD & PREVIEW
# ---------------------------------------------------------
agent_say('To generate flood forecasts, please upload a CSV file containing these details:', speed=0)

with st.expander("See Data Requirements", expanded=False):
    st.markdown('''
        ### Data Requirements
        1. Format: .csv  
        2. Volume: 90 rows per area.
        3. Order: Chronological (Oldest to Newest)
        ---
        Required Columns: `subdistrict`, `rainfall`, `total_report`, `latitude`, `longitude`, `date`
    ''')
    template = {
        "subdistrict": "ลาดกระบัง", "rainfall": "0.11", "total_report": "3.4",
        "latitude": "13.72", "longitude": "100.75", "date": "2025-08-01"
    }
    st.table(pd.DataFrame([template]))

uploaded_file = st.file_uploader("Upload data", type="csv")

# Logic: Load user file OR fallback to example
if uploaded_file:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file)
    agent_say("File uploaded successfully! Ready for prediction.", speed=0)
else:
    df = pd.read_csv("data/example.csv")
    agent_say("Example data loaded—feel free to explore before uploading your own.", speed=0)

st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# 4. PREDICTION ENGINE
# ---------------------------------------------------------
if st.button("Get Flood Forecast"):
    
    # 1. Prepare File
    if uploaded_file:
        uploaded_file.seek(0)
        files = {"file": uploaded_file}
    else:
        files = {"file": open("data/example.csv", "rb")}

    # 2. Call API
    with st.spinner("⏳ Crunching numbers with the AI Model..."):
        try:
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    st.session_state['forecast'] = data
                    st.rerun() 
                else:
                    st.warning(f"API Notice: {data}")
            else:
                st.error(f"❌ API Error ({response.status_code}): {response.text}")
                
        except Exception as e:
            st.error(f"❌ Connection Failed: {e}")

# ---------------------------------------------------------
# 5. SENIOR DASHBOARD (OPTIMIZED)
# ---------------------------------------------------------
if 'forecast' in st.session_state and isinstance(st.session_state['forecast'], list):
    
    st.divider()
    st.markdown("## 📊 Forecast Dashboard")

    # --- 5.1 PERFORMANCE OPTIMIZATION (Hash Map) ---
    # Create a Coordinate Lookup Dictionary O(1) speed
    try:
        coord_map = (
            df.groupby('subdistrict')[['latitude', 'longitude']]
            .first() 
            .to_dict('index')
        )
    except KeyError:
        st.error("❌ Error: Uploaded CSV missing 'subdistrict', 'latitude', or 'longitude'.")
        st.stop()

    # --- 5.2 DATA CLEANING ---
    res_df = pd.DataFrame(st.session_state['forecast'])
    
    if 'subdistrict' in res_df.columns:
        res_df = res_df.rename(columns={'subdistrict': 'location'})

    # Normalize Risk Scores
    def clean_risk_probability(val):
        if isinstance(val, str): val = val.replace("%", "")
        try:
            v = float(val)
            return v * 100 if v <= 1.0 else v
        except: return 0.0

    res_df['risk_probability'] = res_df['risk_probability'].apply(clean_risk_probability)
    res_df['date'] = pd.to_datetime(res_df['date'])
    res_df = res_df.sort_values(['location', 'date']).reset_index(drop=True)

    # --- 5.3 GLOBAL METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    avg_risk = res_df['risk_probability'].mean()
    max_risk = res_df['risk_probability'].max()
    danger_days = res_df[res_df['risk_probability'] >= 80].shape[0]
    
    m1.metric("Average Risk", f"{avg_risk:.1f}%")
    m2.metric("Peak Risk", f"{max_risk:.1f}%", delta="Critical" if max_risk >= 80 else "Normal", delta_color="inverse")
    m3.metric("Danger Reports", f"{danger_days}", help="Reports where risk > 80%")
    m4.metric("Districts Monitored", f"{res_df['location'].nunique()}")

    # =========================================================
    # 5.4 TABS ARCHITECTURE
    # =========================================================
    tab1, tab2 = st.tabs(["🌎 Macro Overview", "🔍 Deep Dive Analysis"])

    # --- TAB 1: SMART TREND CHART ---
    with tab1:
        st.subheader("📈 Comparative Risk Trends")

        # Smart Default: Top 10 Riskiest
        risk_ranking = res_df.groupby('location')['risk_probability'].max().sort_values(ascending=False)
        top_10_riskiest = risk_ranking.head(3).index.tolist()
        all_locations = sorted(res_df['location'].unique())

        # Multiselect with Smart Defaults
        selected_districts_chart = st.multiselect(
            "Select Districts to Compare:", 
            options=all_locations, 
            default=top_10_riskiest
        )

        if selected_districts_chart:
            chart_data = res_df[res_df['location'].isin(selected_districts_chart)]
            
            fig = px.line(
                chart_data, 
                x='date', y='risk_probability', color='location', markers=True,
                color_discrete_sequence=px.colors.qualitative.Bold,
                height=400
            )
            # fig.add_hline(y=80, line_dash="dot", line_color="red", annotation_text="Threshold 80%")
            fig.update_layout(xaxis_title=None, template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select a district to view trends.")

    # --- TAB 2: DAILY OVERVIEW (HEATMAP + MARKERS) ---
    with tab2:
        # Layout: Date Slider | View Toggle
        c_slide, c_toggle = st.columns([3, 1])
        with c_slide:
            min_date, max_date = res_df['date'].min().date(), res_df['date'].max().date()
            selected_date = st.slider("Select Date:", min_value=min_date, max_value=max_date, value=min_date, format="YYYY-MM-DD")
        with c_toggle:
            map_style = st.radio("Map Style", ["📍 Markers", "🔥 Heatmap"], horizontal=True)

        day_data = res_df[res_df['date'].dt.date == selected_date]
        
        if not day_data.empty:
            m_all = folium.Map(location=[13.7563, 100.5018], zoom_start=11, tiles="CartoDB positron")
            heat_data = [] 

            for _, row in day_data.iterrows():
                loc_name = row['location']
                risk = row['risk_probability']
                
                # Optimized Lookup (Hash Map)
                coords = coord_map.get(loc_name)
                
                if coords:
                    lat, lon = coords['latitude'], coords['longitude']
                    
                    if map_style == "🔥 Heatmap":
                        # Weight by risk (0.0 to 1.0)
                        if risk > 10: heat_data.append([lat, lon, risk/100])
                    else:
                        # Marker Logic
                        if risk >= 80: color = "#ff4b4b"
                        elif risk >= 50: color = "#ffa500"
                        else: color = "#21c354"
                        
                        folium.CircleMarker(
                            location=[lat, lon], radius=15, color=color, 
                            fill=True, fill_color=color, fill_opacity=0.7,
                            popup=f"<b>{loc_name}</b><br>Risk: {risk:.1f}%"
                        ).add_to(m_all)

            # Render Heatmap Layer if selected
            if map_style == "🔥 Heatmap" and heat_data:
                HeatMap(
                    heat_data, radius=25, blur=15, max_zoom=10,
                    gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
                ).add_to(m_all)

            st_folium(m_all, height=500, use_container_width=True, key=f"map_{selected_date}_{map_style}")
            
            # Summary Table
            st.markdown(f"### 📋 Risk Report: {selected_date}")
            display_table = day_data[['location', 'risk_probability']].copy().sort_values('risk_probability', ascending=False)
            st.dataframe(
                display_table.style.background_gradient(subset=['risk_probability'], cmap="Reds"),
                use_container_width=True
            )
        else:
            st.info(f"No forecast data for {selected_date}.")