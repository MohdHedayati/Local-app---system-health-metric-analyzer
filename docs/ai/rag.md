# RAG & Vector Database

**Retrieval-Augmented Generation (RAG)** is the mechanism that gives the Generative AI "textbooks" to study from. Without RAG, an AI only knows what it learned during its initial training (which might be months old).

With RAG, we can dynamically feed the AI up-to-date documentation, specific error code dictionaries, and platform-specific troubleshooting guides. This ensures that when the AI suggests a fix for an "Arch Linux" update error, it uses the correct `pacman` commands, not `apt-get`.

---

## 📚 Why RAG is Essential

In a technical diagnostics system, **accuracy is paramount**.

* **The Hallucination Problem:** If you ask a standard LLM about a specific error code, it might guess.
* **The Solution:** RAG forces the LLM to look up the answer in a trusted "Knowledge Base" first, then answer using *only* that retrieved information.

---

## 🏗 Architecture Pipeline

The RAG system operates in two distinct phases: **Ingestion** (Learning) and **Retrieval** (Answering).

### Phase 1: Ingestion (Building the Knowledge Base)
We collect high-quality technical documentation and prepare it for the AI.

1.  **Sourcing:** We scrape reliable sources (Microsoft Learn, Arch Wiki, Ubuntu Manpages).
2.  **Chunking:** Large documents are split into smaller paragraphs (e.g., 500 characters).
3.  **Embedding:** An Embedding Model (like OpenAI `text-embedding-3-small`) converts these text chunks into **Vectors** (lists of floating-point numbers) that represent their *meaning*.
4.  **Storage:** These vectors are stored in **Supabase** using the `pgvector` extension.

### Phase 2: Retrieval (The Search)
When a user asks a question:

1.  **Query Embedding:** The user's question is converted into a vector.
2.  **Semantic Search:** We query the database for the "closest" vectors (using Cosine Similarity). This finds documents that *mean* the same thing, even if they use different keywords.
3.  **Augmentation:** The top 3 matching documents are pasted into the prompt sent to the LLM.

---

## 💾 The Vector Store (Supabase pgvector)

We utilize **PostgreSQL** with the `pgvector` extension as our Vector Database. This simplifies the architecture significantly.

Instead of needing a separate database (like Pinecone or Weaviate), our vectors live right alongside our user data and telemetry logs. This allows us to perform "Hybrid Searches"—filtering by both meaning *and* metadata (e.g., "Search for 'Blue Screen' fixes, but only in the 'Windows 11' documentation").

---

## 🛠 Integration with the Agent

The RAG system functions as a **Tool** for the Agentic AI.

* **Scenario:** User asks *"What does error 0x80070005 mean?"*
* **Action:** The Agent realizes it doesn't know this specific code.
* **Tool Use:** It calls the `VectorSearch` tool.
* **Result:** The system retrieves the official Microsoft documentation for "Access Denied" errors.
* **Response:** The AI explains the error and suggests checking file permissions, citing the official source.

---

## 🎯 Benefits for Device Health

1.  **OS Awareness:** The system creates separate "knowledge partitions" for Windows, Ubuntu, and Arch, preventing command confusion.
2.  **Updatability:** If a new Windows update causes a new bug, we can simply add the new documentation to the database. The AI becomes "smarter" instantly, without needing to be retrained.
3.  **Traceability:** The AI can cite its sources (e.g., *"According to the Arch Wiki..."*), increasing user trust.