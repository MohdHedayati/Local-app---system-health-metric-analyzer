# AI Chatbot Interface

The **AI Chatbot** is the primary interface for the "Agentic AI" system. Unlike generic chatbots (like ChatGPT) that rely solely on pre-trained knowledge, this agent is **context-aware**. It possesses direct access to the user's specific hardware telemetry, allowing it to act as a personalized Systems Administrator.

---

## 🤖 The "Agentic" Difference

Traditional chatbots answer questions based on general knowledge. Our **Diagnostics Agent** operates differently by utilizing a reasoning loop:

1.  **Observe:** The agent listens to the user's query (e.g., *"Why is my system lagging?"*).
2.  **Investigate:** It autonomously decides to look up the latest system data from the database.
3.  **Analyze:** It compares current metrics against healthy baselines to detect anomalies (like high RAM usage).
4.  **Respond:** It provides an answer grounded in the specific facts it just discovered.

---

## 🏗 Architecture: The RAG + Context Pipeline

The chatbot is built on a hybrid architecture combining **Retrieval-Augmented Generation (RAG)** and **Dynamic Context Injection**.

### 1. Dynamic Context Injection (Short-Term Memory)
Before the AI generates a single word, the system "injects" a snapshot of the computer's current health into the conversation. The AI immediately knows the CPU model, current temperature, and memory load without the user having to explain it.

### 2. RAG Knowledge Base (Long-Term Memory)
When the agent encounters specific error codes or symptoms, it queries a Vector Database containing:
* OS-specific troubleshooting guides (Windows/Linux).
* Hardware thermal limits documentation.
* Common software conflict resolutions.

---

## 💻 User Interface Experience

The interface is designed to feel like a standard messaging app.

* **Session History:** The chat history is saved, allowing the user to refresh the page without losing the context of the diagnosis.
* **Streaming Responses:** Answers appear incrementally (like a typewriter) to keep the interaction feeling responsive and alive.

---

## 🛠 Capabilities & Tools

The Agent is equipped with specific "Tools"—functions that allow it to interact with the system data:

* **Fetch Current Metrics:** Allows the AI to see the exact state of the hardware *right now*.
* **Check Historical Trends:** The AI can look back in time to see if a problem (like overheating) has been happening all day.
* **Search Knowledge Base:** Used to find specific solutions for complex error messages.

---

## 🧩 Example Conversation Flow

**User:** "My computer feels slow."

**Agent's Internal Process:**
The agent checks the latest report and sees that Disk I/O is running at 100% capacity, while CPU and RAM are normal. It also notices a background virus scan process is active.

**Agent Response:**
"Your CPU and RAM usage are actually normal, but your Disk usage is extremely high right now. It looks like a background security scan is running, which is likely causing the slowdown. It should resolve once the scan finishes."