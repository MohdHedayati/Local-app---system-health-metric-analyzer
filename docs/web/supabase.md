# Supabase Backend (CRUD)

The Web Dashboard interacts with **Supabase** as its primary data source. While the Desktop Agent is responsible for *writing* telemetry to the cloud, the Web Dashboard is primarily responsible for *reading* and visualizing that data.

Supabase acts as the "Source of Truth" for the entire platform, utilizing a PostgreSQL database to store structured JSON reports, user profiles, and chat history.

---

## 🌉 The Data Bridge

The dashboard serves as a graphical interface for the underlying database. It performs standard CRUD (Create, Read, Update, Delete) operations to manage the user's session.

### Read Operations (Data Visualization)
When a user opens the analytics tab, the dashboard queries the database for historical records. To keep the application fast, it does not fetch *all* data at once. Instead, it filters data based on:

1.  **Time Range:** Only fetching metrics for the specific window selected by the user (e.g., "Last Hour" or "Last 24 Hours").
2.  **Device ID:** Ensuring metrics are only pulled for the specific machine currently being viewed.

### Create Operations (Chat History)
Every interaction with the AI Chatbot is persisted. When the user asks a question, both the user's prompt and the AI's response are written to a `chat_logs` table. This allows the AI to remember the context of the conversation if the user refreshes the page.

---

## ⚡ Real-Time Capabilities

A key advantage of using Supabase is its real-time functionality.

The dashboard subscribes to database changes. If the Desktop Agent uploads a new "Critical Alert" (e.g., high temperature) while the user is viewing the dashboard, the graph updates automatically without requiring a manual page refresh. This provides near-instant visibility into the system's current state.

---

## 🔒 Security via Row Level Security (RLS)

The web application relies on the database to enforce privacy, rather than filtering data in the frontend code.

**How it works:**
* Every request sent from the web dashboard includes the user's unique Authentication Token.
* The database checks this token against the data being requested.
* If the user tries to access a system report that belongs to a different User ID, the database returns an empty result set.

This ensures that even if there is a bug in the web application's code, one user can never accidentally see another user's private system data.