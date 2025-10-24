from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import knowledge, questions, auth, export, ai_upload
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
print(f"Setting up CORS with origins: {settings.cors_origins_list}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Manual CORS handler for debugging
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"CORS request from origin: {origin}")
    print(f"Allowed origins: {settings.cors_origins_list}")
    
    response = await call_next(request)
    
    # Add CORS headers manually if needed
    if origin in settings.cors_origins_list:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])
app.include_router(ai_upload.router, prefix="/api/v1/ai", tags=["ai-upload"])

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

@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Handle OPTIONS requests for CORS preflight"""
    origin = request.headers.get("origin")
    print(f"OPTIONS request from origin: {origin}")
    
    # Check if origin is allowed
    if origin in settings.cors_origins_list:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            }
        )
    else:
        return Response(
            status_code=403,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
            }
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "solana-rfp-api"}

@app.get("/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS test successful",
        "cors_origins": settings.cors_origins_list,
        "timestamp": "2025-01-24T15:30:00Z"
    }

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
    # Exclude static files and common frontend assets
    static_extensions = {'.json', '.js', '.css', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot'}
    if any(full_path.lower().endswith(ext) for ext in static_extensions):
        raise HTTPException(status_code=404, detail="Static file not found")
    
    return {"error": "Not found", "path": full_path, "message": "This is a backend API only"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
