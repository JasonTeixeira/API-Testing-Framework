# 🚀 Advanced API Testing Framework

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/pytest-7.4.3-yellow.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **Enterprise-grade API testing framework demonstrating BOTH API development AND comprehensive testing skills**

A production-ready project showcasing **full-stack QA capabilities**: building a FastAPI application from scratch AND implementing an advanced testing framework with authentication, retry logic, and comprehensive reporting.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Running the API](#-running-the-api)
- [Running Tests](#-running-tests)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Testing Strategies](#-testing-strategies)
- [Skills Demonstrated](#-skills-demonstrated)

---

## 🎯 Overview

This project demonstrates **dual expertise**:

1. **API Development**: Complete FastAPI application with JWT authentication, CRUD operations, and production-grade features
2. **API Testing**: Comprehensive testing framework with custom client, retry logic, and advanced test patterns

**Perfect for QA roles** that value understanding both sides of the API testing equation!

---

## ✨ Key Features

### 🏗️ **FastAPI Application** (1,580+ lines)

- ✅ **JWT Authentication** - Secure token-based auth with OAuth2
- ✅ **User Management** - Full CRUD operations
- ✅ **Pydantic Validation** - Schema validation with detailed errors
- ✅ **SQLAlchemy ORM** - Database operations with migrations
- ✅ **Rate Limiting** - Custom middleware (100 req/min)
- ✅ **Request Timing** - Performance monitoring headers
- ✅ **Error Handling** - Comprehensive exception handlers
- ✅ **CORS & Security** - Production-ready middleware
- ✅ **Auto Documentation** - OpenAPI/Swagger docs
- ✅ **Structured Logging** - Detailed logs with Loguru

### 🧪 **Testing Framework** (460+ lines)

- ✅ **Custom API Client** - Intelligent HTTP wrapper
- ✅ **Retry Logic** - Exponential backoff (3 retries)
- ✅ **Auth Management** - Token handling & refresh
- ✅ **Response Timing** - Performance assertions
- ✅ **Pytest Fixtures** - Reusable test components
- ✅ **Test Markers** - Categorized test execution
- ✅ **Logging Integration** - Detailed request/response logs
- ✅ **Context Managers** - Proper resource cleanup

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  TESTING LAYER                       │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ API Tests │  │ Integration  │  │ Performance  │ │
│  └───────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                FRAMEWORK LAYER                       │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  API Client  │  │  Validators │  │  Utilities │ │
│  │  (400 lines) │  │             │  │            │ │
│  └──────────────┘  └─────────────┘  └────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                   API LAYER                          │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │   Routes   │  │    Auth     │  │   Database   │ │
│  │ (460 lines)│  │ (300 lines) │  │ (350 lines)  │ │
│  └────────────┘  └─────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                 DATABASE LAYER                       │
│  ┌─────────────────────────────────────────────┐    │
│  │  SQLite (Dev) / PostgreSQL (Prod)          │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Virtual environment**: Recommended

```bash
# Verify Python
python --version  # Should be 3.8+

# Verify pip
pip --version
```

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/JasonTeixeira/API-Testing-Framework.git
cd API-Testing-Framework
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### Start the API Server

```bash
# Start FastAPI server
python -m api_app.main

# Server runs at: http://localhost:8000
# API Docs at: http://localhost:8000/docs
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific markers
pytest -m smoke
pytest -m auth
```

---

## 🏃 Running the API

### Start Development Server

```bash
python -m api_app.main
```

or

```bash
uvicorn api_app.main:app --reload --port 8000
```

### Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Test Users (Auto-seeded)

| Username | Password | Role |
|----------|----------|------|
| admin | Admin123! | Superuser |
| testuser | Test123! | Regular User |
| john_doe | John123! | Regular User |

---

## 🧪 Running Tests

### Basic Test Execution

```bash
# All tests
pytest

# Verbose output
pytest -v -s

# Specific test file
pytest tests/api/test_auth.py

# Specific test
pytest tests/api/test_auth.py::TestAuthentication::test_login_success
```

### Test Markers

```bash
# Smoke tests only
pytest -m smoke

# Authentication tests
pytest -m auth

# Integration tests
pytest -m integration

# Performance tests
pytest -m performance
```

### Advanced Options

```bash
# With coverage
pytest --cov=framework --cov-report=html

# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Re-run failures
pytest --lf
```

---

## 📁 Project Structure

```
API-Testing-Framework/
│
├── api_app/                     # FastAPI Application (1,580+ lines)
│   ├── main.py                 # App entry point (350 lines)
│   ├── models/
│   │   └── user.py             # User models (120 lines)
│   ├── auth/
│   │   └── security.py         # JWT & auth (300 lines)
│   ├── database/
│   │   └── database.py         # SQLAlchemy setup (350 lines)
│   └── routes/
│       ├── auth.py             # Auth endpoints (180 lines)
│       └── users.py            # User CRUD (280 lines)
│
├── framework/                   # Testing Framework (460+ lines)
│   ├── clients/
│   │   └── api_client.py       # API client (400 lines)
│   ├── utils/                  # Test utilities
│   └── schemas/                # Response schemas
│
├── tests/                       # Test Suites
│   ├── api/
│   │   └── test_auth.py        # Auth tests (60 lines)
│   ├── integration/            # Integration tests
│   └── performance/            # Performance tests
│
├── config/                      # Configuration files
├── logs/                       # Application logs
├── requirements.txt            # Dependencies (40+ packages)
├── pytest.ini                  # Pytest configuration
└── README.md                   # This file
```

**Total Lines of Code: 2,040+** 🎉

---

## 📚 API Documentation

### Authentication Endpoints

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### User Endpoints

```http
GET    /api/v1/users/
GET    /api/v1/users/me
GET    /api/v1/users/{id}
GET    /api/v1/users/count
PUT    /api/v1/users/me
PUT    /api/v1/users/{id}
DELETE /api/v1/users/{id}
POST   /api/v1/users/{id}/activate
POST   /api/v1/users/{id}/deactivate
```

### Example: Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "New User"
  }'
```

### Example: Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test123!"
```

---

## 🎓 Testing Strategies

### 1. **Unit Testing**
- Individual endpoint validation
- Schema validation
- Error handling

### 2. **Integration Testing**
- End-to-end user flows
- Database interactions
- Authentication flows

### 3. **Performance Testing**
- Response time assertions
- Rate limit testing
- Load testing with Locust

### 4. **Security Testing**
- Authentication bypass attempts
- SQL injection prevention
- XSS prevention

---

## 💡 Skills Demonstrated

### 🐍 **Python Mastery**
- Advanced OOP patterns
- Type hints throughout
- Context managers
- Decorators
- Async/await

### 🔐 **Security**
- JWT implementation
- Password hashing (bcrypt)
- OAuth2 flows
- Rate limiting
- CORS configuration

### 🗄️ **Database**
- SQLAlchemy ORM
- Database migrations
- CRUD operations
- Query optimization

### ⚡ **FastAPI Expertise**
- Dependency injection
- Middleware creation
- Exception handling
- Background tasks
- Lifespan events

### 🧪 **Testing Excellence**
- Custom test framework
- Retry mechanisms
- Fixture design
- Parameterized tests
- Performance assertions

### 📊 **DevOps Ready**
- Docker support
- CI/CD integration
- Logging & monitoring
- Configuration management

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 👨‍💻 Author

**Jason Teixeira**
- GitHub: [@JasonTeixeira](https://github.com/JasonTeixeira)
- Email: sage@sageideas.org

---

## 🌟 Project Highlights

- **2,040+ lines** of production code
- **Full-stack approach**: Build AND test
- **Production-ready** architecture
- **Comprehensive documentation**
- **Industry best practices**
- **Interview-ready** demonstration

---

## 📈 What Makes This Special

### For QA Engineers:
- Demonstrates deep understanding of APIs
- Shows ability to build, not just test
- Advanced testing patterns
- Production-grade code quality

### For Hiring Managers:
- Complete, working application
- Well-documented and maintainable
- Demonstrates senior-level skills
- Ready for immediate review

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**[Report Bug](https://github.com/JasonTeixeira/API-Testing-Framework/issues)** · **[Request Feature](https://github.com/JasonTeixeira/API-Testing-Framework/issues)**

Made with ❤️ by Jason Teixeira

</div>
