# Report Generation

The final responsibility of the Desktop Agent is to transform continuous raw telemetry into structured **System Health Reports**.

A "Report" in this ecosystem is not a PDF file (which is generated on the web side), but a **rich JSON Data Object** containing statistical aggregates, detected anomalies, and metadata. These objects act as the standardized communication protocol between the Local Device and the Cloud Brain.

---

## 📄 The Report Lifecycle

The generation process follows a "Session-Based" approach:

1.  **Session Start:** When the app launches, a unique `session_id` is generated.
2.  **Aggregation:** Data is collected every second, but sending every second of data to the cloud is inefficient. Instead, data is aggregated locally into **5-minute chunks** (or "Snapshots").
3.  **Structuring:** The raw metrics are calculated into statistical summaries (Min, Max, Avg, Variance).
4.  **Signing:** A cryptographic hash is generated to ensure data integrity during transit.
5.  **Dispatch:** The JSON object is securely uploaded to Supabase.

---

## 🧩 Report Data Structure

The report payload is designed to be highly queryable by the Streamlit Dashboard and the RAG Engine.

### JSON Schema

```json
{
  "report_id": "uuid-v4-generated",
  "session_id": "sess-timestamp-user",
  "timestamp": "2023-10-27T14:30:00Z",
  "device_metadata": {
    "hostname": "Desktop-01",
    "os": "Windows 10 Pro",
    "agent_version": "1.2.0"
  },
  "performance_summary": {
    "cpu": {
      "avg_load": 15.4,
      "peak_load": 88.2,
      "thermal_throttling_events": 0
    },
    "memory": {
      "avg_usage_gb": 8.4,
      "peak_usage_gb": 12.1,
      "swap_usage_percent": 2.1
    }
  },
  "detected_anomalies": [
    {
      "type": "HIGH_DISK_IO",
      "severity": "WARNING",
      "description": "Sustained write operations > 50MB/s for 2 minutes",
      "suspected_process": "explorer.exe"
    }
  ],
  "integrity_hash": "sha256-hash-string"
}
```

## 🛡️ Data Integrity
To prevent data tampering (e.g., malware trying to hide its tracks by modifying the report before upload), the agent implements a basic integrity check.

Before transmission, the JSON payload is hashed. On the server side (or when viewed in the web dashboard), this hash can be re-calculated to verify that the report was not altered in transit.

```Python
import hashlib
import json

def sign_report(report_data):
    """Generates a SHA-256 signature for the report payload."""
    payload_string = json.dumps(report_data, sort_keys=True).encode()
    return hashlib.sha256(payload_string).hexdigest()
```

## ☁️ Upload Mechanism
The upload process is handled by a separate worker thread to ensure the UI never hangs, even on slow networks.

Endpoint: Supabase Database (Table: system_reports)

Method: upsert (Update if exists, Insert if new)

Retry Logic: If the internet is down, reports are cached locally in a temporary SQLite database and bulk-uploaded once connectivity is restored.

### 🔗 Integration with Web Dashboard
Once the report lands in Supabase, it becomes immediately available to the Streamlit Web Dashboard.

Visualization: The Web App parses the performance_summary to draw historical graphs.

AI Analysis: The Agentic AI reads the detected_anomalies array. If it sees a "Critical" severity flag, it proactively triggers a diagnostic chat workflow for the user.