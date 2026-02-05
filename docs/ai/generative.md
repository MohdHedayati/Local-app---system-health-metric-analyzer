# Generative AI Pipeline

While the **Agentic Engine** handles reasoning and logic, the **Generative AI Pipeline** is responsible for **communication**. It acts as the "Translator" between the cold, binary world of system logs and the natural language needed by the user.

Its primary goal is to turn complex JSON objects (like `cpu_load: 0.82`) into meaningful explanations (e.g., *"Your processor is under heavy load, likely due to a background update"*).

---

## 🗣 The Role of the LLM

In this architecture, the Large Language Model (LLM) serves three specific functions:

1.  **Summarization:** Taking 500 rows of system logs and condensing them into a single, digestible paragraph.
2.  **Translation:** converting technical error codes (e.g., `0x80040154`) into plain English descriptions.
3.  **Tone Calibration:** Adjusting the complexity of the explanation based on who is asking (e.g., explaining a crash simply to a casual user vs. providing technical details to a developer).

---

## 📝 Prompt Engineering Strategy

To ensure the AI behaves like a reliable Systems Administrator rather than a creative writer, we utilize strict **System Prompts**.

These prompts "program" the behavior of the model before the user ever asks a question.

### The "SysAdmin" Persona
A typical System Message injected into the context looks like this:

> "You are an expert Systems Reliability Engineer. You are analyzing a Windows 11 machine.
>
> **Rules:**
> 1. Be concise and professional.
> 2. Base your answers ONLY on the provided telemetry context.
> 3. If the data is missing, admit it. Do not hallucinate metrics.
> 4. When suggesting fixes, prioritize non-destructive actions first."

By anchoring the model with these rules, we significantly reduce the chance of "hallucinations" (the AI making up facts).

---

## 📄 Context Management

Generative AI models have a **Context Window** (a limit on how much text they can read at once). Sending a full day's worth of raw logs would overflow this limit immediately.

To handle this, the pipeline implements **Intelligent Context pruning**:

1.  **JSON Minimization:** Removing redundant keys from the telemetry data to save tokens.
2.  **Time-Slicing:** Only feeding the model data relevant to the user's query time range (e.g., the exact 5-minute window where the crash happened).
3.  **Key-Event Filtering:** Prioritizing "Critical" and "Warning" logs over "Info" logs.

---

## 🔗 Model Integration

The platform is designed to be model-agnostic, connecting via standard API protocols.

* **Primary Logic:** We use high-intelligence models (like GPT-4 or Claude 3.5 Sonnet) for complex reasoning tasks.
* **Fast Response:** We use lightweight, fast models (like GPT-4o-mini or Gemini Flash) for quick summaries and chat interactions to keep the dashboard snappy.

---

## ⚖️ Generative vs. Agentic vs. ML

It is important to distinguish the three AI pillars in this project:

| Component | Role | Example |
| :--- | :--- | :--- |
| **Generative AI** | **The Voice.** Writes the text and explains the data. | *"Your CPU is hot because Chrome is open."* |
| **Agentic AI** | **The Brain.** Decides which tools to use. | *Decides to fetch CPU data from the DB.* |
| **Machine Learning** | **The Eyes.** Detects patterns in raw numbers. | *Flags a temperature of 95°C as an anomaly.* |