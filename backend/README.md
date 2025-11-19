# LifePilot Backend

FastAPI-based backend for the LifePilot AI assistant application.

## Features

- **Agent Pipeline Architecture**: Router, Planner, Executor, Knowledge, Memory, and Analyzer agents
- **Session Management**: User session tracking with timeout and cleanup
- **Memory Bank**: Persistent storage with categorization and search
- **Tool Integration**: Calendar, Web Search, and Shopping tools
- **Structured Logging**: Comprehensive logging with structlog
- **Async Processing**: Full async support for better performance

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Router    │───▶│   Planner   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   Memory    │    │  Knowledge  │
                   └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  Executor   │    │  Analyzer   │
                   └─────────────┘    └─────────────┘
```

## Core Components

### Agents

- **RouterAgent**: Orchestrates the entire pipeline
- **PlannerAgent**: Creates structured plans from user requests
- **ExecutorAgent**: Executes tasks and manages calendar integration
- **KnowledgeAgent**: Performs web searches and knowledge retrieval
- **MemoryAgent**: Manages persistent memory storage
- **AnalyzerAgent**: Formats and polishes final responses

### Services

- **SessionService**: User session management with timeout
- **MemoryBank**: Centralized memory storage with search capabilities

### Tools

- **CalendarTool**: Mock calendar for task scheduling
- **WebSearchTool**: Mock web search for knowledge retrieval
- **ShoppingTool**: Mock shopping for product recommendations

## Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python start.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Test the Backend

Run the test script:
```bash
python test_backend.py
```

### API Endpoints

#### POST /api/chat
Chat with the LifePilot AI assistant.

**Request:**
```json
{
  "user_id": "user123",
  "message": "Plan my morning routine"
}
```

**Response:**
```json
{
  "reply": "📋 **Your Personalized Plan**\n\nHere's your structured morning routine:\n\n• Wake up at 7:00 AM\n• Meditate for 10 minutes\n• Healthy breakfast with oats and fruits\n• Light exercise or stretching\n\n💡 **Tips for Success:**\n- Be consistent with your wake-up time\n- Prepare breakfast items the night before\n- Start with just 5 minutes of meditation if you're new"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── agents/          # Agent implementations
│   ├── api/            # API endpoints
│   ├── core/           # Core services and utilities
│   ├── tools/          # External tool integrations
│   ├── main.py         # FastAPI application
│   ├── config.py       # Configuration
│   └── schemas.py      # Pydantic models
├── requirements.txt    # Python dependencies
├── start.py           # Startup script
├── test_backend.py    # Test script
└── README.md          # This file
```

### Adding New Agents

1. Create agent class in `app/agents/`
2. Implement async methods following the pattern
3. Add to RouterAgent initialization
4. Update schemas if needed

### Adding New Tools

1. Create tool class in `app/tools/`
2. Implement mock or real functionality
3. Add to relevant agents
4. Test with `test_backend.py`

### Logging

The application uses structured logging with `structlog`. Logs include:
- Agent initialization and processing
- Tool usage and results
- Session management
- Memory operations
- Errors and warnings

## Configuration

Current configuration is minimal and uses defaults. Future versions may include:
- Environment variable configuration
- Database connections
- External API keys
- Feature flags

## Testing

Run the comprehensive test suite:
```bash
python test_backend.py
```

Tests cover:
- Agent pipeline functionality
- Session management
- Memory operations
- Tool integrations
- Error handling

## Deployment

For production deployment:
1. Set environment variables
2. Use a production ASGI server (Gunicorn + Uvicorn)
3. Configure proper logging
4. Set up monitoring and health checks
5. Use HTTPS and proper authentication

## Contributing

1. Follow the existing code patterns
2. Add comprehensive logging
3. Include tests for new features
4. Update documentation
5. Use async/await consistently

## License

[Add your license information here]
