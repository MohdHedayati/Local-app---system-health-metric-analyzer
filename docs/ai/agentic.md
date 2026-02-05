# Agentic AI Engine

The **Agentic AI Engine** is the autonomous reasoning core of the platform. While the Generative AI component handles language and communication, the Agentic Engine is responsible for **taking action** and **solving problems**.

It transforms the system from a passive monitoring tool into an active "Virtual System Administrator" that can investigate root causes on its own.

---

## 🧠 The ReAct Paradigm

The engine is built upon the **ReAct (Reason + Act)** pattern. Instead of immediately trying to guess an answer, the AI enters a reasoning loop:

1.  **Thought:** The agent analyzes the user's request to understand the intent.
2.  **Action:** It selects a specific tool from its toolkit to gather evidence.
3.  **Observation:** It reads the output of that tool (e.g., a database query result).
4.  **Synthesis:** It combines the observation with its internal knowledge to form a conclusion.

If the first observation isn't enough, it repeats the loop until it solves the problem.

---

## 🛠 The Agent's Toolbelt

For an AI to be "Agentic," it must have hands. In this architecture, "hands" are Python functions (Tools) that the LLM is allowed to execute.

| Tool Name | Purpose | Example Trigger |
| :--- | :--- | :--- |
| **`MetricRetriever`** | Queries Supabase for raw telemetry data (CPU, RAM, Disk). | *"Check if the CPU was high 10 mins ago."* |
| **`VectorSearch`** | Queries the RAG system for documentation and fixes. | *"How do I fix error 0x8004?"* |
| **`LogInspector`** | (Planned) Fetches specific error logs from the OS. | *"Check the system event logs."* |
| **`AnomalyChecker`** | Retrieves flags set by the Neural Network. | *"Did the ML model detect anything?"* |

---

## 🕵️ Example Investigation Workflow

**User Query:** *"Why is my internet so slow?"*

**Step 1: Thought**
> "The user is reporting network issues. I need to check if the network interface is saturated or if there are errors."

**Step 2: Action**
> *Calls `MetricRetriever.get_network_stats(duration="30m")`*

**Step 3: Observation**
> *Result: { "download_speed": "0.5 MB/s", "packet_drop_rate": "15%" }*

**Step 4: Thought**
> "Download speed is low, but the packet drop rate is very high (15%). This usually indicates a bad Wi-Fi signal or a faulty cable, not just congestion."

**Step 5: Final Response**
> "I checked your network stats for the last 30 minutes. While your speed is low (0.5 MB/s), the main issue is a **15% packet drop rate**. This suggests a physical hardware issue (like a bad cable) or poor Wi-Fi reception, rather than just a slow ISP connection."

---

## 🛡 Safety & Guardrails

To prevent the agent from hallucinating or executing dangerous commands, strict guardrails are enforced:

* **Read-Only Access:** Currently, the agent can *read* system data but cannot *execute* system commands (like `rm -rf` or `shutdown`).
* **Scoped Queries:** Database queries are strictly scoped to the authenticated user's ID.
* **Confidence Thresholds:** If the agent is unsure, it is programmed to ask for clarification rather than guessing.

---

## 🚀 Why This Matters

Standard LLMs (like ChatGPT) cannot see your computer's screen or internal state. They can only offer generic advice.

By giving the LLM **tools** to look at your actual `psutil` data, the Agentic Engine bridges the gap between **general knowledge** and **specific reality**, providing diagnostics that are actually relevant to your machine's current situation.