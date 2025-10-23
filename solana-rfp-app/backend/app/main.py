from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.core.config import settings
from app.core.database import engine, Base
from app.api import knowledge, questions, auth, export

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Continue anyway - tables might already exist

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
        # Return a simple HTML page if frontend is not built yet
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Solana RFP Database</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { max-width: 600px; margin: 0 auto; }
                .loading { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Solana RFP Database</h1>
                <p class="loading">Frontend is being built... Please wait a moment and refresh the page.</p>
                <p><a href="/docs">API Documentation</a></p>
                <script>
                    setTimeout(() => window.location.reload(), 5000);
                </script>
            </div>
        </body>
        </html>
        """

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
        # Redirect to root if frontend not built
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Solana RFP Database</title>
            <script>window.location.href = '/';</script>
        </head>
        <body>
            <p>Redirecting...</p>
        </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
