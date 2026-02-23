# LegalLink API Documentation

Complete API documentation for frontend developers integrating with the LegalLink backend.

**Base URL:** `http://localhost:8000/api`

---

## Table of Contents

1. [Response Format](#response-format)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Auth](#1-authentication)
   - [Users](#2-user-management)
   - [Chat (RAG AI)](#3-chat-rag-powered-ai)
   - [User Documents & Analysis](#4-user-documents-and-analysis)
4. [Error Handling](#error-handling)
5. [Quick Start Examples](#quick-start-examples)
6. [System Knowledge Base](#system-knowledge-base)

---

## Response Format

All API responses follow a standardized format:

```json
{
  "message": "Description of the result",
  "data": { ... } | [ ... ] | []
}
```

| Field     | Type              | Description                                      |
|-----------|-------------------|--------------------------------------------------|
| `message` | `string`          | Human-readable status message                    |
| `data`    | `object \| array` | Response payload. Empty array `[]` if no data.   |

---

## Authentication

This API uses **JWT Bearer Token** authentication.

### How to Authenticate

1. Call `/auth/login` with credentials
2. Extract `access_token` from response
3. Include token in all protected requests:

```
Authorization: Bearer <access_token>
```

### Token Expiry

Tokens expire after 8 days by default. Re-authenticate when you receive a 401/403 error.

---

## Endpoints

### 1. Authentication

#### 1.1 Sign Up

Create a new user account.

| Property   | Value            |
|------------|------------------|
| **URL**    | `/auth/signup`   |
| **Method** | `POST`           |
| **Auth**   | Not required     |

**Request Body:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "yourpassword",
  "confirm_password": "yourpassword"
}
```

| Field              | Type     | Required | Description                 |
|--------------------|----------|----------|-----------------------------|
| `full_name`        | `string` | Yes      | User's full name            |
| `email`            | `string` | Yes      | Valid email address         |
| `password`         | `string` | Yes      | Password (min 6 characters) |
| `confirm_password` | `string` | Yes      | Must match `password`       |

**Success Response (201 Created):**

```json
{
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "profile_image": null
  }
}
```

---

#### 1.2 Login

Get an access token for authentication.

| Property   | Value          |
|------------|----------------|
| **URL**    | `/auth/login`  |
| **Method** | `POST`         |
| **Auth**   | Not required   |
| **Content-Type** | `application/x-www-form-urlencoded` |

**Request Body (Form Data):**

| Field      | Type     | Required | Description        |
|------------|----------|----------|--------------------|
| `username` | `string` | Yes      | User's email       |
| `password` | `string` | Yes      | User's password    |

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> **Note:** Login returns token at root level (OAuth2 compatible).

---

### 2. User Management

All user endpoints require authentication.

#### 2.1 Get Current User

| Property   | Value         |
|------------|---------------|
| **URL**    | `/users/me`   |
| **Method** | `GET`         |
| **Auth**   | Bearer Token  |

**Success Response (200 OK):**

```json
{
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "profile_image": "static/uploads/profile_1.jpg"
  }
}
```

---

#### 2.2 Update Profile

| Property   | Value         |
|------------|---------------|
| **URL**    | `/users/me`   |
| **Method** | `PUT`         |
| **Auth**   | Bearer Token  |

**Request Body:**

```json
{
  "full_name": "John Smith",
  "email": "johnsmith@example.com"
}
```

---

#### 2.3 Reset Password

| Property   | Value                    |
|------------|--------------------------|
| **URL**    | `/users/me/reset-password` |
| **Method** | `POST`                   |
| **Auth**   | Bearer Token             |

**Request Body:**

```json
{
  "old_password": "currentpassword",
  "new_password": "newpassword123",
  "confirm_new_password": "newpassword123"
}
```

---

#### 2.4 Upload Profile Image

| Property   | Value                    |
|------------|--------------------------|
| **URL**    | `/users/me/profile-image` |
| **Method** | `POST`                   |
| **Auth**   | Bearer Token             |
| **Content-Type** | `multipart/form-data` |

**Request Body:**

| Field  | Type   | Required | Description    |
|--------|--------|----------|----------------|
| `file` | `file` | Yes      | Image file     |

---

### 3. Chat (RAG-Powered AI)

All chat endpoints require authentication. The chat system uses Retrieval-Augmented Generation (RAG) to provide context-aware legal assistance.

#### 3.1 Send Message

Send a message and receive an AI response with RAG context.

| Property   | Value          |
|------------|----------------|
| **URL**    | `/chat/send`   |
| **Method** | `POST`         |
| **Auth**   | Bearer Token   |

**Request Body:**

```json
{
  "message": "What are my rights if my employer withholds my certificates?",
  "session_id": null
}
```

| Field        | Type     | Required | Description                                    |
|--------------|----------|----------|------------------------------------------------|
| `message`    | `string` | Yes      | User's message (1-10000 characters)            |
| `session_id` | `string` | No       | Existing session UUID. Null = new session.     |
| `document_id`| `string` | No       | ID of a user-uploaded document to use as context.|

**Success Response (200 OK):**

```json
{
  "message": "Message sent successfully",
  "data": {
    "session_id": "e1479787-7c18-4072-9d16-04ac7082fef9",
    "user_message": {
      "id": 1,
      "role": "user",
      "content": "What are my rights if my employer withholds my certificates?",
      "created_at": "2026-01-03T15:14:11.250260"
    },
    "assistant_message": {
      "id": 2,
      "role": "assistant",
      "content": "Based on the legal provisions...",
      "created_at": "2026-01-03T15:14:23.424919"
    },
    "context_chunks": [
      "Section 92. Public charities...",
      "may be executed in India as if...",
      "trust is situate to obtain a decree..."
    ]
  }
}
```

**Response Fields:**

| Field             | Type       | Description                                    |
|-------------------|------------|------------------------------------------------|
| `session_id`      | `string`   | UUID of the chat session                       |
| `user_message`    | `object`   | The saved user message                         |
| `assistant_message` | `object` | The AI-generated response                      |
| `context_chunks`  | `array`    | RAG chunks used as context for the response    |

---

#### 3.2 Get All Sessions

Retrieve all chat sessions for the current user.

| Property   | Value              |
|------------|--------------------|
| **URL**    | `/chat/sessions`   |
| **Method** | `GET`              |
| **Auth**   | Bearer Token       |

**Query Parameters:**

| Param  | Type      | Default | Description                |
|--------|-----------|---------|----------------------------|
| `skip` | `integer` | 0       | Number of sessions to skip |
| `limit`| `integer` | 50      | Max sessions to return (1-100) |

**Success Response (200 OK):**

```json
{
  "message": "Sessions retrieved successfully",
  "data": [
    {
      "id": "e1479787-7c18-4072-9d16-04ac7082fef9",
      "title": "What are my rights if my employer...",
      "created_at": "2026-01-03T15:14:11.250260",
      "updated_at": "2026-01-03T15:14:23.424919",
      "message_count": 4
    }
  ]
}
```

---

#### 3.3 Get Session with Messages

Retrieve a specific session with complete message history.

| Property   | Value                         |
|------------|-------------------------------|
| **URL**    | `/chat/sessions/{session_id}` |
| **Method** | `GET`                         |
| **Auth**   | Bearer Token                  |

**Path Parameters:**

| Param       | Type     | Description          |
|-------------|----------|----------------------|
| `session_id`| `string` | UUID of the session  |

**Success Response (200 OK):**

```json
{
  "message": "Session retrieved successfully",
  "data": {
    "id": "e1479787-7c18-4072-9d16-04ac7082fef9",
    "title": "What are my rights...",
    "created_at": "2026-01-03T15:14:11.250260",
    "updated_at": "2026-01-03T15:14:23.424919",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "What are my rights...",
        "created_at": "2026-01-03T15:14:11.250260",
        "context_chunks": null
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Based on the legal provisions...",
        "created_at": "2026-01-03T15:14:23.424919",
        "context_chunks": ["Section 92...", "..."]
      }
    ]
  }
}
```

---

#### 3.4 Update Session (Rename)

Rename a chat session.

| Property   | Value                         |
|------------|-------------------------------|
| **URL**    | `/chat/sessions/{session_id}` |
| **Method** | `PUT`                         |
| **Auth**   | Bearer Token                  |

**Request Body:**

```json
{
  "title": "Employment Certificate Rights"
}
```

**Success Response (200 OK):**

```json
{
  "message": "Session updated successfully",
  "data": {
    "id": "e1479787-7c18-4072-9d16-04ac7082fef9",
    "title": "Employment Certificate Rights",
    "updated_at": "2026-01-03T16:00:00.000000"
  }
}
```

---

#### 3.5 Delete Session

Delete a chat session and all its messages.

| Property   | Value                         |
|------------|-------------------------------|
| **URL**    | `/chat/sessions/{session_id}` |
| **Method** | `DELETE`                      |
| **Auth**   | Bearer Token                  |

**Success Response (200 OK):**

```json
{
  "message": "Session deleted successfully",
  "data": []
}
```

---

#### 3.6 Rebuild RAG Index

Rebuild the knowledge base index from documents.

| Property   | Value                  |
|------------|------------------------|
| **URL**    | `/chat/rebuild-index`  |
| **Method** | `POST`                 |
| **Auth**   | Bearer Token           |

> **Note:** Use after adding/removing documents from the `docs/` folder.

**Success Response (200 OK):**

```json
{
  "message": "RAG index rebuilt successfully",
  "data": []
}
```

---

#### 3.7 Test RAG Search (Debug)

Test RAG search and view relevance scores. Useful for tuning.

| Property   | Value                |
|------------|----------------------|
| **URL**    | `/chat/test-search`  |
| **Method** | `POST`               |
| **Auth**   | Bearer Token         |

**Query Parameters:**

| Param      | Type    | Default | Description                        |
|------------|---------|---------|-------------------------------------|
| `query`    | `string`| -       | Search query (required)             |
| `k`        | `int`   | 6       | Number of chunks to retrieve (1-20) |
| `threshold`| `float` | 0.7     | Minimum similarity score (0-1)      |

**Success Response (200 OK):**

```json
{
  "message": "Found 6 chunks, 3 passed threshold",
  "data": {
    "query": "certificate retention by employer",
    "threshold": 0.7,
    "total_chunks": 6,
    "filtered_chunks": 3,
    "results": [
      {
        "content": "Section 92. Public charities...",
        "similarity_score": 0.8234,
        "source": "THE CODE OF CIVIL PROCEDURE, 1908.pdf"
      },
      {
        "content": "may be executed in India...",
        "similarity_score": 0.7891,
        "source": "THE CODE OF CIVIL PROCEDURE, 1908.pdf"
      }
    ]
  }
}
```

**Similarity Score Guide:**

| Score | Interpretation |
|-------|----------------|
| 0.9+  | Highly relevant |
| 0.7-0.9 | Relevant |
| 0.5-0.7 | Somewhat relevant |
| <0.5  | Likely irrelevant |

---

---

#### 3.8 Upload Document for Chat (Integrated)

Upload a document specifically for chat context. Indexes it immediately.

| Property   | Value               |
|------------|---------------------|
| **URL**    | `/chat/upload`      |
| **Method** | `POST`              |
| **Auth**   | Bearer Token        |
| **Content-Type** | `multipart/form-data` |

**Query Parameters:**

| Param        | Type     | Description                     |
|--------------|----------|---------------------------------|
| `session_id` | `string` | Optional session ID to associate|

**Request Body:**

| Field  | Type   | Required | Description                     |
|--------|--------|----------|---------------------------------|
| `file` | `file` | Yes      | PDF, Image, or Text file        |

**Success Response (200 OK):**

```json
{
  "message": "Document uploaded and processed for chat.",
  "data": {
    "document_id": "uuid-of-document",
    "filename": "contract.pdf",
    "indexing_status": "success",
    "session_id": "optional-session-id"
  }
}
```

---

### 4. User Documents & Analysis

Endpoints for managing user-uploaded documents and performing specialized analysis.

#### 4.1 Upload Document

General purpose document upload.

| Property   | Value               |
|------------|---------------------|
| **URL**    | `/uploads/upload`   |
| **Method** | `POST`              |
| **Auth**   | Bearer Token        |
| **Content-Type** | `multipart/form-data` |

**Request Body:**

| Field  | Type   | Required | Description                     |
|--------|--------|----------|---------------------------------|
| `file` | `file` | Yes      | PDF, Image, or Text file        |

**Success Response (200 OK):**

```json
{
  "message": "File uploaded successfully",
  "data": {
    "id": "uuid-of-document",
    "filename": "contract.pdf",
    "file_type": "application/pdf",
    "file_size": 10240,
    "created_at": "2026-01-26T12:00:00"
  }
}
```

---

#### 4.2 Analyze Loopholes

Analyze an uploaded document for risks and loopholes.

| Property   | Value                                   |
|------------|-----------------------------------------|
| **URL**    | `/uploads/{document_id}/analyze-loopholes` |
| **Method** | `POST`                                  |
| **Auth**   | Bearer Token                            |

**Request Body:**

```json
{
  "custom_instructions": "Check for liability clauses related to termination."
}
```

**Success Response (200 OK):**

```json
{
  "message": "Analysis completed successfully",
  "data": {
    "document_id": "uuid-of-document",
    "analysis": "The document is a standard lease agreement...",
    "concerns": [
      "Clause 5.2 imposes uncapped liability on the tenant."
    ],
    "loopholes": [
      "No specified timeline for returning the security deposit."
    ],
    "created_at": "2026-01-26T12:00:00"
  }
}
```

---

#### 4.3 List Uploaded Documents

| Property   | Value               |
|------------|---------------------|
| **URL**    | `/uploads/`         |
| **Method** | `GET`               |
| **Auth**   | Bearer Token        |

---

#### 4.4 Get Document Details

| Property   | Value                     |
|------------|---------------------------|
| **URL**    | `/uploads/{document_id}`  |
| **Method** | `GET`                     |
| **Auth**   | Bearer Token              |

---

#### 4.5 Delete Document

| Property   | Value                     |
|------------|---------------------------|
| **URL**    | `/uploads/{document_id}`  |
| **Method** | `DELETE`                  |
| **Auth**   | Bearer Token              |

---

## Error Handling

All errors follow the standard response format:

```json
{
  "message": "Error description",
  "data": []
}
```

### HTTP Status Codes

| Code | Description                                      |
|------|--------------------------------------------------|
| 200  | Success                                          |
| 201  | Created (e.g., new user registered)              |
| 400  | Bad Request (invalid input or business logic)    |
| 401  | Unauthorized (missing token)                     |
| 403  | Forbidden (invalid/expired token or access denied) |
| 404  | Not Found                                        |
| 422  | Validation Error (invalid request format)        |
| 429  | Rate Limited (LLM provider limit)                |
| 500  | Internal Server Error                            |

### Validation Error Format

```json
{
  "message": "Validation Error",
  "data": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

---

## Quick Start Examples

### JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api';
let authToken = null;

// Sign Up
async function signUp(fullName, email, password) {
  const response = await fetch(`${BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      full_name: fullName,
      email: email,
      password: password,
      confirm_password: password,
    }),
  });
  return response.json();
}

// Login
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });
  const result = await response.json();
  if (result.access_token) {
    authToken = result.access_token;
  }
  return result;
}

// Get Profile
async function getProfile() {
  const response = await fetch(`${BASE_URL}/users/me`, {
    headers: { 'Authorization': `Bearer ${authToken}` },
  });
  return response.json();
}

// Send Chat Message
async function sendMessage(message, sessionId = null) {
  const response = await fetch(`${BASE_URL}/chat/send`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
    }),
  });
  return response.json();
}

// Get Chat Sessions
async function getChatSessions() {
  const response = await fetch(`${BASE_URL}/chat/sessions`, {
    headers: { 'Authorization': `Bearer ${authToken}` },
  });
  return response.json();
}

// Get Session Messages
async function getSessionMessages(sessionId) {
  const response = await fetch(`${BASE_URL}/chat/sessions/${sessionId}`, {
    headers: { 'Authorization': `Bearer ${authToken}` },
  });
  return response.json();
}

// Delete Session
async function deleteSession(sessionId) {
  const response = await fetch(`${BASE_URL}/chat/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${authToken}` },
  });
  return response.json();
}
```

### Usage Example

```javascript
// Complete flow
await signUp('John Doe', 'john@example.com', 'password123');
await login('john@example.com', 'password123');

// Start a new chat
const chat1 = await sendMessage('What is Section 80 of CPC?');
console.log('Session:', chat1.data.session_id);
console.log('AI Response:', chat1.data.assistant_message.content);
console.log('Context Used:', chat1.data.context_chunks);

// Continue the conversation
const chat2 = await sendMessage('Explain in simpler terms', chat1.data.session_id);

// Get all sessions
const sessions = await getChatSessions();
console.log('Your sessions:', sessions.data);
```

---

## Interactive Documentation

For interactive API testing, visit the auto-generated Swagger UI:

**URL:** `http://localhost:8000/docs`

This provides a fully interactive interface to test all endpoints directly in the browser.

---

## Rate Limiting

The LLM providers may rate-limit requests:

- **OpenRouter**: Has request limits per minute
- **OpenAI**: Based on your API plan
- **Gemini**: Based on your Google Gen AI usage tier

When rate-limited (429 error), the system will:
1. Attempt fallback to OpenAI (if configured)
2. Return a friendly "rate-limited" message

---

## System Knowledge Base

### Adding Documents

1. Place PDF or TXT files in the `docs/` folder
2. Call `POST /chat/rebuild-index` to update the knowledge base
3. New documents will be chunked, embedded, and indexed

### Supported Formats

- PDF files (`.pdf`)
- Text files (`.txt`)

### Best Practices

- Use focused, relevant legal documents
- Keep documents under 50 pages for faster processing
- Rebuild index after any document changes
