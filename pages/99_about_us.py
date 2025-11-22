import streamlit as st
import random
import time
import re

# --- Language Dictionary ---
TEXTS = {
    "en": {
        "page_title": "About Us | JekTurnRight",
        "title": "About Us",
        "subheader_members": "Project Members",
        "project_info": "This project is developed by the team **\"JekTurnRight\"** for the 2110403 Data Science and Data Engineering (DSDE-CEDT) course.",
        "members": ["Titiporn Somboon", "Patcharapon Srisuwan", "Jedsada Meesuk", "Siravut Chunu"],
        "subheader_chat": "Chat with Agent J.",
        "initial_greeting": "Hello! I'm Agent J., ready to answer your questions about the **Bangkok Flooding Prediction** project. Ask me about the data, the model, or the team! (Type 'language=th')",
        "chat_placeholder": "Ask me about the project, data, or model...",
        "lang_switch_ack": "Language switched to English.",
        "default_responses": [
            "I'm here to talk about the project! We focus on using Traffy Fondue reports to predict flooding in Bangkok.",
            "Our primary data sources are citizen reports from the Traffy Fondue platform and relevant weather data.",
            "The model aims to forecast the probability of flooding in specific areas of Bangkok. What part of the model interests you?",
            "JekTurnRight is the student team from Chulalongkorn University. We are a team of four students."
        ]
    },
    "th": {
        "page_title": "เกี่ยวกับเรา | JekTurnRight",
        "title": "เกี่ยวกับเรา",
        "subheader_members": "สมาชิกโครงการ",
        "project_info": "โครงการนี้พัฒนาโดยทีม **\"JekTurnRight\"** สำหรับรายวิชา 2110403 Data Science and Data Engineering (DSDE-CEDT)",
        "members": ["ฐิติพร สมบูรณ์", "พัชรพล ศรีสุวรรณ", "เจษฎา มีสุข", "ศิรวุฒิ ชื่นอยู่"],
        "subheader_chat": "สนทนากับ Agent J.",
        "initial_greeting": "สวัสดีค่ะ/ครับ! ฉันคือ Agent J. พร้อมที่จะตอบคำถามเกี่ยวกับโครงการ **การทำนายน้ำท่วมกรุงเทพฯ** ถามฉันเกี่ยวกับข้อมูล โมเดล หรือทีมได้เลยค่ะ/ครับ! (พิมพ์ 'language=en')",
        "chat_placeholder": "ถามฉันเกี่ยวกับโครงการ ข้อมูล หรือโมเดล...",
        "lang_switch_ack": "เปลี่ยนภาษาเป็นภาษาไทยแล้ว",
        "default_responses": [
            "ฉันมาที่นี่เพื่อพูดคุยเกี่ยวกับโครงการ! เราเน้นการใช้รายงาน Traffy Fondue เพื่อทำนายน้ำท่วมในกรุงเทพฯ",
            "แหล่งข้อมูลหลักของเราคือรายงานจากประชาชนในแพลตฟอร์ม Traffy Fondue และข้อมูลสภาพอากาศที่เกี่ยวข้อง",
            "โมเดลมีเป้าหมายเพื่อพยากรณ์ความน่าจะเป็นของน้ำท่วมในพื้นที่เฉพาะของกรุงเทพฯ โมเดลส่วนใดที่คุณสนใจคะ/ครับ?",
            "JekTurnRight เป็นทีมของนักศึกษาจากจุฬาลงกรณ์มหาวิทยาลัย เรามีสมาชิกสี่คนค่ะ/ครับ"
        ]
    },
    "zh": {
        "page_title": "关于我们 | JekTurnRight",
        "title": "关于我们",
        "subheader_members": "项目成员",
        "project_info": "本项目由 **\"JekTurnRight\"** 团队为 2110403 数据科学与数据工程 (DSDE-CEDT) 课程开发。",
        "members": ["Titiporn Somboon", "Patcharapon Srisuwan", "Jedsada Meesuk", "Siravut Chunu"],
        "subheader_chat": "与 Agent J. 聊天",
        "initial_greeting": "你好！我是 Agent J.，随时可以回答你关于**曼谷洪水预测**项目的问题。请问关于数据、模型或团队的任何问题！ (输入 'language=en' 或 'language=th' 来切换语言。)",
        "chat_placeholder": "你想说什么？",
        "lang_switch_ack": "语言已切换为中文。",
        "default_responses": [
            "我在这里谈论这个项目！我们专注于使用 Traffy Fondue 报告来预测曼谷的洪水情况。",
            "我们的主要数据来源是 Traffy Fondue 平台上的市民报告和相关的天气数据。",
            "该模型的目的是预测曼谷特定地区发生洪水的概率。你对模型的哪一部分感兴趣？",
            "JekTurnRight 是朱拉隆功大学的学生团队。我们是一个由四名学生组成的团队。"
        ]
    }
}

# --- Initialization and Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'en' # Default language is English
lang = st.session_state.lang
T = TEXTS[lang]

st.set_page_config(
    page_title=T['page_title'],
    page_icon="🌊",  
    layout="wide" ,
    menu_items={
        'Get help': 'https://www.youtube.com/watch?v=cUwnLvgdo5g'
    }
)


st.title(f"👤 {T['title']}")
st.subheader(T['subheader_members'])
st.markdown(T['project_info'])
st.markdown('\n'.join([f' - {member}' for member in T['members']])) # Minimal list format
st.divider()

st.subheader(f"💬 {T['subheader_chat']}")

try:
    with open(r'custom_css/tab_style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

if "messages" not in st.session_state or st.session_state.messages[0]["content"] != T['initial_greeting']:
    st.session_state.messages = [
        {"role": "Jek", "content": T['initial_greeting']}
    ]

for message in st.session_state.messages:
    avatar = "assets/images/Jek.png" if message["role"] == "Jek" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(T['chat_placeholder']):

    lang_match = re.match(r"(?i)language=(en|th|zh)", prompt.strip())
    
    if lang_match:
        new_lang = lang_match.group(1).lower()
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)      
        st.session_state.lang = new_lang
        ack_message = TEXTS[new_lang]['lang_switch_ack']
        with st.chat_message("Jek", avatar="assets/images/Jek.png"):
            st.markdown(ack_message)
        st.rerun()
        
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["data", "traffy fondue"]):
            response = TEXTS[lang]['default_responses'][0] # Use a project-specific response
        elif any(keyword in prompt_lower for keyword in ["model", "prediction", "forecast"]):
            response = TEXTS[lang]['default_responses'][2]
        elif any(keyword in prompt_lower for keyword in ["team", "members", "jekturnright"]):
            response = TEXTS[lang]['default_responses'][3]
        else:
            response = random.choice(TEXTS[lang]['default_responses'])
        with st.chat_message("Jek", avatar="assets/images/Jek.png"):
            message_placeholder = st.empty()
            full = ""
            for chunk in response.split():
                full += chunk + " "
                time.sleep(0.03)
                message_placeholder.markdown(full + "▌")
            message_placeholder.markdown(full)

        st.session_state.messages.append({"role": "Jek", "content": full.strip()})