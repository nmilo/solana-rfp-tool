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
    """Serve a simple API interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solana RFP Database API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            h1 { color: #333; }
            .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .api-link:hover { background: #0056b3; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Solana RFP Database API</h1>
            <p class="status">✅ Backend is running successfully!</p>
            <p>Your API is ready to use. Here are the available endpoints:</p>
            
            <h3>API Endpoints:</h3>
            <a href="/docs" class="api-link">📚 API Documentation</a>
            <a href="/health" class="api-link">❤️ Health Check</a>
            <a href="/api/v1/auth/verify-email/demo@solana.org" class="api-link">🔐 Test Auth</a>
            
            <h3>Quick Test:</h3>
            <p>Try this API call to test the system:</p>
            <code>POST /api/v1/questions/process</code>
            
            <h3>Next Steps:</h3>
            <p>1. The backend API is fully functional</p>
            <p>2. You can test all endpoints via the documentation</p>
            <p>3. Frontend can be deployed separately if needed</p>
        </div>
    </body>
    </html>
    """

@app.get("/{full_path:path}")
async def serve_frontend_catch_all(full_path: str):
    """Catch-all route - redirect to API docs for unknown paths"""
    # Don't serve frontend for API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
        return {"error": "Not found"}
    
    # Redirect to root for any other path
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solana RFP Database</title>
        <script>window.location.href = '/';</script>
    </head>
    <body>
        <p>Redirecting to API...</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
