from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from .api.v1.routers import tools, health
from .core.exceptions.base import AppException
from .core.exceptions.handlers import app_exception_handler,validation_exception_handler,python_exception_handler

from .infrastructure.database.mongodb import close_mongodb_connection

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="CloudSnippet API",
    description="A modern API for managing code snippets and tools",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
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

# API v1 router
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(tools.router)
v1_router.include_router(health.router)

# Include versioned API router
app.include_router(v1_router)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb_connection()

@app.get("/")
async def root():
    return {
        "message": "Welcome to CloudSnippet API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }
