"""
API routes for video downloading
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger

from app.models.schemas import VideoInfoRequest, VideoInfoResponse, ErrorResponse
from app.core.downloader import downloader
from app.utils.exceptions import VideoDownloaderException


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Router
router = APIRouter(prefix="/api", tags=["Download"])


@router.post("/fetch", response_model=VideoInfoResponse)
@router.get("/fetch", response_model=VideoInfoResponse)
@limiter.limit("30/minute")
async def fetch_video_info(request: Request, video_request: VideoInfoRequest = None, url: str = None):
    """
    🔥 FETCH VIDEO INFO ENDPOINT
    
    Supports:
    - POST: Send JSON body with 'url' field
    - GET: Send query parameter ?url=...
    
    Returns:
    - Direct download URL
    - Video title, duration, thumbnail
    - Platform info
    - Available formats
    
    Example POST:
    ```json
    {
        "url": "https://www.tiktok.com/@user/video/123456"
    }
    ```
    
    Example GET:
    ```
    /api/fetch?url=https://www.tiktok.com/@user/video/123456
    ```
    """
    try:
        # Handle both GET and POST
        if video_request:
            video_url = video_request.url
        elif url:
            video_url = url.strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="URL gerekli. POST body'de 'url' veya GET query'de '?url=' kullan."
            )
        
        logger.info(f"Processing request for URL: {video_url}")
        
        # Get video info using our elite downloader
        info = await downloader.get_video_info(video_url)
        
        # Return standardized response
        return VideoInfoResponse(
            success=True,
            **info
        )
        
    except VideoDownloaderException as e:
        # Our custom exceptions
        logger.warning(f"Video downloader exception: {e.detail}")
        raise e
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in fetch endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sunucu hatası: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Video Downloader Pro",
        "version": "1.0.0"
    }


@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list of supported platforms
    """
    return {
        "platforms": [
            {
                "name": "Instagram",
                "supported": True,
                "types": ["Reels", "Posts", "Stories", "IGTV"]
            },
            {
                "name": "TikTok",
                "supported": True,
                "types": ["Videos"],
                "features": ["Watermark-free download"]
            },
            {
                "name": "YouTube",
                "supported": True,
                "types": ["Videos", "Shorts"],
                "features": ["Multiple quality options"]
            }
        ]
    }
