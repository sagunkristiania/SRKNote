"""
main.py
-------
Entry point for the SRKNote FastAPI application.

This file initializes the FastAPI app, sets up middleware,
database tables, routers, logging, and provides root, health,
and custom Swagger UI endpoints.

Swagger UI is disabled by default and only available at /mc101docs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

# Import routers and logging from SRKNote package
from .api.auth import router as auth_router
from .api.note import router as notes_router
from .api.user import router as user_router
from .logger.logger import log_requests

from .config.base import Base
from .config.db import get_engine

# ---------------------------
# Database Initialization
# ---------------------------
# Create all tables in the database if they don't exist
Base.metadata.create_all(bind=get_engine())

# ---------------------------
# FastAPI App Initialization
# ---------------------------
# Disable default Swagger (/docs) and ReDoc (/redoc)
app = FastAPI(
    title="SRKNote API",
    description="Secure Note Taking API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# ---------------------------
# Middleware
# ---------------------------
# Enable CORS for all origins, headers, and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Add request/response logging middleware
app.middleware("http")(log_requests)

# ---------------------------
# Routers
# ---------------------------
# Include authentication, notes, and user endpoints
app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(user_router)

# ---------------------------
# Root & Health Endpoints
# ---------------------------
@app.get("/", tags=["root"])
async def root():
    """Root endpoint to verify that the API is running."""
    return {"message": "API is running"}

@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint to confirm API is operational."""
    return {"ok": True}

# ---------------------------
# Custom Swagger UI
# ---------------------------
@app.get("/mc101docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Serve the Swagger UI documentation at /mc101docs.

    The default /docs and /redoc endpoints are disabled.
    """
    return get_swagger_ui_html(openapi_url="/openapi.json", title="MC101 API Docs")

# ----------------------------
# Optional: Run with Uvicorn
# ----------------------------
# Uncomment to run directly
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
