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
# 5. DASHBOARD (ANIMATED TIME-LAPSE & ALWAYS-ON MAP)
# ---------------------------------------------------------
from folium.plugins import TimestampedGeoJson # REQUIRED for Animation

if 'forecast' in st.session_state and isinstance(st.session_state['forecast'], list):
    
    st.divider()
    st.markdown("## 📊 Forecast Dashboard")

    # --- 5.1 PRE-CALCULATIONS ---
    try:
        coord_map = (
            df.groupby('subdistrict')[['latitude', 'longitude']]
            .first() 
            .to_dict('index')
        )
    except KeyError:
        st.error("❌ Error: Uploaded CSV missing 'subdistrict', 'latitude', or 'longitude'.")
        st.stop()

    # --- 5.2 DATA PREP ---
    res_df = pd.DataFrame(st.session_state['forecast'])
    
    # Normalization
    if 'subdistrict' in res_df.columns: res_df = res_df.rename(columns={'subdistrict': 'location'})
    
    # Handle Status Column
    for col in ['prediction', 'label', 'result']:
        if col in res_df.columns:
            res_df = res_df.rename(columns={col: 'Status'})
            break
    if 'Status' not in res_df.columns: res_df['Status'] = 'UNKNOWN'
    res_df['Status'] = res_df['Status'].astype(str).str.upper()

    # Clean Risk
    def clean_risk_probability(val):
        if isinstance(val, str): val = val.replace("%", "")
        try:
            v = float(val)
            return v * 100 if v <= 1.0 else v
        except: return 0.0

    res_df['risk_probability'] = res_df['risk_probability'].apply(clean_risk_probability)
    res_df['date'] = pd.to_datetime(res_df['date'])
    res_df = res_df.sort_values(['location', 'date']).reset_index(drop=True)

    # --- 5.3 METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    flood_days = res_df[res_df['Status'] == 'FLOOD'].shape[0]
    
    m1.metric("Average Risk", f"{res_df['risk_probability'].mean():.1f}%")
    m2.metric("Peak Risk", f"{res_df['risk_probability'].max():.1f}%")
    m3.metric("Total Flood Alerts", f"{flood_days}", help="Total predictions labeled FLOOD")
    m4.metric("Districts", f"{res_df['location'].nunique()}")

    # =========================================================
    # 5.4 TABS ARCHITECTURE
    # =========================================================
    tab1, tab2 = st.tabs(["🌎 Macro Overview", "🔍 Deep Dive Analysis"])

    # --- TAB 1: TRENDS ---
    with tab1:
        st.subheader("📈 Comparative Risk Trends")
        risk_ranking = res_df.groupby('location')['risk_probability'].max().sort_values(ascending=False)
        top_10 = risk_ranking.head(3).index.tolist()
        
        sel = st.multiselect("Select Districts:", sorted(res_df['location'].unique()), default=top_10)
        if sel:
            fig = px.line(res_df[res_df['location'].isin(sel)], x='date', y='risk_probability', color='location', markers=True)
            fig.add_hline(y=50, line_dash="dot", line_color="orange", annotation_text="Risk Zone")
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: DEEP DIVE (UPDATED) ---
    with tab2:
        # Senior UX: Allow user to switch between "Specific Day" and "Video Animation"
        view_mode = st.radio("Visualization Mode:", ["📅 Single Date Inspector", "▶️ Time-Lapse Animation"], horizontal=True)
        
        # =================================================
        # MODE A: SINGLE DATE INSPECTOR (Fixed Rule #1)
        # =================================================
        if view_mode == "📅 Single Date Inspector":
            min_d, max_d = res_df['date'].min().date(), res_df['date'].max().date()
            selected_date = st.slider("Select Date:", min_value=min_d, max_value=max_d, value=min_d)

            # Initialize Map OUTSIDE the loop (Fix for Rule #1)
            m_static = folium.Map(location=[13.7563, 100.5018], zoom_start=11, tiles="CartoDB positron")
            
            day_data = res_df[res_df['date'].dt.date == selected_date]
            count_markers = 0

            # Loop to add markers
            if not day_data.empty:
                for _, row in day_data.iterrows():
                    # STRICT FILTER
                    if row['Status'] != 'FLOOD': continue

                    count_markers += 1
                    coords = coord_map.get(row['location'])
                    if coords:
                        risk = row['risk_probability']
                        # Color Logic
                        if risk >= 90: c = "#ff4b4b"
                        elif risk >= 70: c = "#ffa500"
                        elif risk >= 50: c = "#ffff00"
                        else: c = "#ffff00"

                        folium.CircleMarker(
                            location=[coords['latitude'], coords['longitude']],
                            radius=15, color="black", weight=1, fill=True, fill_color=c, fill_opacity=0.8,
                            popup=f"<b>{row['location']}</b><br>Risk: {risk:.1f}%"
                        ).add_to(m_static)

            # RENDER MAP ALWAYS (Even if count_markers is 0)
            st_folium(m_static, height=500, use_container_width=True, key=f"static_map_{selected_date}")

            # Show status message BELOW map
            if count_markers == 0:
                st.info(f"✅ No confirmed 'FLOOD' status detected on {selected_date}. Map is clear.")
            else:
                st.warning(f"⚠️ Found {count_markers} critical areas on this date.")

        # =================================================
        # MODE B: TIME-LAPSE ANIMATION (Rule #2)
        # =================================================
        else:
            st.markdown("### 🎬 Flood Evolution Time-Lapse")
            st.caption("Press the 'Play' button on the map to watch the flood progression.")

            # 1. Filter Data: We usually only animate the 'FLOOD' events to keep it clean
            anim_data = res_df[res_df['Status'] == 'FLOOD'].copy()
            
            if anim_data.empty:
                st.success("No FLOOD events found in the entire dataset to animate.")
            else:
                # 2. Build GeoJSON Features
                features = []
                for _, row in anim_data.iterrows():
                    coords = coord_map.get(row['location'])
                    if coords:
                        risk = row['risk_probability']
                        # Color Logic (Same as above)
                        if risk >= 90: c = "#ff4b4b"
                        elif risk >= 70: c = "#ffa500"
                        else: c = "#ffff00"

                        # Create Feature
                        feature = {
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [coords['longitude'], coords['latitude']],
                            },
                            'properties': {
                                'time': row['date'].strftime('%Y-%m-%d'), # REQUIRED for animation
                                'style': {'color': c},
                                'icon': 'circle',
                                'iconstyle': {
                                    'fillColor': c,
                                    'fillOpacity': 0.8,
                                    'stroke': 'true',
                                    'radius': 10
                                },
                                'popup': f"{row['location']} ({risk:.0f}%)"
                            }
                        }
                        features.append(feature)

                # 3. Create Animation Map
                m_anim = folium.Map(location=[13.7563, 100.5018], zoom_start=11, tiles="CartoDB positron")

                TimestampedGeoJson(
                    {'type': 'FeatureCollection', 'features': features},
                    period='P1D',    # 1 Day per frame
                    add_last_point=True,
                    auto_play=False,
                    loop=False,
                    max_speed=10,
                    loop_button=True,
                    date_options='YYYY-MM-DD',
                    time_slider_drag_update=True
                ).add_to(m_anim)

                st_folium(m_anim, height=500, use_container_width=True, key="anim_map")