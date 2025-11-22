import streamlit as st
import pandas as pd
import time
import gdown
import os
from utils.data_prep import *
import ipywidgets as widgets
from ipywidgets import interact
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import HeatMap, HeatMapWithTime
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

#-----------------------------------------------
# Configurations
#-----------------------------------------------
df_path = './tmp/data.csv'
shape_path = 'data/BMA/BMA_ADMIN_SUB_DISTRICT.shp'
check_subdis_path = 'data/raw/subwithdis.csv'
font_path = "fonts/THSarabunNew.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "TH Sarabun New"

# -----------------------------------------------
# Agent J Typing Function
# -----------------------------------------------
def agent_say(text, speed=0.02):
    with st.chat_message("agent", avatar="assets/images/icon.png"):
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
def load_data(FILE_ID, DATA_PATH):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    if not os.path.exists(DATA_PATH):
        gdown.download(url, DATA_PATH, quiet=False)
    #data = pd.read_csv(DATA_PATH)
    #return data
# -----------------------------------------------
# Setup Data and Shape
# -----------------------------------------------
# In your utility/data_prep or data_insight file

def setup_data():
    df = get_cleaned_data(df_path, shape_path, check_subdis_path)
    df = clean_type_columns(df)
    return df
def setup_shape():
    shape = get_shape_file(shape_path)
    shape['centroid'] = shape.geometry.centroid.to_crs(epsg=4326)
    shape['latitude'] = shape['centroid'].y
    shape['longitude'] = shape['centroid'].x
    return shape

def create_daily_report_table(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['date_timestamp'] = df['timestamp'].dt.date
    daily_reports = df.groupby('date_timestamp').size().reset_index(name='report_count')
    daily_reports.rename(columns={'date_timestamp':'date'}, inplace=True)
    return daily_reports
# -----------------------------------------------   
# Step 0 -- Create daily report table, which contain amount of report in each date.
# -----------------------------------------------   
def create_daily_report_table(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['date_timestamp'] = df['timestamp'].dt.date
    daily_reports = df.groupby('date_timestamp').size().reset_index(name='report_count')
    daily_reports.rename(columns={'date_timestamp':'date'}, inplace=True)
    #st.dataframe(daily_reports)
    return daily_reports
# ------------------------------------------------
# Report 1 : Distribution of report
# ------------------------------------------------
### Report 1.1 : Distribution of report (all year)
def all_report_distribution(df:pd.DataFrame):
    monthly_counts = df.groupby(df['timestamp'].dt.month_name()).size()

    order = ['January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts = monthly_counts.reindex(order)
    
    col1, col2 = st.columns(2)
    plt.figure(figsize=(10, 5))
    monthly_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Distribution of Reports by Month')
    plt.ylabel('Number of Reports')
    plt.xticks(rotation=45)
    with col1:
        st.pyplot(plt)
    daily_counts = df.set_index('timestamp').resample('D').size()
    plt.figure(figsize=(12, 5))
    daily_counts.plot(kind='line', color='teal')
    plt.title('Daily Trend of Reports')
    plt.ylabel('Number of Reports')
    plt.grid(True, alpha=0.3)
    with col2:
        st.pyplot(plt)
### Report 1.2 : Distribution of report (in a year)
### this function change from ipywidgets to streamlit version, because streamlit do not support ipywidgets
### TT
@st.fragment
def all_report_interactive_distribution(df: pd.DataFrame):
    chart_container = st.container()
    if "selected_years" not in st.session_state:
        st.session_state.selected_years = sorted(df["year_timestamp"].unique())
    all_years = sorted(df["year_timestamp"].unique())
    selected_years = chart_container.multiselect(
        "Select years",
        options=all_years,
        default=st.session_state.selected_years,
        key="select_years_key", 
    )
    st.session_state.selected_years = selected_years
    if not selected_years:
        chart_container.warning("No years selected!")
        return
    
    with chart_container:
        filtered_df = df[df["year_timestamp"].isin(selected_years)].copy()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        monthly_counts = filtered_df.groupby([filtered_df['timestamp'].dt.month, filtered_df['year_timestamp']]).size().unstack()
        monthly_counts.plot(kind='bar', ax=ax1, width=0.8)
        ax1.set_title(f"Monthly Distribution for: {', '.join(map(str, selected_years))}")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Number of Reports")
        daily_counts = filtered_df.set_index('timestamp').resample('D').size()
        daily_counts.plot(kind='line', ax=ax2)
        ax2.set_title("Daily Trend")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Number of Reports")
        plt.tight_layout()
        st.pyplot(fig)
# ------------------------------------------------
# Report 2 : Distribution of each tag
# ------------------------------------------------
### Report 2.1 : Distribution of each tag (all data)
@st.fragment
def tag_report_freq(df: pd.DataFrame):
    exploded_df = df.explode('type_list').copy()
    if pd.api.types.is_datetime64tz_dtype(exploded_df['timestamp']):
        exploded_df['timestamp'] = exploded_df['timestamp'].dt.tz_localize(None)
    exploded_df['month'] = exploded_df['timestamp'].dt.to_period('M').dt.start_time
    exploded_df['year'] = exploded_df['timestamp'].dt.year
    exploded_df.dropna(subset=['type_list', 'year'], inplace=True)
    exploded_df['year'] = exploded_df['year'].astype(int)
    all_years = sorted(exploded_df['year'].unique())
    all_possible_tags = sorted(exploded_df['type_list'].unique())
    palette = sns.color_palette("tab20", len(all_possible_tags)) 
    color_map = dict(zip(all_possible_tags, palette))
    
    chart_container = st.container()
    if "tag_selected_years" not in st.session_state:
        st.session_state.tag_selected_years = [all_years[-1]] if all_years else []
    selected_years = chart_container.multiselect(
        "เลือกปีที่ต้องการวิเคราะห์ (Select Years for Tag Frequency)",
        options=all_years,
        default=st.session_state.tag_selected_years,
        key="tag_year_select_key",
    )
    st.session_state.tag_selected_years = selected_years
    if not selected_years:
        chart_container.warning("โปรดเลือกปีอย่างน้อยหนึ่งปี (Please select at least one year).")
        return
    
    with chart_container:
        filtered_data = exploded_df[exploded_df['year'].isin(selected_years)]
        if filtered_data.empty:
            st.warning(f"ไม่พบข้อมูลสำหรับปี: {', '.join(map(str, selected_years))}")
            return
        trend_data = filtered_data.groupby(['month', 'type_list']).size().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for tag in trend_data.columns:
            if trend_data[tag].sum() > 0:
                ax.plot(
                    trend_data.index, 
                    trend_data[tag], 
                    marker='o', 
                    linewidth=2, 
                    label=tag, 
                    color=color_map.get(tag, 'black')
                )
        
        year_str = ", ".join(map(str, selected_years))
        ax.set_title(f"Trend of each type in {year_str}")
        ax.set_xlabel("Month") 
        ax.set_ylabel("Number of Reports")
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.155), ncol=8)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
# ------------------------------------------------
# Report 3 : Distribution of specific tag
# ------------------------------------------------
def tag_distribution(flood_df:pd.DataFrame, tag:str):
    col1, col2 = st.columns(2)

    flood_df = flood_df[flood_df['type'].str.contains(tag)]

    monthly_counts = flood_df.groupby(flood_df['timestamp'].dt.month_name()).size()

    order = ['January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts = monthly_counts.reindex(order)

    plt.figure(figsize=(10, 5))
    monthly_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Distribution of Reports by Month')
    plt.ylabel('Number of Reports')
    plt.xticks(rotation=45)
    with col1:
        st.pyplot(plt)

    daily_counts = flood_df.set_index('timestamp').resample('D').size()
    plt.figure(figsize=(12, 5))
    daily_counts.plot(kind='line', color='teal')
    plt.title('Daily Trend of Reports')
    plt.ylabel('Number of Reports')
    plt.grid(True, alpha=0.3)
    with col2:
        st.pyplot(plt)
# ------------------------------------------------
# Report 4 : Distribution of co-occurrence tag with tag 'น้ำท่วม'
# ------------------------------------------------
### Report 4.1 : Distribution of co-occurrence tag with tag 'น้ำท่วม' (all data)
def co_occurrence_analysis(df:pd.DataFrame, target_tag: str):

    flood_rows = df[df['type_list'].apply(lambda x: target_tag in x if isinstance(x, list) else False)].copy()
    all_co_tags = flood_rows.explode('type_list')
    all_co_tags['type_list'] = all_co_tags['type_list'].astype(str)
    co_occurrence = all_co_tags[all_co_tags['type_list'] != target_tag]
    tag_counts = co_occurrence['type_list'].value_counts().reset_index()
    tag_counts.columns = ['tag', 'count']

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
    st.plotly_chart(fig)

# ------------------------------------------------
# Report 5 : Table number of reports
# ------------------------------------------------
### Report 5.1 : Table number of reports with tag 'น้ำท่วม' (all data)
def create_complete_daily_summary(df: pd.DataFrame, shape_centers: pd.DataFrame):
    shape_dist_col = 'district'
    shape_sub_col  = 'subdistrict'
    df_dist_col    = 'district'
    df_sub_col     = 'subdistrict'
    start_date = '2022-01-01'
    end_date = '2024-12-31'

    all_dates = pd.DataFrame({'date': pd.date_range(start=start_date, end=end_date, freq='D').date})

    master_locations = shape_centers[[shape_dist_col, shape_sub_col, 'latitude', 'longitude']].copy()

    daily_counts = df.groupby([df_dist_col, df_sub_col, df['timestamp'].dt.date]).size().reset_index(name='number_of_report')
    daily_counts.rename(columns={'timestamp': 'date'}, inplace=True)

    master_locations['_key'] = 1
    all_dates['_key'] = 1
    full_grid = pd.merge(master_locations, all_dates, on='_key').drop('_key', axis=1)

    df_complete = full_grid.merge(
                    daily_counts,
                    left_on=[shape_dist_col, shape_sub_col, 'date'],
                    right_on=[df_dist_col, df_sub_col, 'date'],
                    how='left')
    
    df_complete['number_of_report'] = df_complete['number_of_report'].fillna(0).astype(int)
    df_complete = df_complete[[shape_dist_col, shape_sub_col, 'date', 'number_of_report', 'latitude', 'longitude']]

    df_complete.rename(columns={
        shape_dist_col: 'district', 
        shape_sub_col: 'subdistrict'
    }, inplace=True)

    to_show_df = df_complete.sort_values(by=['number_of_report'], ascending=False).head(10).reset_index(drop=True)
    st.dataframe(to_show_df)
    return df_complete
#-------------------------------------------------
# Report 6 : Heat map of tag 'น้ำท่วม' in each subdistrict
#-------------------------------------------------
### Report 6.1 : Heat map of tag 'น้ำท่วม' in each subdistrict (accumurate all year)
def tag_heatmap(df_complete:pd.DataFrame):

    map_data = df_complete[df_complete['number_of_report'] > 0]

    center_lat = map_data['latitude'].mean()
    center_lon = map_data['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    heat_data = map_data[['latitude', 'longitude', 'number_of_report']].values.tolist()

    HeatMap(heat_data, radius=15, max_zoom=13).add_to(m)
    m.save('./tmp/static_heatmap.html')
    st.components.v1.html(open('./tmp/static_heatmap.html', 'r').read(), height=600)

### Report 6.2: Heat map of tag 'น้ำท่วม' in each subdistrict (time-series)
def tag_heatmap_time_series(df_complete: pd.DataFrame):

    df_complete['date'] = pd.to_datetime(df_complete['date'])
    df_complete['month'] = df_complete['date'].dt.to_period('M').dt.start_time
    monthly_df = df_complete.groupby(['latitude', 'longitude', 'month'])['number_of_report'].sum().reset_index()

    time_index = sorted(monthly_df['month'].unique()) # Get all months in order
    data_by_month = []
    time_labels = []

    for m_date in time_index:
        month_data = monthly_df[monthly_df['month'] == m_date]
        month_data = month_data[month_data['number_of_report'] > 0]
        data_by_month.append(month_data[['latitude', 'longitude', 'number_of_report']].values.tolist())
        time_labels.append(m_date.strftime('%Y-%m'))

    center_lat = monthly_df['latitude'].mean()
    center_lon = monthly_df['longitude'].mean()
    m2 = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    HeatMapWithTime(
        data_by_month, 
        index=time_labels,
        radius=25,
        auto_play=True,
        max_opacity=0.6,
    ).add_to(m2)

    m2.save('./tmp/monthly_flood_heatmap.html')
    st.components.v1.html(open('./tmp/monthly_flood_heatmap.html', 'r').read(), height=600)

# -----------------------------------------------
# Report 7 : Distribution of time-range to solve 'น้ำท่วม' problem
# -----------------------------------------------
### Report 7.1 : Distribution of time-range to solve 'น้ำท่วม' problem
def get_completed_flood_reports(df):
    selected_cols = ['district', 'subdistrict', 'timestamp', 'last_activity', 'latitude', 'longitude']

    # Get type 'น้ำท่วม'
    solve_df = df[df['type'].str.contains('น้ำท่วม')]

    # Get only 'เสร็จสิ้น' type
    solve_df = solve_df[solve_df['state'] == 'เสร็จสิ้น']

    # Get only selected columns
    solve_df = solve_df[selected_cols]

    # Convert date columns to date format
    solve_df['timestamp'] = pd.to_datetime(solve_df['timestamp']).dt.normalize()
    solve_df['last_activity'] = pd.to_datetime(solve_df['last_activity']).dt.normalize()

    # Create new time-range cols
    solve_df['range'] = solve_df['last_activity'] - solve_df['timestamp']
    return solve_df
def tag_time_solve_distribution(solve_df:pd.DataFrame):

    solve_df['days_taken'] = solve_df['range'].dt.days

    bins = [0, 7, 14, 21, 30, 90, 180, 365, float('inf')]
    labels = [
        '<= 1 Week', 
        '1 - 2 Weeks', 
        '2 - 3 Weeks', 
        '3 Weeks - 1 Month', 
        '1 - 3 Months', 
        '3 - 6 Months', 
        '6 Months - 1 Year', 
        '> 1 Year'
    ]

    solve_df['duration_group'] = pd.cut(
        solve_df['days_taken'], 
        bins=bins, 
        labels=labels, 
        right=True,
        include_lowest=True
    )

    dist_counts = solve_df['duration_group'].value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x=dist_counts.index, y=dist_counts.values, palette='viridis')

    for i, v in enumerate(dist_counts.values):
        ax.text(i, v + (v*0.01), str(v), ha='center', fontweight='bold')

    plt.title('Distribution of Flood Report Resolution Times', fontsize=14)
    plt.ylabel('Number of Reports')
    plt.xlabel('Duration')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    st.pyplot(plt)