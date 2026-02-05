# Security & Privacy

Building a system that monitors hardware and process activity requires a high level of trust. We approach security with a **"Privacy by Design"** philosophy, ensuring that user data is encrypted, isolated, and strictly scoped.

This document outlines the security measures implemented across the Desktop Agent, Cloud Backend, and AI Pipelines.

---

## 🛡️ Data Collection Policy

We believe in **Data Minimization**. We collect only the telemetry necessary to diagnose system health.

### ✅ What We Collect
* **Performance Metrics:** CPU load, RAM usage, Temperatures, Fan speeds.
* **Hardware Signatures:** CPU model name, Total Memory, Disk capacity (to create a "baseline" for the AI).
* **Process Statistics:** Resource consumption of running applications (e.g., "chrome.exe uses 2GB RAM").
* **Anomalies:** Events flagged by the ML engine (e.g., "High Thermal Event").

### ❌ What We Do NOT Collect
* **Keystrokes:** The agent has no keylogging capabilities.
* **File Contents:** We scan disk *usage* (I/O rates), but we never read or upload the contents of your documents.
* **Browser History:** We monitor network traffic volume, not the websites you visit.
* **Screen Content:** The application never takes screenshots.

---

## 🔐 Architecture Security Layers

We employ a "Defense in Depth" strategy, securing the data at every stage of its lifecycle.

### 1. Security in Transit (Encryption)
All communication between the Desktop Agent, the Web Dashboard, and the Cloud Backend occurs over **HTTPS (TLS 1.2/1.3)**.
* **Certificate Pinning:** The desktop agent validates SSL certificates to prevent Man-in-the-Middle (MITM) attacks.
* **No Plaintext:** API keys and Tokens are never sent in the URL parameters; they are passed strictly in HTTP Headers.

### 2. Security at Rest (Database)
Data stored in Supabase is encrypted using **AES-256** (Advanced Encryption Standard).
* **Row Level Security (RLS):** As detailed in the backend documentation, the database engine itself enforces strict isolation. A user with ID `A` cannot query the rows belonging to User `B`, even if they manage to send a custom SQL query.

### 3. Desktop Security
* **Token Storage:** OAuth Refresh Tokens are stored using the operating system's native secure vault (Windows Credential Manager / Linux Keyring) via the `keyring` Python library. They are never saved in plain text files.
* **Report Signing:** Before uploading, the desktop agent signs the JSON payload with a hash. This ensures that the data received by the cloud hasn't been tampered with by malware on the local machine.

---

## 🤖 AI & Privacy

Integrating Generative AI introduces new privacy questions. Here is how we handle them:

### No Public Training
Your specific system logs are **NOT** used to train public models (like generic ChatGPT).
* **Context Injection:** We use RAG (Retrieval-Augmented Generation). Your data is sent to the LLM *only* during your active chat session to provide context, and is then discarded from the model's short-term memory.
* **Anonymized Aggregation:** The *internal* Neural Networks (for anomaly detection) are trained on aggregated, anonymized datasets where all user identifiers and specific file paths have been stripped out.

---

## 👤 User Control (GDPR/CCPA)

Users retain full ownership of their data. Through the Web Dashboard settings, users can execute the following actions:

1.  **Purge History:** Delete all historical telemetry logs immediately.
2.  **Unlink Device:** Revoke access for a specific desktop agent.
3.  **Download Data:** Export all stored metrics in JSON/CSV format.

---

## 🐛 Vulnerability Reporting

Security is an ongoing process. If you discover a vulnerability in the Desktop Agent or API, please open a strictly confidential issue on our GitHub repository using the "Security Advisory" tag.