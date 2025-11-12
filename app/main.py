"""
FastAPI Entry Point - Production Ready
Optimized for competition with no rate limiting issues
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import router
from app.config import settings
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Quiz Solver API",
    description="Fast quiz solver - no external API calls",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Allow all for competition
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Include routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info(f"Starting Quiz Solver API on port {settings.PORT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("Shutting down Quiz Solver API")

# Health check endpoint - CRITICAL for preventing 599 errors
@app.get("/")
async def root():
    """Root endpoint - keeps service alive"""
    return {
        "status": "online",
        "service": "quiz-solver",
        "version": "2.0.0",
        "port": settings.PORT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "quiz-solver",
        "port": settings.PORT
    }

@app.get("/ping")
async def ping():
    """Ping endpoint for keep-alive"""
    return {"pong": True}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info",
        access_log=True
    )
