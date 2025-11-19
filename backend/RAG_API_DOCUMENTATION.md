# RAG API Documentation

## Overview

The RAG (Retrieval-Augmented Generation) API provides intelligent conversation capabilities with memory storage, knowledge retrieval, and planning functionality. The system uses Google Gemini for language generation and implements intelligent routing to handle different types of user requests.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for development use.

## Endpoints

### Chat API

**POST** `/api/chat`

Process user messages through the RAG pipeline with intelligent routing.

#### Request Body

```json
{
  "message": "string",
  "user_id": "string", 
  "session_id": "string"
}
```

**Parameters:**
- `message` (required): The user's message or query
- `user_id` (required): Unique identifier for the user
- `session_id` (required): Unique identifier for the conversation session

#### Response

```json
{
  "reply": "string"
}
```

#### Example Requests

##### Memory Storage
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remember: I have a meeting tomorrow at 2 PM with the design team",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

##### Memory Retrieval
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What meetings do I have?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

##### Knowledge Query
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best practices for project management?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

##### Planning Request
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan my day for tomorrow",
    "user_id": "user123", 
    "session_id": "session456"
  }'
```

## Message Types and Routing

The API uses intelligent routing to detect message types and process them accordingly:

### 1. Memory Storage Messages

**Patterns detected:**
- "Remember that I..."
- "Remember: ..."
- "I have a meeting/appointment/deadline..."
- "My preference/habit/routine..."
- "I prefer/like/enjoy/want/need..."
- "Store this..."
- "Keep in mind..."

**Processing:**
- Stores the message in the memory bank
- Returns confirmation of storage

### 2. Memory Retrieval Messages

**Patterns detected:**
- "What do you know/can you tell me..."
- "What have I told/did I say..."
- "Remember that I..."
- "What about/regarding..."
- "Tell me about my..."
- "What meetings/deadlines/tasks/preferences..."
- "Do you remember..."

**Processing:**
- Searches stored memories using vector similarity
- Returns relevant memories with AI-generated summary

### 3. Knowledge Query Messages

**Patterns detected:**
- "What are/is..."
- "How do/does/to..."
- "Why is/are/do..."
- "Explain..."
- "Describe..."
- "Search/find/look up..."
- "Information about..."
- "Best practices..."
- "Latest/recent..."
- "Trends in..."

**Processing:**
- Performs web search (mock implementation)
- Retrieves relevant information
- Formats results with titles, snippets, and URLs

### 4. Planning Messages

**Patterns detected:**
- "Plan my/for me..."
- "Help me plan..."
- "Create a plan..."
- "Schedule/organize..."
- "Project plan..."
- "Daily/weekly plan..."
- "How should I..."

**Processing:**
- Generates structured action plans
- Breaks down requests into actionable steps
- Returns formatted plan with step-by-step instructions

### 5. General Conversation

**Default fallback for other messages:**
- Full RAG pipeline processing
- Planning + Knowledge + Execution + Analysis
- Comprehensive response with multiple components

## Response Formats

### Memory Storage Response
```
Memory stored successfully.
```

### Memory Retrieval Response
```
Based on your stored information:

[Memory 1]
[Memory 2]
...
```

### Knowledge Query Response
```
Here's what I found:

• **Title 1**
  Snippet 1
  URL 1
• **Title 2**
  Snippet 2
  URL 2
...
```

### Planning Response
```
**Your Action Plan:**

1. Action 1
   Details 1
2. Action 2
   Details 2
...
```

### General Conversation Response
```
📋 **Your Personalized Plan**

### 🎯 Action Steps
**1.** Step 1
**2.** Step 2
...

### 💡 Key Insights
• Insight 1
• Insight 2
...

### ✅ Execution Status
• Status 1
• Status 2
...

### 📊 Summary
| Component | Status | Details |
|-----------|--------|---------|
...
```

## Error Handling

The API returns appropriate error messages when:
- Invalid request format
- Processing errors
- No relevant information found
- Memory retrieval fails

Example error response:
```json
{
  "reply": "I apologize, but I encountered an error while processing your request: [error details]"
}
```

## Environment Configuration

Required environment variables:

```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_API_KEY=your_gemini_api_key_here
```

## Testing

Use the provided test suite to verify functionality:

```bash
cd backend
python3 test_rag_api.py
```

The test suite covers:
- Memory storage and retrieval
- Knowledge queries
- Planning functionality
- Context continuity
- Error handling

## Implementation Details

### Architecture

- **RouterAgent**: Intelligent message routing and pipeline orchestration
- **MemoryAgent**: Memory storage, retrieval, and vector search
- **KnowledgeAgent**: Web search and knowledge retrieval
- **PlannerAgent**: Structured plan generation
- **ExecutorAgent**: Task execution (mock implementation)
- **AnalyzerAgent**: Response polishing and formatting

### Technologies

- **FastAPI**: Web framework
- **Google Gemini**: Language model
- **Vector Database**: Memory storage and similarity search
- **Structured Logging**: Comprehensive logging with structlog

### Mock Components

For development purposes, the following components use mock implementations:
- Web search (returns relevant mock results)
- Task execution (simulates task completion)

## Rate Limits

Currently no rate limits are enforced in development mode.

## Session Management

- Sessions are created automatically on first message
- Message count is tracked per session
- Context is maintained within sessions
- No session expiration in development mode

## Memory Storage

- Memories are stored with vector embeddings
- Supports semantic search and similarity matching
- Automatic categorization based on content
- Persistent storage across sessions

## Examples

### Complete Workflow

1. **Store Information**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remember: I prefer working in the morning and have a deadline Friday",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

2. **Retrieve Information**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my work preferences?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

3. **Get Knowledge**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are productivity tips for morning work?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

4. **Plan Actions**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me plan my work week",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

## Troubleshooting

### Common Issues

1. **Environment variables not loaded**
   - Ensure `.env` file exists in backend directory
   - Check `load_dotenv()` is called in `main.py`

2. **Mock responses instead of real Gemini responses**
   - Verify `GEMINI_API_KEY` is set correctly
   - Check network connectivity to Google API

3. **Memory not being retrieved**
   - Ensure memories are stored first
   - Check user_id consistency between store and retrieve calls

4. **Server not responding**
   - Ensure server is running on port 8000
   - Check for port conflicts

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=debug
```

## Future Enhancements

Planned improvements:
- Real web search integration
- Authentication and user management
- File upload and document indexing
- Real-time collaboration features
- Advanced analytics and insights
- Multi-language support
