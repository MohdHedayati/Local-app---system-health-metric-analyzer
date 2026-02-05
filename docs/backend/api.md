# API & Security Architecture

In a traditional web application, developers manually write API endpoints (e.g., creating a Python function for `/get-users`).

This project adopts a **Serverless / Backend-as-a-Service (BaaS)** architecture using **Supabase**. Instead of a custom middleware server, Supabase automatically generates a high-performance **REST API** and **WebSocket** layer directly from our PostgreSQL database schema.

---

## 🔌 The Auto-Generated API (PostgREST)

The core API layer is powered by **PostgREST**. This tool turns the database tables directly into RESTful endpoints.

* **Database Table:** `public.system_metrics`
* **Auto-Generated Endpoint:** `https://[project-ref].supabase.co/rest/v1/system_metrics`

This means that as soon as we define a new table in the database, the API is instantly ready to accept data from the Desktop Agent or serve data to the Web Dashboard. No extra deployment code is required.

### Supported Operations
The API supports standard HTTP verbs mapped to database actions:
* **GET:** Read telemetry (Select).
* **POST:** Upload new reports (Insert).
* **PATCH:** Update user settings (Update).
* **DELETE:** Clear old logs (Delete).

---

## ⚡ Real-Time API (WebSockets)

Beyond standard request/response cycles, the platform utilizes **Real-Time Subscriptions**.

The Desktop Agent writes to the database, and Supabase broadcasts these changes via WebSockets to any connected Web Dashboard clients. This allows the dashboard to update graphs **instantly** without needing to refresh the page or poll the server every few seconds.

**Key Use Case:**
> If the Desktop Agent detects a temperature spike (>90°C), it writes a row to the `alerts` table. The Web Dashboard, subscribed to `alerts`, receives this event in milliseconds and triggers a visual warning.

---

## 🛡 Security Architecture

Since the API URL is public and exposed to the internet, security is not handled by hiding the API, but by **authorizing the data**.

### 1. JSON Web Tokens (JWT)
Every request made to the API must include a valid **Bearer Token**.
* **Authentication:** When a user logs in via Google OAuth, they receive a JWT.
* **Transport:** This token is sent in the header of every HTTP request (`Authorization: Bearer <token>`).
* **Verification:** Supabase verifies the signature of the token to ensure it hasn't been forged.

### 2. Row Level Security (RLS)
This is the firewall of our database. Even if a hacker has a valid API token, RLS restricts what they can touch.

* **The Rule:** `auth.uid() = user_id`
* **The Effect:** A user can only run `SELECT`, `INSERT`, `UPDATE`, or `DELETE` on rows that contain their specific User ID.

### 3. API Gateway Protection
Supabase places an API Gateway (Kong) in front of the database to handle:
* **Rate Limiting:** Preventing a malfunctioning Desktop Agent from spamming the server with millions of requests.
* **DDoS Protection:** Filtering out malicious traffic.
* **SSL/TLS:** Enforcing encrypted connections (HTTPS) for all data in transit.

---

## 🔑 Service Role Access

While the Desktop App and Web Dashboard use restricted "User Keys" (public), the backend administrative scripts use a **Service Role Key** (private).

* **Public Key (Anon):** Safe to embed in the PyQt5 app and Streamlit code. Restricted by RLS.
* **Service Key (Admin):** Bypasses all RLS rules. Used only for background maintenance tasks (like training ML models on aggregate data) running in a secure, isolated server environment.