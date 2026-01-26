import json
import uuid
import platform
import os
import socket
from datetime import datetime
from utils.constants import TOKEN_FILE, DATA_FILE as HISTORY_FILE

def load_email():
    with open(TOKEN_FILE, "r") as f:
        token = json.load(f)
    return token["profile"]["email"]

def generate_secret_id():
    # Stable per-machine secret
    # (store once, reuse forever)
    secret_id = str(uuid.uuid4())
    with open(".secret_id", "w") as f:
        f.write(secret_id)
    return secret_id

import requests
import gzip
import json

def get_cloud_analysis(history_dict):
    # Your Render URL looks like: https://my-app.onrender.com/analyze
    API_URL = "https://ml-engine-backend.onrender.com/analyze"
    
    try:
        json_str = json.dumps(history_dict)
        compressed_payload = gzip.compress(json_str.encode("utf-8"))
        
        # We increase timeout to 120s to account for the "Cold Start" spin-up
        response = requests.post(
            API_URL,
            data=compressed_payload,
            headers={
                "Content-Encoding": "gzip",
                "Content-Type": "application/json"
            },
            timeout=120 
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        return {"error": "Server is taking too long to wake up. Please try again in 30 seconds."}
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}


def build_payload():
    if not os.path.exists(HISTORY_FILE):
        raise FileNotFoundError("No monitoring data found. Please run monitoring before upload.")
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    # 1. DATA SUFFICIENCY CHECK
    recent_count = len(history.get("data", {}).get("recent_samples", []))
    agg_count = len(history.get("data", {}).get("aggregates", []))

    if recent_count < 50 or agg_count < 5:
        # This string will appear in your PyQt QMessageBox
        raise ValueError(
            f"Insufficient data (Samples: {recent_count}/50, Aggs: {agg_count}/5). "
            f"Please let monitoring continue for {(5-agg_count)*5} mins minimum before upload."
        )

    # 2. RUN ANALYTIC ENGINE
    # The engine expects a JSON string, so we dump the history dict
    analysis_summary = get_cloud_analysis(history)

    # 3. CONSTRUCT FINAL PAYLOAD
    return {
        "user_email": load_email(),
        "raw_data": history,
        "summary": analysis_summary, # The AI results & 15 forecast samples
        "device_name": socket.gethostname(),
        "os": platform.system(),
        "source": "desktop_app",
        "status": "pending"
    }

