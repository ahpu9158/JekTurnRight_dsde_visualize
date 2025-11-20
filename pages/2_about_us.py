import streamlit as st
import random
import time

st.markdown('<style>' + open(r'custom_css/tab_style.css').read() + '</style>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "Jek", "content": "让我们开始聊天吧！👇"}
    ]

# Render chat history with avatars
for message in st.session_state.messages:
    avatar = "assets/images/Jek.png" if message["role"] == "Jek" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("你想说什么？"):

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Jek response
    response = random.choice(
        [
            "你好呀！有什么我能帮你的吗？",
            "嗨，人类！需要我帮忙吗？",
            "你需要帮助吗？",
            "我在呢～你想聊点什么？",
            "有什么想问的？尽管说！"
        ]
    )

    # Display Jek with avatar
    with st.chat_message("Jek", avatar="assets/images/Jek.png"):
        message_placeholder = st.empty()
        full = ""
        for chunk in response.split():
            full += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full + "▌")
        message_placeholder.markdown(full)

    # Save Jek response
    st.session_state.messages.append({"role": "Jek", "content": full})
