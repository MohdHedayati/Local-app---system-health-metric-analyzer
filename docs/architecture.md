# System Architecture

This project implements a **distributed intelligent diagnostics platform** combining system-level monitoring, machine learning, agentic AI, retrieval-augmented generation (RAG), and full-stack web technologies.

The system is architected into **two tightly coupled applications**:

- **Desktop System Agent (PyQt5)** – responsible for hardware-level data collection, ML inference, and secure reporting.
- **Web Dashboard (Streamlit)** – responsible for visualization, AI-powered diagnostics, and cloud-based analytics.

---

## High-Level Architecture

```mermaid
graph TD
    %% Styling
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef cloud fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef ml fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;

    subgraph Client_Side [User Local Environment]
        direction TB
        User((User))
        
        subgraph Desktop_App [PyQt5 Desktop Agent]
            Auth_Local[Google OAuth]
            Metrics[psutil Metrics Engine]
            Report_Gen[Report Generator]
            
            subgraph ML_Engine [Local Intelligence]
                Neural_Net[Neural Networks]
                Anomaly[Anomaly Detection]
            end
        end
    end

    subgraph Cloud_Side [Cloud Infrastructure]
        direction TB
        
        subgraph Backend [Supabase Backend]
            Auth_DB[(Auth & Users)]
            Metrics_DB[(Metrics Storage)]
            Vector_DB[(Vector Store)]
        end

        subgraph Web_Platform [Streamlit Web Dashboard]
            Dashboard[Visual Dashboard]
            Chat_UI[AI Chat Interface]
            
            subgraph AI_Core [Agentic AI Engine]
                RAG[RAG Pipeline]
                LLM[LLM Reasoning]
                Agents[Autonomous Agents]
            end
        end
    end

    %% Connections
    User -->|Starts| Desktop_App
    User -->|Visits| Web_Platform

    %% Desktop Flows
    Metrics -->|Raw Data| Neural_Net
    Neural_Net -->|Inference| Anomaly
    Anomaly -->|Insights| Report_Gen
    Metrics -->|Stats| Report_Gen
    Report_Gen -->|Secure Upload| Metrics_DB

    %% Cloud Flows
    Web_Platform -->|Fetch Data| Metrics_DB
    Chat_UI -->|Query| AI_Core
    AI_Core -->|Retrieve Context| Vector_DB
    AI_Core -->|Response| Chat_UI
    
    %% Styles
    class Desktop_App,Web_Platform client;
    class Backend,AI_Core cloud;
    class Auth_DB,Metrics_DB,Vector_DB db;
    class ML_Engine,Neural_Net,Anomaly ml;
```

---

## Architectural Principles

### 1. Separation of Concerns

The system separates responsibilities between:

- **Local System Intelligence**
- **Cloud-based AI Reasoning**
- **Persistent Storage & Authentication**

This ensures:
- Security
- Scalability
- Platform independence
- Modularity

---

### 2. Dual Application Design

#### Desktop System Agent (PyQt5)

The desktop agent is responsible for **hardware-sensitive operations**, which are not possible inside browser-based applications due to sandboxing and security constraints.

Responsibilities:

- Secure Google OAuth authentication
- Real-time system metric collection using `psutil`
- Local ML inference using trained neural networks
- Structured health report generation
- Secure upload of reports to Supabase

The desktop client acts as a **trusted system sensor and intelligence node**.

---

#### Web Dashboard (Streamlit)

The web application provides:

- Cloud-based visualization
- Historical report analysis
- AI-powered diagnostics chatbot
- Interactive dashboards

Responsibilities:

- Secure OAuth login
- Supabase data access
- RAG pipeline execution
- LLM-powered conversational diagnostics
- UX-focused interface design

---

## Data Flow Pipeline

### Step 1 — Metric Collection (Desktop)

System metrics are collected using `psutil`, including:

- CPU utilization and frequency
- Memory usage
- Disk usage and I/O
- Network activity
- Temperature sensors (when available)
- Active process statistics

---

### Step 2 — Local ML Inference

Collected metrics are passed into **trained neural classifiers** that perform:

- Real-time anomaly detection
- Subsystem classification:
  - CPU + Memory
  - Disk
  - Network
  - Temperature

This enables **immediate local detection of suspicious system behavior**.

---

### Step 3 — Agentic Intelligence Engine

ML outputs are combined with:

- Statistical heuristics
- Domain-driven threat signatures
- Multi-dimensional risk scoring

The system performs:

- Cryptojacking detection
- Data exfiltration detection
- Thermal abuse analysis
- Sustained workload profiling
- Root cause process attribution

This hybrid architecture combines:

> **Neural Intelligence + Rule-based Expert Systems**

---

### Step 4 — Structured Report Generation

A comprehensive health report is generated containing:

- Global threat index
- Subsystem anomaly breakdown
- Root cause processes
- Aggregate window analysis
- Predictive system forecasts

This structured format enables seamless cloud analysis and AI interpretation.

---

### Step 5 — Secure Cloud Synchronization

Reports are uploaded to Supabase using secure API access.

Supabase provides:

- Authentication mapping
- Report storage
- Chat history storage
- Full CRUD support

---

### Step 6 — AI Reasoning & RAG

The Streamlit web application integrates:

- Vector database powered RAG pipeline
- OS-specific contextual knowledge bases
- Generative LLM chatbot

This allows:

- Context-aware diagnostics
- Explainable system health insights
- OS-tailored optimization guidance

---

## AI System Design

### Generative AI

- LLM-based conversational diagnostics
- System health explanation
- Actionable optimization guidance

---

### Agentic AI

- Autonomous threat reasoning
- Root cause inference
- Predictive trend modeling
- Decision fusion across subsystems

---

### Machine Learning Layer

- Neural classifiers for:
  - CPU + memory anomalies
  - Disk anomalies
  - Network anomalies
  - Thermal anomalies
- Encoders for feature extraction
- Supervised training on synthetic + real workload profiles

---

## Why This Architecture Matters

This system replicates **real-world observability and cybersecurity architectures** used in:

- Enterprise monitoring platforms
- Endpoint detection systems (EDR)
- Cloud telemetry analytics
- Predictive maintenance systems

By integrating:

- Desktop-level sensing
- Cloud-scale AI reasoning
- Hybrid intelligence models

the project achieves **industrial-grade system diagnostics capabilities**.

---

## System Capabilities Summary

| Layer | Capability |
|---------|-------------|
| Desktop | Real-time monitoring + ML inference |
| Backend | Secure storage + authentication |
| AI | Generative + Agentic + RAG |
| Web | Visualization + conversational diagnostics |
| ML | Trend modeling + anomaly classification |

---

This architecture enables **scalable, secure, and intelligent system diagnostics across platforms**.
