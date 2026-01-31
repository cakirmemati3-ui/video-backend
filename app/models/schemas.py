"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List
from datetime import datetime


class VideoInfoRequest(BaseModel):
    """Request model for video info"""
    url: str = Field(..., description="Video URL (Instagram, TikTok, YouTube)")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        v = v.strip()
        if not v:
            raise ValueError("URL boş olamaz")
        
        # Check if URL contains supported platforms
        supported = ['instagram.com', 'tiktok.com', 'youtube.com', 'youtu.be', 'instagr.am']
        if not any(platform in v.lower() for platform in supported):
            raise ValueError("Sadece Instagram, TikTok ve YouTube linkleri destekleniyor")
        
        return v


class VideoFormat(BaseModel):
    """Video format information"""
    format_id: str
    format_note: Optional[str] = None
    ext: str
    quality: Optional[str] = None
    filesize: Optional[int] = None
    filesize_mb: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None


class VideoInfoResponse(BaseModel):
    """Response model for video info"""
    success: bool = True
    title: str = Field(..., description="Video başlığı")
    duration: Optional[float] = Field(None, description="Video süresi (saniye)")
    duration_string: Optional[str] = Field(None, description="Formatlanmış süre (00:00)")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    direct_url: str = Field(..., description="Direkt indirme linki")
    platform: str = Field(..., description="Platform (Instagram/TikTok/YouTube)")
    uploader: Optional[str] = Field(None, description="Yükleyen kişi/kanal")
    view_count: Optional[int] = Field(None, description="Görüntülenme sayısı")
    like_count: Optional[int] = Field(None, description="Beğeni sayısı")
    description: Optional[str] = Field(None, description="Video açıklaması")
    filesize_mb: Optional[float] = Field(None, description="Dosya boyutu (MB)")
    resolution: Optional[str] = Field(None, description="Çözünürlük (1080p, 720p, vs.)")
    ext: str = Field(default="mp4", description="Dosya uzantısı")
    formats: Optional[List[VideoFormat]] = Field(None, description="Mevcut formatlar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "title": "Amazing TikTok Video",
                "duration": 45,
                "duration_string": "00:45",
                "thumbnail": "https://example.com/thumb.jpg",
                "direct_url": "https://example.com/video.mp4",
                "platform": "TikTok",
                "uploader": "cool_user",
                "view_count": 10000,
                "filesize_mb": 5.2,
                "resolution": "1080p",
                "ext": "mp4"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid URL",
                "detail": "Hacı bu link sorunlu görünüyor",
                "timestamp": "2024-01-31T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
