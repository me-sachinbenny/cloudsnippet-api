from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from .api.v1.routers import users
from .core.exceptions.base import AppException
from .core.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    python_exception_handler
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="User Management API",
    description="A modern API for user management with proper architecture",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)

# Include routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to User Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
