from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import knowledge, questions, auth, export
from app.core.startup import initialize_application
from app.core.logger import main_logger

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered RFP question answering system for Solana",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        main_logger.info("Starting Solana RFP Tool API...")
        initialize_application()
        main_logger.info("API startup complete")
    except Exception as e:
        main_logger.error(f"Failed to start API: {str(e)}")
        raise

# Backend-only: No frontend static files

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "solana-rfp-api"}

@app.get("/")
async def root():
    return {
        "message": "Solana RFP Database API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "Backend API is running"
    }

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route for unknown paths"""
    return {"error": "Not found", "path": full_path, "message": "This is a backend API only"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
