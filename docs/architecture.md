# System Architecture

## High-Level Flow

1. User authenticates via Google OAuth in the desktop app
2. System metrics are collected using `psutil`
3. A structured health report is generated locally
4. Report is uploaded securely to Supabase
5. User logs into the web dashboard to view reports
6. AI chatbot uses RAG to answer system-related questions

## Components

### Desktop Client (PyQt5)
- UI and user interaction
- OAuth authentication
- Local data collection
- Report generation

### Backend (Supabase)
- User authentication mapping
- Report storage
- Secure API access

### AI Layer
- LLM-based chatbot
- RAG context per operating system
- Diagnostic reasoning on system metrics
