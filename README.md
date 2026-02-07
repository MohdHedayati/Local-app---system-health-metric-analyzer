# System Health AI - Experimental (Torch)

**Version 2.0 - Experimental**

This is the heavy-weight research version of the Desktop Agent using **PyTorch**.

> **Note:** Unlike the standard versions which use optimized ONNX models, this version loads raw **PyTorch (`.pth`) models**. It is an experimental branch designed for future scalability and is intended to be run on powerful cloud computing instances with dedicated GPUs. It has a significantly larger footprint.

## 🛠 Developer Guide

### 1. Installation
```bash
# Clone this specific experimental branch
git clone -b PyQt-app-torch-heavy-version [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)

# Create Virtual Environment (Verified on Python 3.12.0)
python -m venv venv 
# Activate venv: source venv/bin/activate

# Install Dependencies (Includes heavy torch libraries)
pip install -r requirements.txt

# Run the Application
cd PyQt5
python app.py 
2. Configuration Secrets
To launch the application, you must provide the standard API credentials in the PyQt5/data directory.
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
git commit -m "Update docs for Torch Experimental branch"
git push origin PyQt-app-torch-heavy-version
```