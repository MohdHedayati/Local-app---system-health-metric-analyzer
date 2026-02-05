# Iterations & Improvements

No software is perfect in version 1.0. This project underwent significant refactoring as we encountered real-world bottlenecks. Below are the key technical pivots that defined the current architecture.

---

## 🔄 Pivot 1: From Polling to Event-Driven
**The Problem:**
Initially, the Desktop App used a `while True:` loop with `time.sleep(1)`.
* **Issue:** This blocked the Main UI thread. If the network request to the database took 2 seconds, the entire window would freeze, becoming unresponsive to clicks.

**The Fix:**
We rewrote the core engine using **PyQt5 `QThread` and Signals**.
* Now, the "Worker Thread" handles the heavy lifting (`psutil` + Network I/O).
* It emits a `data_ready` signal.
* The "Main Thread" catches the signal and updates the UI.
* **Result:** A buttery smooth 60 FPS interface, even during heavy data uploads.

---

## 🔄 Pivot 2: From Local SQLite to Cloud Supabase
**The Problem:**
Version 1 stored data in a local `data.db` (SQLite) file.
* **Issue:** Users could only see data if they were physically sitting at that specific computer. There was no "remote monitoring" capability.

**The Fix:**
We migrated to **Supabase (PostgreSQL)**.
* This introduced the complexity of network latency and offline handling.
* We added a **Local Buffer**: If the internet cuts out, the app saves reports to a temporary local file and batch-uploads them when the connection returns.

---

## 🔄 Pivot 3: From Hardcoded Auth to OAuth
**The Problem:**
Early versions required users to manually copy-paste a "Device Key" from the website to the desktop app `config.json`.
* **Issue:** It was user-unfriendly and insecure. If a key was stolen, anyone could flood the database.

**The Fix:**
We implemented **Google OAuth 2.0 with PKCE**.
* This required building a local HTTP server in Python to capture the browser redirect.
* **Result:** A seamless "Sign in with Google" button that securely identifies the user without manual key management.

---

## 🔄 Pivot 4: From Basic Chatbot to Agentic AI
**The Problem:**
The first chatbot integration was just a wrapper around GPT-3.5.
* **Issue:** If asked "Why is my PC slow?", it would give generic advice like "Check Task Manager." It couldn't *see* the actual data.

**The Fix:**
We moved to an **Agentic RAG Architecture**.
* We gave the LLM "Tools" (Python functions) to query the database.
* **Result:** Now, the AI proactively looks at the RAM usage *before* answering, providing specific advice based on the actual telemetry.