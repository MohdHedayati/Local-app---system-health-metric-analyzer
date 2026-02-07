# System Health AI - Desktop Agent (Linux)

**Version 2.0**

This is the native Linux implementation of the System Health AI Desktop Agent.

> **Note:** Unlike the Windows version, this edition runs **ONNX models locally** on your device. This ensures maximum privacy and allows for offline anomaly detection without external API calls to Render.com.

## 📥 User Guide
To download the Linux binaries (AppImage/Deb), please visit the **[Releases Page](../../releases)**.

## 🛠 Developer Guide

If you wish to run the source code or contribute, follow these steps.

### 1. Installation
```bash
# Clone the Linux branch specifically
git clone -b PyQtApp-Linux [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)

# Create Virtual Environment (Verified on Python 3.12.0)
python -m venv venv 
# Activate venv: source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run the Application
cd PyQt5
python app.py 
2. Configuration Secrets (Crucial)
You must create a data folder inside the PyQt5 directory and add the following two JSON files:
```

```File Structure:

PyQt5/
├── app.py
├── data/
│   ├── client_secrets.json
│   └── supabase_secrets.json
```

## A. PyQt5/data/client_secrets.json (Google OAuth)

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

```JSON
{
    "PROJECT_URL": "[https://bozt....supabase.co](https://bozt....supabase.co)",
    "service_role_key": "eyJhbG....."
}
```

**Push the changes:**
```bash
git add README.md LICENSE.md
git commit -m "Update docs for Linux Agent v2.0"
git push origin PyQtApp-Linux
```