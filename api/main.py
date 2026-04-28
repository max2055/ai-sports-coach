"""FastAPI application entry point for AI Tennis Coach API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analysis, charts, frames, upload

app = FastAPI(
    title="AI Tennis Coach API",
    version="1.0.0",
    description="API for uploading and analyzing tennis training videos",
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(frames.router, prefix="/api", tags=["frames"])
app.include_router(charts.router, prefix="/api", tags=["charts"])


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
