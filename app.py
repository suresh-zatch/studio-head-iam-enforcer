import streamlit as st
import os
import requests
import time
from google import genai
from google.genai import types

st.set_page_config(page_title="Studio Head | IAM Enforcer", layout="wide")
st.title("🎬 Studio Head: Cloud IAM Enforcer")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6KRnTUJenRKkK42aHcvptUO4vkYu6pDRI3-IosrV4aLSQ")
GRAFANA_LOKI_URL = st.secrets.get("GRAFANA_LOKI_URL", "https://logs-prod-028.grafana.net")
GRAFANA_USER_ID = st.secrets.get("GRAFANA_USER_ID", "1782114")
GRAFANA_TOKEN = st.secrets.get("GRAFANA_TOKEN", "glc_eyJvIjoiMTkwNTg3OSIsIm4iOiJzdGFjay0xODI0MzI3LWhsLXJlYWQtYWdlbnRpYy1jaW5lbWFzLWhhY2thdGhvbiIsImsiOiIzRDhFREhhbUl0MndONzNPbTl0N242NzIiLCJtIjp7InIiOiJwcm9kLWFwLXNvdXRoLTEifX0")

def push_test_log_to_grafana():
    """Pushes a real security threat log to Grafana Cloud Loki via REST API."""
    url = f"{GRAFANA_LOKI_URL.rstrip('/')}/loki/api/v1/push"
    ns_time = str(int(time.time() * 1e9))
    payload = {
        "streams": [{
            "stream": {"job": "vfx-access-logs", "env": "production"},
            "values": [
                [ns_time, "IP: 192.168.1.55 | User: vfx-vendor-external | Action: IAM_ELEVATION_ATTEMPT | Resource: roles/storage.admin | Status: DENIED"]
            ]
        }]
    }
    res = requests.post(url, auth=(GRAFANA_USER_ID, GRAFANA_TOKEN), json=payload, timeout=10)
    return res.status_code

def query_grafana_loki_logs(query: str) -> str:
    """The Agent Tool: Queries real logs from Grafana Cloud Loki."""
    url = f"{GRAFANA_LOKI_URL.rstrip('/')}/loki/api/v1/query_range"
    params = {
        "query": '{job="vfx-access-logs"}',
        "limit": 5
    }
    res = requests.get(url, auth=(GRAFANA_USER_ID, GRAFANA_TOKEN), params=params, timeout=10)
    if res.status_code == 200:
        return str(res.json().get("data", {}).get("result", []))
    return f"Grafana API Error: {res.text}"

st.markdown("### Step 1: Push Real Telemetry to Grafana Cloud")
if st.button("Push Breach Log to Grafana"):
    status = push_test_log_to_grafana()
    if status in [200, 204]:
        st.success("✅ Log successfully ingested into live Grafana Loki backend!")
    else:
        st.error(f"❌ Ingestion failed with status code: {status}. Verify token scope permissions.")

st.markdown("---")
st.markdown("### Step 2: Live Gemini Agent Audit")

if st.button("Run Live Agent Audit"):
    if not GEMINI_API_KEY:
        st.error("API Key is missing from Streamlit secrets.")
    else:
        with st.spinner("Connecting to Gemini and querying Grafana Loki API..."):
            client = genai.Client(api_key=GEMINI_API_KEY)
            chat = client.chats.create(
                model="gemini-3.6-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are an elite Cloud IAM security agent. Analyze the retrieved logs and generate an incident report with a gcloud remediation command.",
                    tools=[query_grafana_loki_logs],
                    temperature=0.2 
                )
            )
            response = chat.send_message("Query the Grafana logs for the last hour. Report any security anomalies.")
            st.success("Live Audit Complete")
            st.markdown("### 📋 Production Incident Report")
            st.markdown(response.text)
