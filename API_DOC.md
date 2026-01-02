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
```

---

## Interactive Documentation

For interactive API testing, visit the auto-generated Swagger UI:

**URL:** `http://localhost:8000/docs`

This provides a fully interactive interface to test all endpoints directly in the browser.
