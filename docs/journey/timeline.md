# Project Timeline

The development of **System Health AI** was not a straight line; it was an iterative evolution. What started as a simple curiosity—*"How do I get my CPU usage using Python?"*—expanded layer by layer into the full-stack agentic platform it is today.

---

## 📅 Phase 1: The "Script" Era
**Focus: Raw Data Extraction**

The project began as a standalone Python script running in a terminal.
* **Goal:** Learn how to access low-level hardware counters without C++.
* **Implementation:** A simple loop using `psutil` and `time.sleep(1)` that printed CPU and RAM stats to the console.
* **Limitation:** It was ephemeral. Once you closed the terminal, the data was gone. There was no history, no visualization, and no persistence.

---

## 📅 Phase 2: The Desktop Application
**Focus: Visualization & UX**

To make the tool usable, we needed a Graphical User Interface (GUI).
* **Tech Shift:** Adopted **PyQt5** to wrap the logic in a desktop window.
* **Feature:** Added real-time graphing using `pyqtgraph`.
* **Challenge:** The GUI would freeze during data collection.
* **Solution:** Implemented `QThread` to separate the heavy `psutil` queries from the UI rendering loop, creating a smooth, responsive experience.

---

## 📅 Phase 3: The Cloud Bridge
**Focus: Connectivity & Identity**

A monitoring tool is useless if you have to be *at* the computer to see it. We needed to send data off-device.
* **Backend:** Integrated **Supabase** (PostgreSQL) to store logs.
* **Identity:** Implemented **Google OAuth 2.0**.
* **The Hurdle:** Getting OAuth to work in a desktop app was difficult. We had to build a local socket server (`localhost`) to catch the browser redirect and capture the secure tokens.
* **Result:** The "Connected" status. The desktop app could now identify *who* was using it and securely upload encrypted JSON payloads to the cloud.

---

## 📅 Phase 4: The Web Dashboard
**Focus: Analytics & Accessibility**

With data flowing into the database, we needed a way to view it remotely.
* **Frontend:** Built a **Streamlit** web application.
* **Feature:** Created interactive time-series charts (Plotly) to visualize CPU load and Thermal spikes over 24-hour periods.
* **Impact:** Users could now check their home PC's health from their smartphone while away.

---

## 📅 Phase 5: Generative AI Integration
**Focus: Insight vs. Data**

We realized that users didn't want to read graphs; they wanted answers.
* **Integration:** Connected an LLM (Large Language Model) to the dashboard.
* **Feature:** Added a "Chat" interface.
* **Mechanism:** We engineered a pipeline to feed the *current* system metrics into the LLM's system prompt.
* **Result:** Instead of just showing "CPU: 99%", the app could now say: *"Your CPU is at 99%, which is unusual for this time of day."*

---

## 📅 Phase 6: Agentic AI & RAG (Current State)
**Focus: Autonomous Reasoning**

The current phase moves beyond simple observations to complex diagnostics.
* **RAG:** Implemented **Vector Search** (Supabase `pgvector`) to let the AI read documentation for specific error codes (Windows vs. Linux).
* **Agentic Workflow:** Transitioned from a simple "Chatbot" to an "Agent" that can use tools. The AI can now decide *on its own* to query historical data if it suspects a trend.
* **Neural Expansion:** The desktop app was updated to collect high-frequency training data, preparing the ground for the custom Neural Networks that will power the next generation of anomaly detection.

---

## 🚀 Future Horizons

The journey continues. The next steps involve moving from **Detection** to **Prediction** (using LSTMs) and eventually **Auto-Remediation** (allowing the agent to fix problems for you).