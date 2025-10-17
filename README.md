# SRKNote

SRKNote is a secure, full-featured note-taking web application built with **FastAPI** and **PostgreSQL**.  
It allows users to create, encrypt, view, update, and delete personal notes safely.  

---

## Table of Contents
1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Environment Configuration](#environment-configuration)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Usage Examples](#usage-examples)
9. [Logging](#logging)
10. [Security](#security)
11. [License](#license)

---

## Features
- **User Management**
  - Register, login, and logout
  - Secure password hashing
  - JWT-based authentication
- **Notes Management**
  - Create, read, update, and delete notes
  - Optional user-provided encryption key or default server key
  - Prevent duplicate notes with same encryption key per user
- **Security**
  - AES-style encryption for note content
  - JWT authentication and token validation
  - Password hashing using Argon2, bcrypt, and PBKDF2
- **Logging**
  - Middleware logs all requests and responses
  - Sensitive data (passwords, tokens) is masked

---

## Project Structure
```

srknote/                        # Root folder of the project
├── src/
│   └── srknote/                # Main application code
│       ├── config/             # Configuration & settings
│       │   ├── base.py           # SQLAlchemy base class
│       │   ├── db.py             # Database connection/session
│       │   ├── security.py       # Hashing, JWT, encryption/decryption
│       │   └── config.py         # App settings from .env
│       ├── models/             # SQLAlchemy models
│       │   ├── User.py           # User table/model
│       │   └── Note.py           # Note table/model
│       ├── repository/         # Database access layer
│       │   ├── BaseRepository.py # Generic repository for CRUD
│       │   ├── UserRepository.py # User-specific queries
│       │   └── NoteRepository.py # Note-specific queries
│       ├── Schemas/            # Pydantic schemas
│       │   └── Schemas.py        # Request & response validation
│       ├── api/            # API endpoints
│       │   ├── auth.py           # Register & login endpoints
│       │   ├── user.py           # User profile endpoints
│       │   └── note.py           # Note CRUD endpoints
│       ├── logger.py           # Request/response logging
│       └── main.py             # FastAPI app initialization
├── logs/                       # Logs folder (not committed to GitHub)
│   └── log.log                  # Application logs
├── .github/                     # GitHub-specific configuration
│   └── workflows/               # CI/CD workflows
│       └── deploy.yml           # Deployment workflow for GitHub Actions
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Multi-container setup
├── pyproject.toml               # Poetry dependencies and scripts
├── requirements.txt             # Optional pip requirements
├── .env                         # Environment variables (secret)
└── README.md                    # Project documentation and setup instruction
```

---

## Technologies Used
- **Backend**: Python 3.10, FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: OAuth2 with JWT
- **Encryption**: Fernet (cryptography)
- **Logging**: Python `logging` module with masked sensitive info
- **Containerization**: Docker, Docker Compose
- **Package Management**: Poetry

---

## Installation

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional, recommended)
- Poetry (optional)

### Using Docker Compose
```bash
# Build and start containers
docker-compose up --build
```

### Using Local Python Environment
```bash
# Clone the repository
git clone <repo-url>
cd srknote

# Install dependencies
poetry install
# or
pip install -r requirements.txt

# Start the FastAPI server
uvicorn src.srknote.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Configuration

Create a `.env` file in the root directory with the following:

```env
DB_USER=postgres
DB_PASSWORD=Demon
DB_HOST=postgres
DB_PORT=5432
DB_NAME=srknotesapp-db
ENC_KEY=password

JWT_SECRET=Add your JWT Secret key
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Note**: Replace `JWT_SECRET` with a strong, unique secret key.

---

## Running the Application

Once the server is running, visit:

- **API Docs (Swagger UI):** `http://localhost:8000/mc101docs`



---

## API Endpoints

### Authentication
- `POST /api/v1/users/register` → Register new user
- `POST /api/v1/users/login` → Login and receive JWT
- `POST /api/v1/users/logout` → Logout (client-side)

### User Operations
- `GET /api/v1/users/check-login` → Check login status
- `PATCH /api/v1/users/` → Update user profile
- `DELETE /api/v1/users/` → Delete user account

### Note Operations
- `POST /api/v1/notes/` → Create a new note
- `GET /api/v1/notes/` → List all notes for user
- `GET /api/v1/notes/{note_id}` → Access a single note
- `PATCH /api/v1/notes/{note_id}` → Edit a note
- `DELETE /api/v1/notes/{note_id}` → Delete a note

---

## Usage Examples

### Create a Note
```json
POST /api/v1/notes/
{
  "title": "My First Note",
  "content": "This is an encrypted note.",
  "user_enc": true,
  "enc_key": "user-secret-key"
}
```

### Retrieve a Note
```bash
GET /api/v1/notes/1?enc_key=user-secret-key
```

### Update a Note
```json
PUT /api/v1/notes/1
{
  "title": "Updated Title",
  "content": "Updated content",
  "enc_key": "user-secret-key"
}
```

### Delete a Note
```bash
DELETE /api/v1/notes/1
```

---

## Logging

- Requests and responses are logged with timestamps and processing time.
- Sensitive fields like passwords, JWT tokens, or API keys are masked.

---

## Security

- Passwords are hashed with **Argon2**, **bcrypt**, and **PBKDF2**.
- Notes are encrypted using **Fernet symmetric encryption**.
- JWT tokens are used for secure authentication and access control.
- Duplicate encryption keys per user are prohibited to prevent accidental data leaks.

---

