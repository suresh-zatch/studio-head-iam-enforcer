# 🎬 Studio Head: Cloud IAM Enforcer

An autonomous Gemini security agent that uses Grafana observability to detect and neutralize VFX vendor IAM threats in real-time. Built for the Google Cloud Agentic Cinema Hackathon (Grafana Track).

## How to Run

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables for `GEMINI_API_KEY`, `GRAFANA_URL`, and `GRAFANA_TOKEN`.
4. Run the app: `streamlit run app.py`

## Technologies Used
* Google Cloud `google-genai` SDK
* Grafana Cloud (Loki Logs simulation for MCP integration)
* Streamlit
