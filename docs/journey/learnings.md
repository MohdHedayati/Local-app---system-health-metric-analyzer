# Project Learnings

Building a distributed, AI-powered system provided deep insights into full-stack development, system-level programming, and AI orchestration. This project was not just about connecting libraries; it was about managing complexity across different environments (Desktop, Web, and Cloud).

---

## 🧠 Technical Takeaways

### 1. The "Main Thread" Rule (PyQt5)
One of the earliest and hardest lessons was understanding the GUI Event Loop.
* **The Mistake:** Running `psutil` queries or network requests directly inside the button click function.
* **The Consequence:** The application window would "freeze" and become unresponsive while waiting for the server.
* **The Lesson:** We learned to religiously use `QThread` and `pyqtSignal`. Keep the UI thread purely for rendering, and offload *everything* else to background workers.

### 2. The Stateless Web (Streamlit)
Coming from desktop development, Streamlit's execution model was a paradigm shift.
* **The Challenge:** Streamlit reruns the entire Python script from top to bottom every time a user interacts with a widget.
* **The Lesson:** We mastered `st.session_state` to persist data (like chat history and auth tokens) across these reruns. Without this, the user would be logged out every time they clicked a button.

### 3. Context Windows are Precious (AI)
We initially thought we could just "feed the logs to the AI."
* **The Reality:** LLMs have token limits, and API calls are priced by the token. Sending 24 hours of raw JSON logs is prohibitively expensive and confusing for the model.
* **The Lesson:** **Data Aggregation is key.** We built pre-processing logic to summarize 1,000 data points into a concise "Health Snapshot" before the AI ever sees it.

---

## 🛡 Security & Architecture

### 1. Row Level Security (RLS) > API Logic
In early prototypes, we tried to filter data in the Python code (`if user.id == row.user_id`).
* **The Risk:** It is too easy to make a mistake and leak data.
* **The Lesson:** Pushing security down to the database layer (Supabase RLS) is safer. If the database engine enforces the rules, the frontend code can be simpler and less fragile.

### 2. OAuth on Desktop is Hard
Implementing "Log in with Google" on a website is standard. Doing it in a standalone desktop app is complex.
* **The Lesson:** We learned about the **PKCE (Proof Key for Code Exchange)** flow and how to spin up ephemeral local socket servers to capture redirect tokens securely.

---

## 📈 Product Philosophy

### Data != Insight
The biggest realization was that **users do not care about raw numbers**.
* **Initial Thought:** "Let's show them a cool graph of CPU interrupt requests."
* **User Feedback:** "Is my computer okay?"
* **The Pivot:** We shifted focus from "Monitoring" (showing data) to "Diagnostics" (explaining data). This drove the decision to integrate the Agentic AI to translate the graphs into plain English.