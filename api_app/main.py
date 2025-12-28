"""
FastAPI Main Application
Enterprise-grade REST API with authentication, CRUD operations, and comprehensive testing
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import time
from loguru import logger

from api_app.routes import auth, users
from api_app.database.database import init_db, seed_test_users, SessionLocal

# Configure logging
logger.add(
    "logs/api_{time}.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
)


# ============= Lifespan Events =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    
    Startup:
    - Initialize database
    - Seed test data
    
    Shutdown:
    - Close connections
    - Cleanup resources
    """
    # Startup
    logger.info("=" * 80)
    logger.info("STARTING API APPLICATION")
    logger.info("=" * 80)
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Seed test users (only in development)
        db = SessionLocal()
        try:
            seed_test_users(db)
            logger.info("Test users seeded")
        finally:
            db.close()
            
        logger.info("API startup complete")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("SHUTTING DOWN API APPLICATION")
    logger.info("=" * 80)


# ============= Application Initialization =============

app = FastAPI(
    title="QA API Testing Framework",
    description="""
    **Enterprise-grade REST API** built for comprehensive testing demonstrations.
    
    ## Features
    
    * 🔐 **JWT Authentication** - Secure token-based authentication
    * 👥 **User Management** - Full CRUD operations
    * 📊 **Request Validation** - Pydantic schema validation
    * 🚀 **Fast & Async** - Built with FastAPI for high performance
    * 📝 **Auto Documentation** - Interactive API docs
    * 🧪 **Test-Ready** - Designed for automated testing
    
    ## Authentication
    
    Most endpoints require authentication. Use `/api/v1/auth/login` to get a JWT token,
    then include it in the `Authorization` header as `Bearer <token>`.
    
    ## Rate Limiting
    
    API endpoints are rate-limited to prevent abuse. Default: 100 requests/minute.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============= Middleware Configuration =============

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify exact hosts
)


# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


# Rate Limiting Middleware (Simple Implementation)
from collections import defaultdict
from datetime import datetime, timedelta

request_counts = defaultdict(list)
RATE_LIMIT = 100  # requests
RATE_PERIOD = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Simple rate limiting middleware.
    Limits requests per IP address.
    """
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < timedelta(seconds=RATE_PERIOD)
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Try again later.",
                "limit": RATE_LIMIT,
                "period_seconds": RATE_PERIOD
            }
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = RATE_LIMIT - len(request_counts[client_ip])
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(RATE_PERIOD)
    
    return response


# ============= Error Handlers =============

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred"
        }
    )


# ============= Route Registration =============

# API v1 routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


# ============= Root & Health Endpoints =============

@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint.
    Returns API information and available endpoints.
    """
    return {
        "message": "QA API Testing Framework",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Used for monitoring and load balancer health checks.
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/api/v1/status", tags=["Status"])
async def api_status():
    """
    API status endpoint with detailed information.
    """
    from api_app.database.database import get_user_count, SessionLocal
    
    db = SessionLocal()
    try:
        total_users = get_user_count(db)
        active_users = get_user_count(db, is_active=True)
    finally:
        db.close()
    
    return {
        "api": "QA Testing Framework",
        "version": "1.0.0",
        "status": "operational",
        "database": "connected",
        "statistics": {
            "total_users": total_users,
            "active_users": active_users
        }
    }


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "api_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
