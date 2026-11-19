import os

import streamlit as st
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

if "history" not in st.session_state:
    st.session_state.history = []

prompt = st.chat_input("prompt")

if prompt:
    st.session_state.history.append({"role": "user", "text": prompt})

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    st.session_state.history.append({"role": "assistant", "text": response.text})

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])