import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time
import gdown
import os

# -----------------------------
# CONFIG
# -----------------------------
FILE_ID = "1tBAyy3PE_2LtqiY7-F1tj3wXIoNqGhXa"
DATA_PATH = "./tmp/data.csv"

# -----------------------------------------------
# Agent J Typing Function
# -----------------------------------------------
def jek_say(text, speed=0.03):
    with st.chat_message("Jek", avatar="assets/images/Jek.png"):
        msg = st.empty()
        display = ""

        for char in text:
            display += char
            msg.markdown(display + "▌")   # cursor
            time.sleep(speed)

        msg.markdown(display)  # final (no cursor)

# -----------------------------------------------
# Data Loader
# -----------------------------------------------
@st.cache_resource
def load_data():
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    if not os.path.exists(DATA_PATH):
        gdown.download(url, DATA_PATH, quiet=False)
    data = pd.read_csv(DATA_PATH)
    return data

# ------------------------------------------------
# PAGE START
# ------------------------------------------------
st.title("Visualization with Jek")

# --- Agent J talks during loading ---
with st.chat_message("Jek", avatar="assets/images/Jek.png"):
    msg = st.empty()
    loading_text = "数据加载中，请稍等，我正在帮你下载文件……"
    dots = ""
    for i in range(20):  # ~4 seconds loading animation
        dots = "." * (i % 4)
        msg.markdown(f"{loading_text}{dots}")
        time.sleep(0.2)

data = load_data()

with st.chat_message("Jek", avatar="assets/images/Jek.png"):
    st.markdown("下载完成啦！我们继续吧～")

jek_say("数据载入好了，我已经准备好帮你分析啦！")

# ------------------------------------------------
# SHOW DATAFRAME
# ------------------------------------------------
st.dataframe(data)
jek_say("这是你上传的数据，我已经检查过啦，看起来一切正常～")

# ------------------------------------------------
# FILTERING
# ------------------------------------------------
df2 = data
df = data[data['type'].str.contains('น้ำท่วม')]
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ------------------------------------------------
# MONTHLY CHART
# ------------------------------------------------
monthly_counts = df.groupby(df['timestamp'].dt.month_name()).size()

order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
monthly_counts = monthly_counts.reindex(order)

plt.figure(figsize=(10, 5))
monthly_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Distribution of Reports by Month')
plt.ylabel('Number of Reports')
plt.xticks(rotation=45)
st.pyplot(plt)

jek_say("这是每个月出现『น้ำท่วม』的次数～看起来某些月份特别多，你要不要继续深入看看？")

# ------------------------------------------------
# DAILY TREND
# ------------------------------------------------
daily_counts = df.set_index('timestamp').resample('D').size()

plt.figure(figsize=(12, 5))
daily_counts.plot(kind='line', color='teal')
plt.title('Daily Trend of Reports')
plt.ylabel('Number of Reports')
plt.grid(True, alpha=0.3)
st.pyplot(plt)

jek_say("这里是每日趋势图～注意到某些天突然激增了吗？可能代表当天发生了大事件哦。")

# ------------------------------------------------
# TAG CO-OCCURRENCE
# ------------------------------------------------
def parse_type_string(text):
    if not isinstance(text, str) or pd.isna(text):
        return []
    text = text.replace('{', '').replace('}', '').replace("'", "").replace('"', '')
    items = text.split(',')
    cleaned_items = [item.strip() for item in items if item.strip()]
    return cleaned_items

def clean_type_columns(df: pd.DataFrame, explode: bool = False) -> pd.DataFrame:
    df = df[df['type'] != '{}']
    df['type_list'] = df['type'].apply(parse_type_string)

    if explode:
        df = df.explode('type_list')

    return df

df_clean = clean_type_columns(df2, explode=False)

target_tag = 'น้ำท่วม'

flood_rows = df_clean[df_clean['type_list'].apply(
    lambda x: target_tag in x if isinstance(x, list) else False
)].copy()

all_co_tags = flood_rows.explode('type_list')
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

jek_say("这些就是与『น้ำท่วม』最常一起出现的标签～可以帮助你分析事件之间的关系！")

# ------------------------------------------------
# END
# ------------------------------------------------
jek_say("所有分析都完成啦！如果你想让我解释更多内容，随时叫我～")
