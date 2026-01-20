# AI Chatbot Platform - Backend

FastAPI backend with LangChain integration for an AI chatbot platform.

## Tech Stack

- **Framework**: FastAPI
- **AI Framework**: LangChain (Python)
- **Server**: uvicorn
- **Memory**: LangChain ConversationBufferMemory

## Project Structure

```
backend/
│
├── app/
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Authentication endpoints (stub)
│   │   ├── chat.py            # Chat endpoints (core)
│   │   └── conversations.py   # Conversation management
│   │
│   ├── core/                   # Core business logic
│   │   ├── config.py          # Configuration management
│   │   ├── model_router.py    # LLM model routing
│   │   ├── agent_factory.py   # LangChain agent creation
│   │   └── memory_manager.py  # Conversation memory management
│   │
│   ├── schemas/                # Pydantic models
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── conversation.py
│   │
│   └── storage/                # Data storage layer
│       └── chat_history.py    # In-memory chat history
│
├── requirements.txt
└── README.md
```

## Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Server health status

### Authentication (Stub)
- `POST /auth/login` - Mock login endpoint

### Chat
- `POST /chat` - Send chat messages with conversation memory

### Conversations
- `GET /conversations` - List all conversations
- `GET /conversations/{conversation_id}` - Get specific conversation

## Features

- ✅ FastAPI with async support
- ✅ LangChain conversation agents
- ✅ Conversation memory (in-memory)
- ✅ Model routing (extensible)
- ✅ Clean architecture with separation of concerns

## Future Extensions

This is a foundational backend. Future steps will add:
- MCP tool integration
- RAG (Retrieval-Augmented Generation)
- Web search capabilities
- Image generation
- Database persistence
- Real authentication
