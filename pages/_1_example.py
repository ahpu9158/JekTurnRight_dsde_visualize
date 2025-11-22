import streamlit as st
import pandas as pd
st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)

st.markdown("## Example")
df = pd.read_csv("./data/station_metadata.csv")

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True)

st.subheader("Station Count by District")
district_counts = df["DistrictName"].value_counts().reset_index()
district_counts.columns = ["District", "Count"]
st.bar_chart(district_counts.set_index("District"))

st.subheader("Station Locations Map")
map_df = df[["StationName_Short", "DistrictName", "Latitude", "Longitude"]].dropna()
map_df = map_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
st.map(map_df)

st.subheader("Filter Stations by District")
district = st.selectbox("Select a District", ["All"] + sorted(df["DistrictName"].unique()))

if district != "All":
    filtered = df[df["DistrictName"] == district]
else:
    filtered = df

st.write(f"Showing **{len(filtered)}** stations")
st.dataframe(filtered, use_container_width=True)

st.markdown("you can write code too if you like")
code = '''def hello():
    print("Hello, Streamlit!")'''
st.code(code, language="python")