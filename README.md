# LifePilot: AI-Powered Personal Growth Architect 🚀

![LifePilot Banner](https://img.shields.io/badge/Status-Live-green) ![Gemini](https://img.shields.io/badge/AI-Gemini_Flash-blue) ![Agentic](https://img.shields.io/badge/Architecture-Multi--Agent-purple)

**LifePilot** is an intelligent, agentic productivity system designed to act as your personal life architect. Unlike passive to-do lists, LifePilot uses a **Multi-Agent System (MAS)** powered by **Google Gemini** to actively plan, schedule, and manage your life.

---

<div align="center">
  <a href="https://lifepilot-nine.vercel.app/" target="_blank" style="text-decoration: none;">
    <div style="
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 16px;
      padding: 32px;
      margin: 24px 0;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;
      max-width: 600px;
      position: relative;
      overflow: hidden;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 25px 50px rgba(0, 0, 0, 0.2)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 20px 40px rgba(0, 0, 0, 0.15)'">
      
      <!-- Animated background elements -->
      <div style="
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
      "></div>
      
      <!-- Content -->
      <div style="position: relative; z-index: 2;">
        <div style="
          display: inline-flex;
          align-items: center;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50px;
          padding: 8px 16px;
          margin-bottom: 16px;
          backdrop-filter: blur(10px);
        ">
          <span style="
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 2s infinite;
          "></span>
          <span style="color: white; font-size: 14px; font-weight: 600;">LIVE NOW</span>
        </div>
        
        <h2 style="
          color: white;
          font-size: 28px;
          font-weight: 700;
          margin: 0 0 12px 0;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        ">Experience LifePilot</h2>
        
        <p style="
          color: rgba(255, 255, 255, 0.9);
          font-size: 16px;
          margin: 0 0 20px 0;
          line-height: 1.5;
        ">Try the AI-powered personal growth architect in action</p>
        
        <div style="
          display: inline-flex;
          align-items: center;
          background: white;
          color: #667eea;
          padding: 12px 24px;
          border-radius: 8px;
          font-weight: 600;
          font-size: 16px;
          transition: all 0.2s ease;
        " onmouseover="this.style.background='rgba(255, 255, 255, 0.95)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='white'; this.style.transform='scale(1)'">
          <span>Launch Live Demo</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-left: 8px;">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </div>
      </div>
    </div>
  </a>
</div>

<style>
@keyframes pulse {
  0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.5; }
  50% { transform: scale(1.1) rotate(180deg); opacity: 0.3; }
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>

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
    style Router fill:#059669
    style Orchestrator fill:#C92519
    style Gemini fill:#F87726
    style Pinecone fill:#4E9FE5
    style MongoDB fill:#111111
```

### AI Architecture Diagram
```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#6366F1', 'primaryTextColor': '#fff', 'primaryBorderColor': '#4F46E5', 'lineColor': '#94A3B8', 'secondaryColor': '#FEF3C7', 'secondaryTextColor': '#000', 'secondaryBorderColor': '#F59E0B', 'tertiaryColor': '#D1FAE5', 'tertiaryTextColor': '#000', 'tertiaryBorderColor': '#10B981', 'noteBkgColor': '#DBEAFE', 'noteTextColor': '#000', 'noteBorderColor': '#3B82F6'}}}%%
mindmap
  root((LifePilot AI))
    Core Orchestration
      MultiAgentOrchestrator
        Workflow Management
        State Machine
        A2A Protocol
    Entry Point
      RouterAgent
        Intent Detection
        Direct Dispatch
    Specialized Agents
      PlannerAgent
        LLMService
      ExecutorAgent
        CalendarTool
        PythonExecutionTool
      KnowledgeAgent
        WebSearchTool
        RAG Integration
      NotificationAgent
        Alert Management
        WebSocket Delivery
      RoutineAgent
        Cron Scheduler
        LongRunner Tasks
        Notification Checks
      UIAgent
        Dashboard Generation
    Memory System
      MemoryBank
        Pinecone Vector DB
        Semantic Search
      SessionService
        Conversation History
      ContextCompactor
        Token Management
    Observability
      ObservabilityManager
        OpenTelemetry Tracing
        Structlog Logging
        System Metrics
```

### Mind Map
![LifePilot Mind Map](frontend/public/images/mindmap.png)

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


