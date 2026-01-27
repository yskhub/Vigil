import streamlit as st
import requests
import json

st.set_page_config(page_title="Agentic Honeypot UI", page_icon="🪤")

st.title("Agentic Honeypot — Demo UI")

st.markdown("Send a test message to the backend `/events` endpoint and view the response.")

col1, col2 = st.columns(2)
with col1:
    backend_url = st.text_input("Backend base URL (e.g. https://your-backend.example.com)")
    api_key = st.text_input("x-api-key", type="password")
with col2:
    session_id = st.text_input("Session ID", value="demo-session")
    channel = st.selectbox("Channel", ["SMS", "WhatsApp", "Email"], index=0)

text = st.text_area("Message text", value="Your bank account will be blocked. Verify immediately.")

if st.button("Send message"):
    if not backend_url:
        st.error("Please provide `backend_url`.")
    elif not api_key:
        st.error("Please provide `x-api-key`.")
    else:
        payload = {
            "sessionId": session_id,
            "message": {"sender": "scammer", "text": text, "timestamp": ""},
            "conversationHistory": [],
            "metadata": {"channel": channel, "language": "English", "locale": "IN"}
        }
        url = backend_url.rstrip("/") + "/events"
        try:
            r = requests.post(url, json=payload, headers={"x-api-key": api_key, "Content-Type": "application/json"}, timeout=10)
            try:
                data = r.json()
            except Exception:
                data = {"status_text": r.text}
            st.write("Status:", r.status_code)
            st.json(data)
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
