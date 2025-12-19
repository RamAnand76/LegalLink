# LegalLink FastAPI Backend

A professional, industry-standard FastAPI backend for the LegalLink project.

## Project Structure

```text
app/
├── api/                # API route definitions
│   ├── endpoints/      # Specific endpoint logic (auth, users, etc.)
│   └── api.py          # Main router combining all endpoints
├── core/               # Core configuration and security
│   ├── config.py      # Pydantic settings management
│   └── security.py    # JWT and Hashing utilities
├── crud/               # CRUD (Create, Read, Update, Delete) operations
├── db/                 # Database connection and session management
├── models/             # SQLAlchemy database models
├── schemas/            # Pydantic models for data validation/serialization
└── main.py             # FastAPI application entry point
static/                 # Static files (e.g., uploaded profile pictures)
```

## Features

- **Authentication**: JWT-based authentication with signup and login.
- **User Management**: Profile updates, password changes, and profile picture uploads.
- **Security**: Password hashing using Passlib (Bcrypt) and secure JWT tokens.
- **Validation**: Strict data validation using Pydantic.
- **Database**: SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL).

## API Response Format

All API responses follow a standardized international format:

```json
{
  "message": "A descriptive message about the operation",
  "data": { ... } or [ ... ] or null
}
```

- **message**: A human-readable string explaining the result.
- **data**: The actual payload of the response. If no data is returned, this will be `null`.

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual Environment (recommended)

### Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on the provided template:
   ```env
   PROJECT_NAME=LegalLink
   API_STR=/api
   SECRET_KEY=yoursecretkeyhere
   ACCESS_TOKEN_EXPIRE_MINUTES=11520
   SQLALCHEMY_DATABASE_URL=sqlite:///./sql_app.db
   ```

### Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
Access the interactive documentation at `http://127.0.0.1:8000/docs`.

## Workflow for Trainees

1. **Schema First**: Define your data models in `app/schemas/` before writing logic.
2. **Database Models**: Create SQLAlchemy models in `app/models/` to match your schemas.
3. **CRUD Operations**: Implement data logic in `app/crud/` to keep controllers thin.
4. **Endpoints**: Add routes in `app/api/endpoints/` and register them in `api.py`.
5. **Testing**: Test your endpoints using the `/docs` UI or Postman.
