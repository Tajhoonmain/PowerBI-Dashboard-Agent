"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.connection import init_db
from backend.api.routes import upload, transform, dashboard, agent

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="BI Dashboard Agent API",
    description="Free, open-source BI dashboard with AI agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(transform.router)
app.include_router(dashboard.router)
app.include_router(agent.router)

# Frontend router
from backend.api.routes import frontend
app.include_router(frontend.router)

# Export router
from backend.api.routes import export
app.include_router(export.router)

# Evaluation router
from backend.api.routes import evaluation
app.include_router(evaluation.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "BI Dashboard Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

