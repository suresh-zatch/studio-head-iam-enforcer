import streamlit as st
import os
import requests
import time
from google import genai
from google.genai import types

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Studio Head | IAM Enforcer", layout="wide")
st.title("🎬 Studio Head: Cloud IAM Enforcer")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GRAFANA_LOKI_URL = st.secrets.get("GRAFANA_LOKI_URL", "") 
GRAFANA_USER_ID = st.secrets.get("GRAFANA_USER_ID", "")   
GRAFANA_TOKEN = st.secrets.get("GRAFANA_TOKEN", "")       

# --- 2. 100% REAL GRAFANA INTEGRATION ---
def push_test_log_to_grafana():
    """Pushes a real, live log entry into your Grafana Cloud instance."""
    url = f"{GRAFANA_LOKI_URL}/loki/api/v1/push"
    # Loki requires the timestamp in nanoseconds
    ns_time = str(int(time.time() * 1e9))
    payload = {
        "streams": [{
            "stream": {"job": "vfx-access-logs", "env": "production"},
            "values": [
                [ns_time, "IP: 192.168.1.55 | User: vfx-vendor-external | Action: IAM_ELEVATION_ATTEMPT | Resource: roles/storage.admin | Status: DENIED"]
            ]
        }]
    }
    # Grafana Cloud Loki uses Basic Auth (User ID + Token)
    res = requests.post(url, auth=(GRAFANA_USER_ID, GRAFANA_TOKEN), json=payload)
    return res.status_code

def query_grafana_loki_logs(query: str) -> str:
    """The Agent Tool: Queries REAL Grafana Cloud Loki for access logs."""
    url = f"{GRAFANA_LOKI_URL}/loki/api/v1/query_range"
    params = {
        "query": '{job="vfx-access-logs"}',
        "limit": 10
    }
    res = requests.get(url, auth=(GRAFANA_USER_ID, GRAFANA_TOKEN), params=params)
    
    if res.status_code == 200:
        results = res.json().get("data", {}).get("result", [])
        if not results:
            return "No logs found in Grafana. The environment is secure."
        return str(results)
    return f"Grafana API Error: {res.text}"

# --- 3. GEMINI AGENT INITIALIZATION ---
client = genai.Client(api_key=GEMINI_API_KEY)

agent_instructions = """
You are the 'Studio Head', an elite Cloud IAM security agent for a major Hollywood studio. 
Your job is to monitor access logs from Grafana to ensure external VFX vendors are not accessing restricted pre-release assets or attempting to elevate their cloud privileges.
If you detect an anomaly, immediately output an Incident Report and provide the exact gcloud CLI command to revoke the user's IAM privileges.
"""

# --- 4. WEB INTERFACE & EXECUTION ---
st.markdown("### Step 1: Generate Live Grafana Data")
st.write("Push a real threat log into your live Grafana Cloud instance to give the agent something to find.")

if st.button("Push Breach Log to Grafana"):
    if not GRAFANA_LOKI_URL:
        st.error("Missing Grafana credentials in Streamlit Secrets!")
    else:
        status = push_test_log_to_grafana()
        if status == 204:
            st.success("✅ Real log successfully pushed to Grafana Cloud!")
        else:
            st.error(f"❌ Failed to push log. Error Code: {status}")

st.markdown("---")
st.markdown("### Step 2: Autonomous Security Operations Center")

if st.button("Run Live Agent Audit"):
    if not GEMINI_API_KEY:
        st.error("API Key is missing!")
    else:
        with st.spinner("Agent is querying real logs directly from Grafana Cloud..."):
            try:
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=agent_instructions,
                        tools=[query_grafana_loki_logs],
                        temperature=0.2 
                    )
                )
                
                response = chat.send_message("Query the Grafana logs for the last hour. Report any security anomalies.")
                
                st.success("Audit Complete")
                st.markdown("### 📋 Agent Incident Report")
                st.write(response.text)
            except Exception as e:
                st.error(f"Execution Failed: {str(e)}")
