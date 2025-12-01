# LifePilot: AI-Powered Personal Growth Architect 🚀

![LifePilot Banner](https://img.shields.io/badge/Status-Live-green) ![Gemini](https://img.shields.io/badge/AI-Gemini_Flash-blue) ![Agentic](https://img.shields.io/badge/Architecture-Multi--Agent-purple)

**LifePilot** is an intelligent, agentic productivity system designed to act as your personal life architect. Unlike passive to-do lists, LifePilot uses a **Multi-Agent System (MAS)** powered by **Google Gemini** to actively plan, schedule, and manage your life.

---

## ✨ Key Features

This project demonstrates **3 Key Agent Concepts**:
1.  **Multi-Agent Orchestration**: A central `RouterAgent` and `MultiAgentOrchestrator` that delegate tasks to specialized workers (`Planner`, `Executor`, `Knowledge`).
2.  **RAG-Powered Long-Term Memory**: A `MemoryAgent` that uses **Pinecone Vector DB** to retain user context across sessions, solving "Context Amnesia".
3.  **Proactive Routine Management**: A `RoutineAgent` that runs in the background (Cron-like) to manage recurring tasks and health checks without user initiation.

---

## 📖 Table of Contents
- [Problem Statement](#-problem-statement)
- [Solution & Value](#-solution--value)
- [Architecture](#-architecture)
- [Technical Implementation](#-technical-implementation)
- [Setup & Installation](#-setup--installation)
- [Project Journey](#-project-journey)

---

## 🚩 Problem Statement
**The "Execution Gap" in Personal Productivity.**
We live in an era of decision fatigue. Most tools are passive containers—they store *what* you type but offer no intelligence on *how* to achieve it.
-   **Fragmentation**: Context is lost between calendars, notes, and to-do apps.
-   **Planning Fallacy**: Humans struggle to break down complex goals (e.g., "Learn DSA") into actionable steps.
-   **Context Amnesia**: Chatbots usually forget who you are after the session ends.

## 💡 Solution & Value
LifePilot bridges the gap between *knowing* and *doing*.
-   **Active Planning**: You say "I want to get fit," and the **Planner Agent** generates a 4-week workout schedule tailored to your free time.
-   **Unified Context**: The **Memory Agent** remembers your bad knees and prefers evening workouts, applying this constraint to every future plan.
-   **Automated Execution**: The **Executor Agent** and **Routine Agent** turn plans into database entries and reminders automatically.

---

## 🏗 Architecture

LifePilot employs a Hub-and-Spoke Agentic Architecture.

### Full-Stack Application Architecture

```mermaid
graph TB
    subgraph "Frontend - Next.js 14"
        UI[User Interface]
        Pages[Pages/Routes]
        Components[React Components]
        Store[Zustand State Management]
        API_Client[API Service Layer]
    end

    subgraph "Backend - FastAPI"
        Router[RouterAgent<br/>Entry Point]
        Orchestrator[MultiAgentOrchestrator<br/>Workflow Manager]
        
        subgraph "Specialized Agents"
            Planner[PlannerAgent<br/>Plan Generation]
            Executor[ExecutorAgent<br/>Task Execution]
            Knowledge[KnowledgeAgent<br/>Web Search]
            Memory[MemoryAgent<br/>Context Management]
            Routine[RoutineAgent<br/>Background Jobs]
            Notification[NotificationAgent<br/>Alerts]
            UIAgent[UIAgent<br/>Dashboard Data]
        end
        
        subgraph "Core Services"
            LLM[LLM Service<br/>Gemini Flash]
            Session[Session Service<br/>Context Tracking]
            MemBank[Memory Bank<br/>RAG Pipeline]
            Obs[Observability<br/>Tracing/Logging]
        end
        
        subgraph "Tools"
            Calendar[Calendar Tool]
            WebSearch[Web Search Tool]
            Python[Python Executor]
        end
    end

    subgraph "External Services"
        Gemini[Google Gemini API<br/>LLM + Embeddings]
        Pinecone[Pinecone Vector DB<br/>Long-term Memory]
        MongoDB[MongoDB Atlas<br/>User Data]
    end

    UI --> Pages
    Pages --> Components
    Components --> Store
    Store --> API_Client
    
    API_Client -->|HTTP/WebSocket| Router
    Router --> Orchestrator
    Router --> Planner
    Router --> Knowledge
    Router --> Memory
    
    Orchestrator --> Planner
    Orchestrator --> Executor
    Orchestrator --> Knowledge
    Orchestrator --> UIAgent
    
    Planner --> LLM
    Planner --> MemBank
    Knowledge --> WebSearch
    Knowledge --> MemBank
    Executor --> Calendar
    Executor --> Python
    Memory --> MemBank
    Routine --> Notification
    
    LLM --> Gemini
    MemBank --> Pinecone
    MemBank --> Gemini
    Session --> MongoDB
    Router --> MongoDB
    Planner --> MongoDB
    
    style UI fill:#4F46E5
    style Router fill:#10B981
    style Orchestrator fill:#F59E0B
    style Gemini fill:#EA4335
    style Pinecone fill:#00D4AA
    style MongoDB fill:#47A248
```

### AI Architecture
![LifePilot Architecture](frontend/public/images/architecture.png)

### Mind Map
![LifePilot Mind Map](frontend/public/images/mindmap.png)

### Architecture Diagram
```mermaid
mindmap
  root((LifePilot AI))
    Core_Orchestration:::orangeClass
      MultiAgentOrchestrator
        Workflow_Management
        State_Machine
        A2A_Protocol
    Entry_Point:::greenClass
      RouterAgent
        Intent_Detection
        Direct_Dispatch
    Specialized_Agents:::purpleClass
      PlannerAgent
        LLMService
      ExecutorAgent
        CalendarTool
        PythonExecutionTool
      KnowledgeAgent
        WebSearchTool
        RAG_Integration
      NotificationAgent
        Alert_Management
        WebSocket_Delivery
      RoutineAgent
        Cron_Scheduler
        LongRunner_Tasks
        Notification_Checks
      UIAgent
        Dashboard_Generation
    Memory_System:::blueClass
      MemoryBank
        Pinecone_Vector_DB
        Semantic_Search
      SessionService
        Conversation_History
      ContextCompactor
        Token_Management
    Observability:::redClass
      ObservabilityManager
        OpenTelemetry_Tracing
        Structlog_Logging
        System_Metrics
        
    classDef orangeClass fill:#F59E0B,stroke:#D97706,stroke-width:2px,color:#000
    classDef greenClass fill:#10B981,stroke:#059669,stroke-width:2px,color:#000
    classDef purpleClass fill:#8B5CF6,stroke:#7C3AED,stroke-width:2px,color:#fff
    classDef blueClass fill:#3B82F6,stroke:#2563EB,stroke-width:2px,color:#fff
    classDef redClass fill:#EF4444,stroke:#DC2626,stroke-width:2px,color:#fff
```

### Core Components
1.  **RouterAgent (The Gatekeeper)**: Analyzes intent (regex/LLM) and routes requests.
2.  **PlannerAgent (The Architect)**: Uses Gemini to decompose goals into structured plans.
3.  **MemoryBank (The Hippocampus)**: Dual-layer memory (Session + Pinecone Vector Store).
4.  **ExecutorAgent (The Doer)**: Executes code and manages calendar events.

---

## 🛠 Technical Implementation

### Tech Stack
-   **AI**: Google Gemini Flash Lite, text-embedding-004
-   **Backend**: FastAPI (Python), LangChain
-   **Frontend**: Next.js 14, TailwindCSS, Framer Motion
-   **Database**: MongoDB Atlas (User Data), Pinecone (Vector Memory)
-   **Observability**: OpenTelemetry, Structlog

### Key Features
-   **Agent-to-Agent (A2A) Protocol**: Standardized messaging format for inter-agent communication.
-   **Context Compactor**: Smart pruning of conversation history to manage token windows efficiently.
-   **Resilient Error Handling**: Agents have fallback mechanisms (e.g., Planner falls back to rule-based steps if LLM fails).

---

## 🚀 Setup & Installation

### Prerequisites
-   Node.js 18+
-   Python 3.10+
-   MongoDB Atlas URI
-   Pinecone API Key
-   Google Gemini API Key

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your API keys in .env

# Run the server
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local file
cp .env.local.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

Visit `http://localhost:3000` to start using LifePilot!

---

## 🛣 Project Journey
Building LifePilot was a journey of moving from "Chatbot" to "Agent".
-   **Challenge**: Getting the AI to "remember" context meaningfully.
-   **Solution**: We implemented a RAG pipeline with Pinecone, allowing the agents to query past interactions before generating a plan.
-   **Challenge**: Managing complex, multi-step tasks.
-   **Solution**: We built the `MultiAgentOrchestrator` to handle state and workflow transitions, ensuring long-running tasks don't time out or get lost.


