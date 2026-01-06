# LegalLink FastAPI Backend

A professional, production-ready FastAPI backend for the LegalLink project featuring **RAG-powered AI legal assistance** with chat history and session management.

## 🚀 Features

### Core Features
- **JWT Authentication**: Secure signup/login with Bearer token authentication
- **User Management**: Profile updates, password changes, profile picture uploads
- **Security**: Password hashing (Bcrypt) and secure JWT tokens

### AI Chat Features
- **RAG-Powered Chat**: Retrieval-Augmented Generation using legal documents
- **FAISS Vector Store**: Fast similarity search for document retrieval
- **Multi-Provider LLM**: Switch between OpenRouter and OpenAI
- **Chat Sessions**: Individual chat history per user (like ChatGPT)
- **UUID Session IDs**: Secure, unique session identifiers
- **Context Transparency**: Returns RAG chunks used for each response
- **Relevance Scoring**: Filters irrelevant chunks with configurable threshold

## 📁 Project Structure

```text
app/
├── api/                    # API route definitions
│   ├── endpoints/          # Endpoint logic
│   │   ├── auth.py         # Authentication (signup, login)
│   │   ├── users.py        # User profile management
│   │   └── chat.py         # RAG chat endpoints
│   ├── deps.py             # Dependencies (DB session, auth)
│   └── api.py              # Main router
├── core/                   # Core configuration
│   ├── config.py           # Pydantic settings (env vars)
│   └── security.py         # JWT and hashing utilities
├── crud/                   # CRUD operations
│   ├── crud_user.py        # User CRUD
│   └── crud_chat.py        # Chat session/message CRUD
├── db/                     # Database
│   ├── base.py             # SQLAlchemy Base imports
│   ├── base_class.py       # Base model class
│   └── session.py          # Database session
├── models/                 # SQLAlchemy models
│   ├── user.py             # User model
│   └── chat.py             # ChatSession, ChatMessage models
├── schemas/                # Pydantic schemas
│   ├── user.py             # User schemas
│   ├── chat.py             # Chat schemas
│   ├── token.py            # Token schemas
│   └── response.py         # Standard response schema
├── services/               # Business logic services
│   ├── rag_service.py      # FAISS + embeddings
│   └── llm_service.py      # OpenRouter/OpenAI integration
└── main.py                 # FastAPI app entry point
docs/                       # Legal documents for RAG (PDFs, TXT)
faiss_index/                # Persisted FAISS vector store
static/                     # Static files (profile images)
```

## 📋 API Response Format

All API responses follow a standardized format:

```json
{
  "message": "A descriptive message about the operation",
  "data": { ... } | [ ... ] | []
}
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.9+
- Virtual Environment (recommended)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd LegalLink
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```env
   # Core Settings
   PROJECT_NAME=LegalLink
   SECRET_KEY=your-super-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=11520
   SQLALCHEMY_DATABASE_URL=sqlite:///./sql_app.db

   # LLM Provider (openrouter or openai)
   PROVIDER=openrouter

   # OpenRouter Settings
   OPENROUTER_API_KEY=your-openrouter-api-key
   OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free

   # OpenAI Settings (optional fallback)
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-3.5-turbo

   # RAG Settings
   DOCS_PATH=docs
   FAISS_INDEX_PATH=faiss_index
   ```

5. **Add legal documents** to the `docs/` folder (PDFs or TXT files)

### Running the Application

```bash
uvicorn app.main:app --reload
```

- **API**: `http://127.0.0.1:8000`
- **Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 🤖 RAG Chat System

### How It Works

1. **Document Loading**: PDFs/TXT files from `docs/` folder
2. **Chunking**: Documents split into 1000-char chunks (200 overlap)
3. **Embedding**: `sentence-transformers/all-MiniLM-L6-v2`
4. **Vector Store**: FAISS for fast similarity search
5. **Retrieval**: Top-k chunks retrieved based on query similarity
6. **Filtering**: Only chunks above relevance threshold (default 0.7)
7. **Generation**: LLM generates response using retrieved context

### Relevance Scoring

```
Similarity Score = 1 / (1 + FAISS_Distance)

Threshold Guide:
- 0.5: Loose (more chunks, some noise)
- 0.7: Balanced (default)
- 0.8: Strict (highly relevant only)
- 0.9: Very strict (may return nothing)
```

### Provider Switching

Set `PROVIDER` in `.env`:
- `openrouter`: Uses OpenRouter API (free models available)
- `openai`: Uses OpenAI API

If OpenRouter rate-limits (429), automatically falls back to OpenAI if configured.

## 📚 API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/signup` | POST | Create new user |
| `/api/auth/login` | POST | Get access token |

### User Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/me` | GET | Get current user |
| `/api/users/me` | PUT | Update profile |
| `/api/users/me/reset-password` | POST | Change password |
| `/api/users/me/profile-image` | POST | Upload profile picture |

### Chat (RAG-Powered AI)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/send` | POST | Send message, get AI response |
| `/api/chat/sessions` | GET | List all sessions |
| `/api/chat/sessions/{uuid}` | GET | Get session with messages |
| `/api/chat/sessions/{uuid}` | PUT | Rename session |
| `/api/chat/sessions/{uuid}` | DELETE | Delete session |
| `/api/chat/rebuild-index` | POST | Rebuild RAG index |
| `/api/chat/test-search` | POST | Test RAG with scores |

## 🔒 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key |
| `SQLALCHEMY_DATABASE_URL` | Yes | - | Database connection string |
| `PROVIDER` | No | `openrouter` | LLM provider |
| `OPENROUTER_API_KEY` | No* | - | OpenRouter API key |
| `OPENAI_API_KEY` | No* | - | OpenAI API key |
| `DOCS_PATH` | No | `docs` | Documents folder path |
| `FAISS_INDEX_PATH` | No | `faiss_index` | FAISS index path |

*At least one API key required for chat functionality

## 📖 Documentation

- **API Documentation**: See [API_DOC.md](API_DOC.md) for detailed endpoint documentation
- **Swagger UI**: `http://127.0.0.1:8000/docs`

## 🧪 Testing

Use the Swagger UI at `/docs` for interactive API testing:
1. Call `/auth/signup` to create a user
2. Click **Authorize** and enter credentials
3. Test chat endpoints with your legal questions

## 📝 License

This project is for educational purposes.
