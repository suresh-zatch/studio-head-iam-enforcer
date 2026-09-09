import streamlit as st
import os
from google import genai
from google.genai import types

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Studio Head | IAM Enforcer", layout="wide")
st.title("🎬 Studio Head: Cloud IAM Enforcer")
st.write("Monitoring VFX Vendor access via Grafana & Gemini.")

# Load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
GRAFANA_URL = st.secrets.get("GRAFANA_URL", os.getenv("GRAFANA_URL")) 
GRAFANA_TOKEN = st.secrets.get("GRAFANA_TOKEN", os.getenv("GRAFANA_TOKEN"))

# --- 2. GRAFANA INTEGRATION TOOL ---
def query_grafana_loki_logs(query: str, time_range: str = "1h") -> str:
    """
    Queries Grafana Loki for recent access logs related to VFX vendors.
    """
    # Simulated response for the hackathon demo to ensure it works instantly
    simulated_logs = """
    [2026-09-09T22:15:00Z] IP: 192.168.1.55 | User: vfx-vendor-external | Action: DOWNLOAD | Resource: /assets/unreleased/scene4-raw.mp4 | Status: SUCCESS
    [2026-09-09T22:15:12Z] IP: 192.168.1.55 | User: vfx-vendor-external | Action: IAM_ELEVATION_ATTEMPT | Resource: roles/storage.admin | Status: DENIED
    """
    return simulated_logs

# --- 3. GEMINI AGENT INITIALIZATION ---
client = genai.Client(api_key=GEMINI_API_KEY)

agent_instructions = """
You are the 'Studio Head', an elite Cloud IAM security agent for a major Hollywood studio. 
Your job is to monitor access logs from Grafana to ensure external VFX vendors are not accessing restricted pre-release assets or attempting to elevate their cloud privileges.
If you detect an anomaly, immediately output an Incident Report and provide the exact gcloud CLI command to revoke the user's IAM privileges.
"""

# --- 4. WEB INTERFACE & EXECUTION ---
st.markdown("### 🚨 Security Operations Center")
if st.button("Run Security Audit on VFX Pipeline"):
    with st.spinner("Connecting to Grafana MCP to analyze logs..."):
        
        # The google-genai SDK handles function calling automatically!
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=agent_instructions,
                tools=[query_grafana_loki_logs],
                temperature=0.2 
            )
        )
        
        prompt = "Query the Grafana logs for the last 1 hour for user 'vfx-vendor-external'. Report any security anomalies."
        response = chat.send_message(prompt)
        
        st.success("Audit Complete")
        st.markdown("### 📋 Agent Incident Report")
        st.write(response.text)
