# Supabase Architecture

The backend infrastructure of System Health AI is built entirely on **Supabase**, an open-source Backend-as-a-Service (BaaS) platform.

By choosing Supabase, we replace the complexity of managing separate servers (e.g., an AWS EC2 instance for the API, an RDS instance for the database, and a separate Auth0 service for login) with a single, unified ecosystem built on top of **PostgreSQL**.

---

## 🏗 The Stack Components

Supabase is not just a database; it is a suite of tools that wraps the database. We utilize five key components:

### 1. PostgreSQL (The Core)
Everything in Supabase starts with the database. Unlike NoSQL solutions (like Firebase), Supabase offers a full relational SQL environment.
* **Role:** Stores User Profiles, Device Metadata, and Telemetry.
* **Extensions:** We enable `pgvector` for AI memory and `pg_cron` for automated data cleanup.

### 2. GoTrue (Authentication)
This service manages users and issues JWTs (JSON Web Tokens).
* **Role:** Handles the Google OAuth handshake for both the Desktop App and Web Dashboard.
* **Benefit:** It unifies the identity. A user logged into the PyQt5 app has the exact same User ID (UUID) as the user on the Streamlit web app.

### 3. PostgREST (The API Layer)
As detailed in the API section, this service automatically turns our SQL tables into a secure REST API.
* **Role:** Allows the Desktop Agent to upload JSON reports via standard HTTP POST requests without us writing a single line of backend API code.

### 4. Realtime (WebSockets)
This service listens to the PostgreSQL Write-Ahead Log (WAL).
* **Role:** Pushes updates to the Web Dashboard instantly.
* **Scenario:** If the Desktop Agent writes a "Critical Thermal Warning" to the database, the Realtime engine instantly pushes that event to the open Web Dashboard, triggering an alert UI.

### 5. Edge Functions (Serverless Compute)
* **Role:** Runs custom TypeScript code triggered by database events.
* **Use Case:** We use Edge Functions to sanitize data or trigger external webhooks when a specific anomaly threshold is breached.

---

## 🔄 The "Glue" Architecture

Supabase acts as the bridge between the two distinct halves of our project:

1.  **The "Writer" (Desktop Agent):**
    * Connects via the **REST API**.
    * Focuses on *Ingestion* (High-frequency writes).
    * Authenticated via Device/User Tokens.

2.  **The "Reader" (Web Dashboard):**
    * Connects via the **Supabase Python SDK**.
    * Focuses on *Querying* and *Analysis*.
    * Uses **Vector Search** for RAG operations.

---

## 🚀 Why Supabase?

### vs. AWS/Google Cloud
Setting up an equivalent stack on AWS would require configuring RDS, Lambda, API Gateway, Cognito, and Kinesis. Supabase provides all of this out-of-the-box, allowing us to focus on the AI/ML logic rather than DevOps.

### vs. Firebase
While Firebase is popular, it is a NoSQL document store.
* **SQL Power:** System monitoring data is highly structured (time-series). SQL is much better suited for querying "Average CPU usage over the last 7 days" than a NoSQL document store.
* **Vector Support:** Firebase does not natively support Vector Embeddings for AI. Supabase's `pgvector` makes it an all-in-one solution for our Generative AI needs.

---

## 🌍 Scalability

The architecture is designed to scale horizontally.
* **Connection Pooling:** Supabase (via Supavisor) manages thousands of simultaneous connections from desktop agents without crashing the database.
* **Partitioning:** As data grows, we can partition the `system_metrics` table by time (e.g., one partition per month) to keep queries fast.