from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.core.config import settings
from app.core.database import engine, Base
from app.api import knowledge, questions, auth, export

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

# Serve static files from frontend build
frontend_build_path = os.path.join(os.path.dirname(__file__), "../../../frontend/build")
if os.path.exists(frontend_build_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_path, "static")), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "solana-rfp-api"}

@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    frontend_build_path = os.path.join(os.path.dirname(__file__), "../../../frontend/build")
    index_file = os.path.join(frontend_build_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {
            "message": "Solana RFP Database API",
            "version": "1.0.0",
            "docs": "/docs"
        }

@app.get("/{full_path:path}")
async def serve_frontend_catch_all(full_path: str):
    """Catch-all route to serve React frontend for client-side routing"""
    # Don't serve frontend for API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
        return {"error": "Not found"}
    
    frontend_build_path = os.path.join(os.path.dirname(__file__), "../../../frontend/build")
    index_file = os.path.join(frontend_build_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {"error": "Frontend not built"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
