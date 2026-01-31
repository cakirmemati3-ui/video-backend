"""
Custom exceptions for Video Downloader Pro
"""
from fastapi import HTTPException, status


class VideoDownloaderException(HTTPException):
    """Base exception for video downloader"""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvalidURLException(VideoDownloaderException):
    """Raised when URL is invalid or unsupported"""
    
    def __init__(self, url: str):
        super().__init__(
            detail=f"Hacı bu link sorunlu görünüyor: {url}. Instagram, TikTok veya YouTube linki olduğundan emin ol.",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class VideoUnavailableException(VideoDownloaderException):
    """Raised when video is not available or private"""
    
    def __init__(self, message: str = None):
        detail = message or "Video bulunamadı veya özel hesap. Bot engellemiş olabilir, başka link dene."
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DownloadFailedException(VideoDownloaderException):
    """Raised when download fails"""
    
    def __init__(self, message: str = None):
        detail = message or "İndirme sırasında bir hata oluştu. Link geçerli ama sunucu şu an sıkıntılı."
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RateLimitException(VideoDownloaderException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self):
        super().__init__(
            detail="Yavaş abi! Çok fazla istek attın. Birkaç saniye bekle.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class FileTooLargeException(VideoDownloaderException):
    """Raised when file size exceeds limit"""
    
    def __init__(self, size_mb: int, max_mb: int):
        super().__init__(
            detail=f"Video çok büyük ({size_mb}MB). Maksimum {max_mb}MB olmalı.",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


class TimeoutException(VideoDownloaderException):
    """Raised when download times out"""
    
    def __init__(self):
        super().__init__(
            detail="İndirme çok uzun sürdü. Daha kısa bir video dene veya tekrar deneyebilirsin.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT
        )
