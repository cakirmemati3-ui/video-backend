"""
🔥 VIDEO DOWNLOADER PRO - MAIN APPLICATION
Instagram, TikTok, YouTube Video Downloader API

Author: Elite Full-Stack Developer
Tech Stack: FastAPI + yt-dlp
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sys
from datetime import datetime

from app.config import settings
from app.api.routes import download
from app.utils.exceptions import VideoDownloaderException
from app.models.schemas import ErrorResponse


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level=settings.LOG_LEVEL
)


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🚀 **Video Downloader Pro API**
    
    Professional video downloader supporting:
    - 📸 **Instagram** (Reels, Posts, Stories, IGTV)
    - 🎵 **TikTok** (Watermark-free downloads!)
    - 🎥 **YouTube** (Videos & Shorts, multiple qualities)
    
    ## Features
    - ⚡ Lightning fast async processing
    - 🎯 Smart format selection (TikTok watermark-free)
    - 🛡️ Enterprise-level error handling
    - 🔒 Rate limiting & security
    - 📊 Detailed video metadata
    
    ## Usage
    Send POST or GET request to `/api/fetch` with video URL.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# RATE LIMITING
# ============================================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CUSTOM EXCEPTION HANDLERS
# ============================================================================
@app.exception_handler(VideoDownloaderException)
async def video_downloader_exception_handler(request: Request, exc: VideoDownloaderException):
    """Handle custom video downloader exceptions"""
    logger.warning(f"VideoDownloaderException: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            detail=str(exc.detail),
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            error="Geçersiz istek formatı",
            detail=str(exc.errors()),
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded from IP: {get_remote_address(request)}")
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            success=False,
            error="Çok fazla istek!",
            detail="Yavaş abi! Dakikada en fazla 30 istek atabilirsin. Biraz bekle.",
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Sunucu hatası",
            detail="Beklenmeyen bir hata oluştu. Geliştiriciler bilgilendirildi.",
            timestamp=datetime.utcnow()
        ).model_dump()
    )


# ============================================================================
# MIDDLEWARE
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path} from {get_remote_address(request)}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    return response


# ============================================================================
# ROUTES
# ============================================================================
# Include download routes
app.include_router(download.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "🔥 Video Downloader Pro API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "fetch": "/api/fetch",
            "health": "/api/health",
            "platforms": "/api/platforms"
        },
        "supported_platforms": ["Instagram", "TikTok", "YouTube"],
        "features": [
            "⚡ Async processing",
            "🎯 TikTok watermark-free",
            "📊 Detailed metadata",
            "🛡️ Rate limiting"
        ]
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.APP_VERSION
    }


# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"Allowed Origins: {settings.cors_origins}")
    logger.info(f"Rate Limit: {settings.RATE_LIMIT_PER_MINUTE}/min per IP")
    logger.info(f"Max File Size: {settings.MAX_DOWNLOAD_SIZE_MB}MB")
    logger.info("=" * 80)
    logger.success("✅ Application started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("=" * 80)
    logger.warning("🛑 Shutting down application...")
    logger.info("=" * 80)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
