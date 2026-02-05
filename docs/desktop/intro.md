# Desktop System Agent

The **Desktop System Agent** is a standalone client-side application built with **PyQt5**. It serves as the primary data collection and local intelligence node for the System Health AI platform.

Unlike web-based monitoring tools that are restricted by browser sandboxing, this native application has direct access to low-level system APIs, allowing it to gather high-fidelity telemetry and perform real-time hardware analysis.

---

## 🎯 Core Responsibilities

The Desktop Agent is designed to fulfill three critical roles:

1. **Telemetry Collection**
   Using `psutil` and platform-specific drivers to harvest granular metrics (CPU cycles, thermal zones, memory pages) that browsers cannot access.

2. **Edge Intelligence (Local ML)**
   Running lightweight neural networks locally to detect anomalies in real-time. This reduces cloud latency and ensures that critical alerts are generated even if the internet connection is unstable.

3. **Secure Synchronization**
   Acting as a secure bridge between the user's hardware and the Supabase cloud backend, ensuring all data is authenticated via Google OAuth before upload.

---

## 🏗 Architecture & Tech Stack

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **GUI Framework** | PyQt5 | Robust, cross-platform (Windows/Linux), and natively integrates with Python's data science stack. |
| **Metrics Engine** | `psutil` | Industry standard for cross-platform hardware monitoring. |
| **Network Layer** | `requests` / Supabase | Handles secure REST API calls and real-time database synchronization. |
| **Concurrency** | `QThread` | Ensures the UI remains responsive while heavy data collection runs in the background. |

---

## 🔄 Application Workflow

When the user launches the Desktop Agent, the following lifecycle executes:

1. **Initialization:** The app checks for local configuration files and validates the internet connection.
2. **Authentication:** A Google OAuth window opens. Upon success, a secure session token is cached.
3. **Monitoring Loop:**
    * **Fetch:** `psutil` queries hardware sensors.
    * **Analyze:** The local ML engine scores the data frame for anomalies.
    * **Visualize:** Real-time graphs update on the desktop UI.
4. **Reporting:** Every *N* seconds (configurable), a structured JSON report is cryptographically signed and uploaded to the Supabase backend.

---

## 🖥 User Interface Design

The application is designed to be unobtrusive.

* **Main Dashboard:** Displays a "Health Score" speedometer and live sparklines for CPU/RAM.
* **Status Bar:** Shows connectivity status to the Cloud Brain.
* **System Tray:** The app can minimize to the tray to run silently in the background, only notifying the user via toast notifications if an anomaly (e.g., thermal throttling) is detected.

---

## 🚀 Why a Desktop App?

Web browsers are sandboxed for security. They cannot read your CPU temperature or see exactly which process is eating your RAM.

By running a native **PyQt5** application, we bridge the gap between **hardware visibility** and **cloud intelligence**, enabling the Agentic AI to "see" exactly what is happening on your machine.