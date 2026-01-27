import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Agentic Honey-Pot Demo (Streamlit)", layout="wide")

st.title("Agentic Honey-Pot — Streamlit Demo")

st.markdown("Use this simple Streamlit app to send messages to the honeypot API and to inspect sessions.")

backend_url = st.sidebar.text_input("Backend base URL", value="http://localhost:8000")
api_key = st.sidebar.text_input("API Key", value="secret-key", type="password")

st.sidebar.markdown("\nQuick actions:\n")

col1, col2 = st.columns(2)
with col1:
    session_id = st.text_input("Session ID", value="demo-streamlit-1")
with col2:
    channel = st.selectbox("Channel", ["SMS", "WhatsApp", "Email", "Chat"], index=0)

message = st.text_area("Message", value="Your bank account will be blocked today. Verify immediately. Share your UPI ID: scammer@upi")

if st.button("Send Message"):
    payload = {
        "sessionId": session_id,
        "message": {"sender": "scammer", "text": message, "timestamp": datetime.utcnow().isoformat() + "Z"},
        "conversationHistory": [],
        "metadata": {"channel": channel, "language": "English", "locale": "IN"}
    }
    try:
        r = requests.post(f"{backend_url.rstrip('/')}/events", json=payload, headers={"x-api-key": api_key}, timeout=10)
        st.success(f"Status: {r.status_code}")
        st.json(r.json())
    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.header("Sessions")

if st.button("Refresh Sessions"):
    try:
        r = requests.get(f"{backend_url.rstrip('/')}/sessions", headers={"x-api-key": api_key}, timeout=10)
        if r.status_code == 200 and r.json().get("status") == "success":
            sessions = r.json().get("sessions", [])
            for s in sessions:
                with st.expander(f"{s['sessionId']} — messages: {s['totalMessages']}"):
                    st.write(f"Last seen: {s['lastSeen']}")
                    if st.button(f"View {s['sessionId']}"):
                        try:
                            rd = requests.get(f"{backend_url.rstrip('/')}/sessions/{s['sessionId']}", headers={"x-api-key": api_key}, timeout=10)
                            st.json(rd.json())
                        except Exception as e:
                            st.error(str(e))
        else:
            st.error(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Note: Do not commit API keys. Use Streamlit secrets or environment variables when deploying.")
