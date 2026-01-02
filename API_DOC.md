# LegalLink API Documentation

This document provides comprehensive API documentation for frontend developers to integrate with the LegalLink backend.

**Base URL:** `http://localhost:8000/api`

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

1. Call the `/auth/login` endpoint with credentials.
2. Extract the `access_token` from the response.
3. Include the token in all protected requests:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Authentication

#### 1.1 Sign Up

Create a new user account.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/auth/signup`             |
| **Method** | `POST`                   |
| **Auth** | Not required               |

**Request Body:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "yourpassword",
  "confirm_password": "yourpassword"
}
```

| Field              | Type     | Required | Description                     |
|--------------------|----------|----------|---------------------------------|
| `full_name`        | `string` | Yes      | User's full name                |
| `email`            | `string` | Yes      | Valid email address             |
| `password`         | `string` | Yes      | Password (min 6 characters)     |
| `confirm_password` | `string` | Yes      | Must match `password`           |

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

**Error Responses:**

| Status | Message                               |
|--------|---------------------------------------|
| 400    | Passwords do not match.               |
| 400    | A user with this email already exists.|
| 422    | Validation Error                      |

---

#### 1.2 Login

Authenticate and receive a JWT token.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/auth/login`              |
| **Method** | `POST`                   |
| **Auth** | Not required               |
| **Content-Type** | `application/x-www-form-urlencoded` |

**Request Body (Form Data):**

| Field      | Type     | Required | Description           |
|------------|----------|----------|-----------------------|
| `username` | `string` | Yes      | User's email address  |
| `password` | `string` | Yes      | User's password       |

**Example (JavaScript Fetch):**

```javascript
const formData = new URLSearchParams();
formData.append('username', 'john@example.com');
formData.append('password', 'yourpassword');

const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: formData,
});
```

**Success Response (200 OK):**

```json
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Error Responses:**

| Status | Message                    |
|--------|----------------------------|
| 400    | Incorrect email or password|
| 400    | User account is inactive   |

---

### 2. User Profile

All profile endpoints require authentication.

#### 2.1 Get Current User

Retrieve the authenticated user's profile.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/users/me`                |
| **Method** | `GET`                    |
| **Auth** | Bearer Token required      |

**Success Response (200 OK):**

```json
{
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "profile_image": "static/default_headshot.png"
  }
}
```

**Error Responses:**

| Status | Message                         |
|--------|---------------------------------|
| 401    | Not authenticated               |
| 403    | Could not validate credentials  |

---

#### 2.2 Update Profile

Update the current user's profile information.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/users/me`                |
| **Method** | `PUT`                    |
| **Auth** | Bearer Token required      |

**Request Body:**

```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "newpassword",
  "confirm_password": "newpassword"
}
```

> **Note:** All fields are optional. Only include fields you want to update.

**Success Response (200 OK):**

```json
{
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "jane@example.com",
    "full_name": "Jane Doe",
    "is_active": true,
    "profile_image": "static/default_headshot.png"
  }
}
```

---

#### 2.3 Reset Password

Change the current user's password.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/users/me/reset-password` |
| **Method** | `POST`                   |
| **Auth** | Bearer Token required      |

**Request Body:**

```json
{
  "old_password": "currentpassword",
  "new_password": "newpassword123",
  "confirm_new_password": "newpassword123"
}
```

| Field                  | Type     | Required | Description                    |
|------------------------|----------|----------|--------------------------------|
| `old_password`         | `string` | Yes      | Current password for verification |
| `new_password`         | `string` | Yes      | New password to set            |
| `confirm_new_password` | `string` | Yes      | Must match `new_password`      |

**Success Response (200 OK):**

```json
{
  "message": "Password changed successfully",
  "data": []
}
```

**Error Responses:**

| Status | Message                     |
|--------|-----------------------------|
| 400    | Invalid current password    |
| 400    | New passwords do not match  |

---

#### 2.4 Update Profile Image

Upload a new profile picture.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/users/me/profile-image`  |
| **Method** | `POST`                   |
| **Auth** | Bearer Token required      |
| **Content-Type** | `multipart/form-data` |

**Request Body:**

| Field  | Type   | Required | Description          |
|--------|--------|----------|----------------------|
| `file` | `file` | Yes      | Image file to upload |

**Example (JavaScript Fetch):**

```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/api/users/me/profile-image', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
  body: formData,
});
```

**Success Response (200 OK):**

```json
{
  "message": "Profile image updated successfully",
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

### 3. Chat (RAG-Powered AI)

All chat endpoints require authentication. The chat system uses Retrieval-Augmented Generation (RAG) to provide context-aware responses.

#### 3.1 Send Message

Send a message to the AI and receive a response.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/chat/send`               |
| **Method** | `POST`                   |
| **Auth** | Bearer Token required      |

**Request Body:**

```json
{
  "message": "What are the legal requirements for starting a business?",
  "session_id": null
}
```

| Field        | Type      | Required | Description                                           |
|--------------|-----------|----------|-------------------------------------------------------|
| `message`    | `string`  | Yes      | The user's message/question                           |
| `session_id` | `integer` | No       | Existing session ID. If null, creates a new session.  |

**Success Response (200 OK):**

```json
{
  "message": "Message sent successfully",
  "data": {
    "session_id": 1,
    "user_message": {
      "id": 1,
      "role": "user",
      "content": "What are the legal requirements for starting a business?",
      "created_at": "2026-01-02T18:00:00"
    },
    "assistant_message": {
      "id": 2,
      "role": "assistant",
      "content": "Starting a business typically involves several legal requirements...",
      "created_at": "2026-01-02T18:00:05"
    }
  }
}
```

**Example (JavaScript):**

```javascript
// Start a new conversation
const response = await fetch('http://localhost:8000/api/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "What are the legal requirements for starting a business?",
    session_id: null  // null = new session
  }),
});

const result = await response.json();
const sessionId = result.data.session_id;  // Save for follow-up messages

// Continue the conversation
const followUp = await fetch('http://localhost:8000/api/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "What about tax registration?",
    session_id: sessionId  // Continue in same session
  }),
});
```

---

#### 3.2 Get All Sessions

Retrieve all chat sessions for the current user.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/chat/sessions`           |
| **Method** | `GET`                    |
| **Auth** | Bearer Token required      |

**Query Parameters:**

| Param  | Type      | Default | Description                    |
|--------|-----------|---------|--------------------------------|
| `skip` | `integer` | 0       | Number of sessions to skip     |
| `limit`| `integer` | 50      | Maximum sessions to return     |

**Success Response (200 OK):**

```json
{
  "message": "Sessions retrieved successfully",
  "data": [
    {
      "id": 2,
      "title": "Tax registration requirements...",
      "created_at": "2026-01-02T18:30:00",
      "updated_at": "2026-01-02T19:00:00"
    },
    {
      "id": 1,
      "title": "What are the legal requirements...",
      "created_at": "2026-01-02T18:00:00",
      "updated_at": "2026-01-02T18:05:00"
    }
  ]
}
```

---

#### 3.3 Get Session with Messages

Retrieve a specific session with its complete message history.

| Property | Value                         |
|----------|-------------------------------|
| **URL**  | `/chat/sessions/{session_id}` |
| **Method** | `GET`                       |
| **Auth** | Bearer Token required         |

**Success Response (200 OK):**

```json
{
  "message": "Session retrieved successfully",
  "data": {
    "id": 1,
    "title": "What are the legal requirements...",
    "created_at": "2026-01-02T18:00:00",
    "updated_at": "2026-01-02T18:05:00",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "What are the legal requirements for starting a business?",
        "created_at": "2026-01-02T18:00:00"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Starting a business typically involves...",
        "created_at": "2026-01-02T18:00:05"
      }
    ]
  }
}
```

**Error Responses:**

| Status | Message                |
|--------|------------------------|
| 404    | Chat session not found |

---

#### 3.4 Update Session (Rename)

Rename a chat session.

| Property | Value                         |
|----------|-------------------------------|
| **URL**  | `/chat/sessions/{session_id}` |
| **Method** | `PUT`                       |
| **Auth** | Bearer Token required         |

**Request Body:**

```json
{
  "title": "Business Legal Requirements"
}
```

**Success Response (200 OK):**

```json
{
  "message": "Session updated successfully",
  "data": {
    "id": 1,
    "title": "Business Legal Requirements",
    "updated_at": "2026-01-02T19:00:00"
  }
}
```

---

#### 3.5 Delete Session

Delete a chat session and all its messages.

| Property | Value                         |
|----------|-------------------------------|
| **URL**  | `/chat/sessions/{session_id}` |
| **Method** | `DELETE`                    |
| **Auth** | Bearer Token required         |

**Success Response (200 OK):**

```json
{
  "message": "Session deleted successfully",
  "data": []
}
```

---

#### 3.6 Rebuild RAG Index

Rebuild the knowledge base index from documents in the `docs` folder.

| Property | Value                      |
|----------|----------------------------|
| **URL**  | `/chat/rebuild-index`      |
| **Method** | `POST`                   |
| **Auth** | Bearer Token required      |

> **Note:** Use this after adding new documents to the `docs` folder.

**Success Response (200 OK):**

```json
{
  "message": "RAG index rebuilt successfully",
  "data": []
}
```

---

## Error Handling

All errors follow the standard response format:

```json
{
  "message": "Error description",
  "data": []
}
```

### Common HTTP Status Codes

| Code | Description                                      |
|------|--------------------------------------------------|
| 200  | Success                                          |
| 201  | Created (e.g., new user registered)              |
| 400  | Bad Request (invalid input or business logic)   |
| 401  | Unauthorized (missing or invalid token)          |
| 403  | Forbidden (token invalid or expired)             |
| 404  | Not Found                                        |
| 422  | Validation Error (invalid request body format)  |
| 500  | Internal Server Error                            |

### Validation Error Format

When a 422 error occurs, the `data` field contains validation details:

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

## Quick Start Example (JavaScript)

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
  if (result.data?.access_token) {
    authToken = result.data.access_token;
  }
  return result;
}

// Get Profile (Protected)
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
```

---

## Interactive Documentation

For interactive API testing, visit the auto-generated Swagger UI:

**URL:** `http://localhost:8000/docs`

This provides a fully interactive interface to test all endpoints directly in the browser.
