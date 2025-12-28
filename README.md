# API Testing Framework

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/pytest-7.4.3-yellow.svg)](https://pytest.org/)

> A complete API testing solution - I built the API and the testing framework

This project demonstrates something I think is important for QA engineers: understanding both sides of the equation. I built a full FastAPI application AND a comprehensive testing framework to show how APIs work from the inside out.

---

## What's This Project?

This is two things in one:

**1. A Working API**
A FastAPI application with user management, JWT authentication, and all the features you'd find in a real application. It's not just a mock - it actually works.

**2. A Testing Framework**
A custom API testing client with smart retry logic, authentication handling, and performance monitoring. Built to test the API I created, but flexible enough to test any REST API.

Why both? Because the best testers understand what they're testing. Building the API taught me what makes APIs fragile, how authentication really works, and where edge cases hide.

---

## Key Features

### The API Application

- **JWT Authentication** - Real OAuth2 implementation with token refresh
- **User Management** - Full CRUD operations (create, read, update, delete users)
- **Request Validation** - Pydantic schemas catch bad requests before they hit the database
- **Rate Limiting** - Prevents abuse with a simple middleware approach
- **Performance Monitoring** - Every response includes timing headers
- **Auto Documentation** - Swagger UI at `/docs` for interactive testing

### The Testing Framework

- **Smart API Client** - Handles authentication, retries, and logging automatically
- **Retry Logic** - Exponential backoff when requests fail
- **Token Management** - Automatically refreshes expired tokens
- **Performance Assertions** - Test response times alongside functionality
- **Flexible Fixtures** - Reusable pytest fixtures for common scenarios

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- That's it!

### Installation

```bash
# Clone and setup
git clone https://github.com/JasonTeixeira/API-Testing-Framework.git
cd API-Testing-Framework

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install everything
pip install -r requirements.txt
```

### Start the API

```bash
# Run the FastAPI server
python -m api_app.main

# API runs at: http://localhost:8000
# Check out the docs: http://localhost:8000/docs
```

The API automatically seeds some test users:
- **admin** / Admin123! (superuser)
- **testuser** / Test123! (regular user)
- **john_doe** / John123! (regular user)

### Run Tests

```bash
# Make sure the API is running first, then:
pytest

# Or with more detail:
pytest -v
```

---

## How It Works

### The API Architecture

```
API Request → Middleware → Routes → Database
                ↓
         Authentication
         Rate Limiting
         Logging
```

I kept the architecture straightforward:
- **Routes** handle incoming requests
- **Auth layer** validates JWT tokens
- **Database layer** manages SQLAlchemy operations
- **Middleware** adds cross-cutting concerns (logging, rate limiting, etc.)

### The Testing Client

The API client wraps Python's `requests` library with:
- Automatic retry on failures (with exponential backoff)
- Token management (login once, use everywhere)
- Request/response logging (debug easily)
- Performance tracking (every request is timed)

Example usage:

```python
from framework.clients.api_client import APIClient

# Create client and login
client = APIClient(base_url="http://localhost:8000")
client.login("testuser", "Test123!")

# Make authenticated requests
response = client.get("/api/v1/users/me")
assert response.status_code == 200
```

---

## Project Structure

```
API-Testing-Framework/
├── api_app/                    # The FastAPI application
│   ├── main.py                # App entry point
│   ├── models/                # Database and Pydantic models
│   ├── auth/                  # JWT and authentication
│   ├── database/              # SQLAlchemy setup
│   └── routes/                # API endpoints
│
├── framework/                  # The testing framework
│   ├── clients/               # API client wrapper
│   ├── utils/                 # Test utilities
│   └── schemas/               # Response validators
│
├── tests/                     # Test suites
│   ├── api/                   # API endpoint tests
│   ├── integration/           # Integration tests
│   └── performance/           # Performance tests
│
├── config/                    # Configuration files
└── requirements.txt           # Dependencies
```

---

## API Endpoints

### Authentication
```
POST /api/v1/auth/register     - Create new user
POST /api/v1/auth/login        - Get JWT token
POST /api/v1/auth/refresh      - Refresh expired token
```

### Users
```
GET    /api/v1/users/          - List all users
GET    /api/v1/users/me        - Get current user
GET    /api/v1/users/{id}      - Get specific user
PUT    /api/v1/users/me        - Update your profile
DELETE /api/v1/users/{id}      - Delete user (admin only)
```

Try them out at `http://localhost:8000/docs` - the Swagger UI is interactive!

---

## Design Decisions

### Why FastAPI?

It's fast, has great async support, and generates OpenAPI docs automatically. Plus, the dependency injection system makes testing easier.

### Why Build the API Too?

Testing something you built yourself teaches you:
- What makes APIs break
- How authentication flows really work
- Where race conditions hide
- Why rate limiting matters

It's way more valuable than just testing someone else's API.

### Why Custom Test Client?

Most projects need API testing at some point. I wanted something that:
- Handles authentication without repeated code
- Retries intelligently (not just blindly)
- Logs enough to debug issues fast
- Works as both a library and standalone tool

---

## What I Learned

Building this taught me:

**About APIs:**
- JWT tokens are more complex than they seem
- Rate limiting needs careful thought about edge cases
- Good logging is critical for debugging production issues
- Middleware order matters a lot

**About Testing:**
- Retry logic needs exponential backoff (not fixed delays)
- Authentication state management is tricky to test
- Performance tests need consistent environments
- Good fixtures make tests way more maintainable

---

## Running in CI/CD

Works with GitHub Actions, Jenkins, etc. Basic example:

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python -m api_app.main &
      - run: sleep 5  # Let API start
      - run: pytest -v
```

---

## Contributing

Found a bug? Have an idea? Open an issue or PR. I'm always interested in better approaches!

---

## Author

**Jason Teixeira**
- GitHub: [@JasonTeixeira](https://github.com/JasonTeixeira)
- Email: sage@sageideas.org

---

## License

MIT License - use it however you want.
