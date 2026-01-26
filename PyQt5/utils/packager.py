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

import torch
from ml_engine.scripts.analytic_engine import SystemAnalyticEngine

# Initialize engine once to save VRAM; or init inside build_payload if preferred
# Note: Ensure models are already trained and in /models/
engine = SystemAnalyticEngine()

def build_payload():
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
    analysis_summary = engine.analyze_packet(json.dumps(history))

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

