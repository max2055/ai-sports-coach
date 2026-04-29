"""FastAPI application entry point for AI Tennis Coach API."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import analysis, charts, frames, history, pros, report, upload

app = FastAPI(
    title="AI Tennis Coach API",
    version="1.0.0",
    description="API for uploading and analyzing tennis training videos",
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5252,http://localhost:5173,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(frames.router, prefix="/api", tags=["frames"])
app.include_router(charts.router, prefix="/api", tags=["charts"])
app.include_router(pros.router, prefix="/api", tags=["pros"])
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(history.router, prefix="/api", tags=["history"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "ai-tennis-coach-api"}


@app.get("/")
def root() -> dict:
    """Root endpoint with API info."""
    return {
        "name": "AI Tennis Coach API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
