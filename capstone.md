# LifePilot
## Your AI-Powered Personal Growth Architect

### Project Description

**LifePilot** is not just another to-do list; it is an intelligent, agentic productivity system designed to act as your personal life architect. LifePilot leverages a sophisticated Multi-Agent System (MAS) to help users move from chaos to clarity.

In a world where attention is our scarcest resource, LifePilot uses Google's Gemini models to understand your goals, break them down into actionable plans, and help you execute them with precision. It bridges the gap between *knowing* what to do and actually *doing* it by embedding an AI that remembers your context, understands your schedule, and proactively assists in managing your life.

### Problem Statement

**The "Execution Gap" in Personal Productivity.**

We live in an era of information overload and decision fatigue. Most productivity tools are passive containers—they store what you type but offer no intelligence on *how* to achieve it.
-   **Fragmentation**: Users juggle a calendar for time, a todo app for tasks, and notes for planning. Context is lost between apps.
-   **Planning Fallacy**: Humans are terrible at estimating time and breaking down complex goals. A goal like "Learn DSA" often sits undefined on a list for months.
-   **Context Amnesia**: Traditional chatbots don't remember your life. You have to re-explain your schedule, preferences, and past progress every time.

We built LifePilot to solve the **Execution Gap**—the void between setting a goal and taking the first step. We believe productivity software should be *active*, not passive. It should be a partner that plans *with* you.

### Why agents?

**Static code cannot solve dynamic human problems.**

Traditional "if-this-then-that" logic fails when applied to the messiness of human life.
-   **Reasoning vs. Rules**: A rule-based system can set a reminder. An **Agent** can look at your goal ("Run a marathon"), understand your constraints ("I have bad knees"), and generate a custom 4-week training plan that adapts to your schedule.
-   **Multi-Step Autonomy**: We needed a system that could handle complex workflows: *Understand Request -> Retrieve Past Context -> Research Best Practices -> Generate Plan -> Format for UI*. This requires a chain of specialized thinkers, not a single prompt.
-   **Contextual Adaptation**: Agents allow us to inject long-term memory (via Vector DB) into every interaction, making the AI feel like it truly *knows* you, rather than just processing your current sentence.

### What you created

We built a **Multi-Agent Productivity Ecosystem** that integrates a high-performance Planner App with an intelligent Agentic Backend.

**Agent Architecture**

The LifePilot backend is a sophisticated multi-agent system composed of a main orchestrator agent and several specialized sub-agents, working in harmony to deliver personalized productivity.

**Main Agent**

*   `RouterAgent`: This is the intelligent orchestrator that serves as the single point of entry for all user interactions. It analyzes the semantic intent of every message (distinguishing between planning requests, memory retrieval, or casual chat) and manages the workflow by delegating tasks to the appropriate specialist sub-agents.

**Multi-Agents**

The sub-agents are specialized workers defined in our agentic pipeline, each responsible for a specific cognitive task:

*   `PlannerAgent`: The core architect. It specializes in breaking down vague user goals (e.g., "I want to get fit") into structured, actionable routines and schedules. It leverages RAG (Retrieval Augmented Generation) to contextualize plans based on the user's unique history and preferences.
*   `MemoryAgent`: The guardian of context. It manages the **Pinecone Vector Database**, embedding user interactions to provide infinite memory. It ensures the AI never forgets a detail, retrieving relevant past information to inform current decisions.
*   `KnowledgeAgent`: The researcher. It connects to the external world via web search tools to fetch real-time information, ensuring plans are based on up-to-date data (e.g., finding specific diet trends or local gym hours).
*   `ExecutorAgent`: The action-taker. Designed to interact directly with the application state, it handles the creation of tasks, updates to routines, and modifications to the user's calendar based on the approved plans.

**Tools**

The agents utilize a suite of custom and integrated tools to interact with data and the outside world:

*   `Google Gemini Flash Lite`: The high-speed cognitive engine powering the reasoning capabilities of all agents.
*   `Pinecone Vector DB`: Provides low-latency semantic search, allowing agents to "remember" and retrieve relevant past conversations.
*   `WebSearchTool`: Enables agents to browse the live internet for research, validation, and gathering external context.
*   `CalendarTool`: Allows the system to understand time constraints and schedule tasks effectively within the user's real-world timeline.
*   `MongoDB Atlas`: The persistent storage layer for structured user data (tasks, routines, user profiles).

**Workflow**

The `RouterAgent` orchestrates a dynamic workflow to handle complex user requests:

1.  **Analyze & Route**: The user's message is analyzed for intent. If a complex goal is detected (e.g., "Plan a 4-week DSA roadmap"), it is routed to the `PlannerAgent`.
2.  **Contextual Retrieval**: The `MemoryAgent` is triggered to search the Vector DB for relevant past context (e.g., "User prefers studying in the mornings").
3.  **Plan Generation**: The `PlannerAgent` synthesizes the request, the retrieved memory context, and potentially live web data (via `KnowledgeAgent`) to construct a detailed, week-by-week plan.
4.  **Refinement**: The plan is presented to the user. If feedback is provided (e.g., "Make it 6 weeks"), the cycle repeats with the new constraint added to the context.
5.  **Execution**: Once finalized, the plan is converted into actionable database entries (Tasks and Routines) for the user to track in the LifePilot dashboard.

**Current Implementation Status:**
-   **✅ Established & Live**: The core **Planner**, **Tasks**, and **Routines** modules are fully functional. The **AI Chatbot** is deeply integrated, capable of generating structured plans. The **Multi-Agent Backend** with RAG and Vector Memory is fully operational.
-   **🚀 Future Vision**: The **Dashboard** currently serves as a visual north star for "Smart Insights". The **Settings** page outlines the future of deep personalization.

### Demo

*(Leave empty for manual video insertion)*

### The Build

We engineered LifePilot with a modern, scalable stack designed for performance and AI integration:

-   **AI & Logic**:
    -   **Google Gemini Flash Lite**: Chosen for its incredible balance of latency and reasoning capability, essential for a real-time chat interface.
    -   **Google Gemini text-embedding-004**: For high-fidelity semantic search in our memory system.
    -   **Pinecone (Serverless)**: A high-performance Vector Database for long-term agent memory.
    -   **LangChain & Custom Agent Loop**: We built a custom, lightweight agent loop for maximum control over the reasoning steps.

-   **Backend**:
    -   **FastAPI (Python)**: High-performance async backend to handle concurrent agent operations.
    -   **MongoDB Atlas**: Flexible document storage for complex user data (nested routines, rich task metadata).

-   **Frontend**:
    -   **Next.js 14**: For a reactive, server-side rendered UI.
    -   **TailwindCSS & Framer Motion**: To create a "premium," fluid user experience that feels alive.

### If I had more time, this is what I'd do

We have laid a powerful foundation, but we are just scratching the surface of Agentic Productivity.

1.  **"One-Click" Plan Adoption**: Currently, the AI generates a beautiful plan. The next step is **Deep Action Integration**, where the AI can directly inject these routines and tasks into the user's database with a single confirmation click. Imagine saying "Apply this plan," and your calendar is instantly populated for the month.
2.  **Proactive Coaching Agents**: Instead of waiting for you to ask, a background agent would analyze your completion data. *"Hey, I noticed you missed your 'Morning Run' 3 days in a row. Should we adjust the time to 7:30 AM?"*
3.  **Voice Mode**: A hands-free planning experience. Talk to LifePilot while driving to organize your day.
4.  **Collaborative Planning**: Multi-user agents that can negotiate schedules between two users (e.g., finding a time for a meeting or a shared gym session).

LifePilot is not just a tool; it's a vision of a future where AI helps us reclaim our time and potential.
