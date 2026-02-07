# System Health Metric Analyzer - Desktop Agent (Windows)

**Version 2.0**

This is the standard Windows implementation of the Desktop Agent.

> **Note:** This version utilizes **Render.com** to host the ONNX models for cloud-based inference. This architecture keeps the local client lightweight and reduces dependency on local hardware resources.

## 📥 User Guide
To download the executable installer (`.exe`) or the portable ZIP version, please visit the **[Releases Page](../../releases)**.

## 🛠 Developer Guide

If you wish to run the source code or contribute, follow these steps.

### 1. Installation
```bash
# Clone the Windows branch
git clone -b main [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)

# Create Virtual Environment (Verified on Python 3.12.0)
python -m venv venv 
# Activate venv: .\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Run the Application
cd PyQt5
python app.py
```

### 2. Configuration Secrets (Crucial)
The application will not start without API credentials. You must create a data folder inside the PyQt5 directory and add the following two JSON files:

```File Structure:

Plaintext
PyQt5/
├── app.py
├── data/
│   ├── client_secrets.json
│   └── supabase_secrets.json
```

## A. PyQt5/data/client_secrets.json (Google OAuth)
Get this from your Google Cloud Console. It should look like this:

```JSON
{
  "installed": {
    "client_id": "35809.....apps.googleusercontent.com",
    "project_id": "sodium-primer-48...",
    "auth_uri": "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)",
    "token_uri": "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)",
    "auth_provider_x509_cert_url": "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)",
    "client_secret": "GOCS...",
    "redirect_uris": ["http://localhost"]
  }
}
```

## B. PyQt5/data/supabase_secrets.json (Database)
Get this from your Supabase Project Settings.

```JSON
{
    "PROJECT_URL": "[https://bozt....supabase.co](https://bozt....supabase.co)",
    "service_role_key": "eyJhbG....."
}
```