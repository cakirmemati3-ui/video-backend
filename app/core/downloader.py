"""
Core video downloader service using yt-dlp
The BOSS of video downloading 🔥
"""
import yt_dlp
import asyncio
from typing import Dict, Optional, List
from loguru import logger
import re
from datetime import timedelta

from app.utils.exceptions import (
    InvalidURLException,
    VideoUnavailableException,
    DownloadFailedException,
    FileTooLargeException,
    TimeoutException
)
from app.config import settings


class VideoDownloader:
    """
    Elite video downloader service
    Supports: Instagram, TikTok, YouTube
    """
    
    # Platform detection patterns
    PLATFORM_PATTERNS = {
        'instagram': r'instagram\.com|instagr\.am',
        'tiktok': r'tiktok\.com|vm\.tiktok\.com',
        'youtube': r'youtube\.com|youtu\.be'
    }
    
    def __init__(self):
        """Initialize downloader with base config"""
        self.base_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
        }
    
    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        url_lower = url.lower()
        
        for platform, pattern in self.PLATFORM_PATTERNS.items():
            if re.search(pattern, url_lower):
                return platform
        
        raise InvalidURLException(url)
    
    def get_tiktok_opts(self) -> Dict:
        """
        TikTok için özel ayarlar
        🎯 WATERMARK-FREE format seçimi!
        """
        return {
            **self.base_opts,
            # TikTok için watermark olmayan formatı seç
            'format': (
                'best[ext=mp4][vcodec^=avc1]/'  # H.264 codec ile en iyi kalite
                'best[ext=mp4]/'                 # Yoksa herhangi bir mp4
                'best'                           # Son çare: en iyi format
            ),
            # Cookie kullanımı (bot detection bypass)
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
    
    def get_instagram_opts(self) -> Dict:
        """Instagram için özel ayarlar"""
        return {
            **self.base_opts,
            'format': 'best[ext=mp4]/best',
            # Instagram için özel header'lar
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
    
    def get_youtube_opts(self) -> Dict:
        """YouTube için özel ayarlar"""
        return {
            **self.base_opts,
            # En iyi video+audio kombinasyonu
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        }
    
    def get_platform_opts(self, platform: str) -> Dict:
        """Platform'a göre optimal ayarları getir"""
        opts_map = {
            'tiktok': self.get_tiktok_opts,
            'instagram': self.get_instagram_opts,
            'youtube': self.get_youtube_opts,
        }
        
        return opts_map.get(platform, lambda: self.base_opts)()
    
    async def get_video_info(self, url: str) -> Dict:
        """
        Video bilgilerini çek (async)
        Returns: Direct URL, title, duration, thumbnail, etc.
        """
        try:
            # Platform tespiti
            platform = self.detect_platform(url)
            logger.info(f"Platform detected: {platform} for URL: {url}")
            
            # Platform-specific options
            ydl_opts = self.get_platform_opts(platform)
            ydl_opts['noplaylist'] = True  # Sadece tek video
            
            # Run yt-dlp in thread pool (blocking operation)
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                self._extract_info_sync,
                url,
                ydl_opts
            )
            
            if not info:
                raise VideoUnavailableException()
            
            # Parse video information
            result = self._parse_video_info(info, platform)
            
            # File size check
            filesize_mb = result.get('filesize_mb', 0)
            max_size = settings.MAX_DOWNLOAD_SIZE_MB
            
            if filesize_mb and filesize_mb > max_size:
                raise FileTooLargeException(int(filesize_mb), max_size)
            
            logger.info(f"Successfully extracted info for: {result['title']}")
            return result
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp error: {error_msg}")
            
            # Specific error handling
            if 'private' in error_msg.lower() or 'not available' in error_msg.lower():
                raise VideoUnavailableException("Video özel veya kaldırılmış.")
            elif 'copyright' in error_msg.lower():
                raise VideoUnavailableException("Video telif hakkı nedeniyle kullanılamıyor.")
            else:
                raise DownloadFailedException(f"İndirme hatası: {error_msg}")
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout while processing: {url}")
            raise TimeoutException()
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DownloadFailedException(f"Beklenmeyen hata: {str(e)}")
    
    def _extract_info_sync(self, url: str, opts: Dict) -> Optional[Dict]:
        """Synchronous info extraction (runs in thread pool)"""
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    def _parse_video_info(self, info: Dict, platform: str) -> Dict:
        """Parse yt-dlp output to our standard format"""
        
        # Get best format
        formats = info.get('formats', [])
        best_format = self._select_best_format(formats, platform)
        
        # Duration formatting
        duration = info.get('duration', 0)
        duration_str = str(timedelta(seconds=duration)).split('.')[0] if duration else None
        
        # Filesize calculation
        filesize = best_format.get('filesize') or info.get('filesize')
        filesize_mb = round(filesize / (1024 * 1024), 2) if filesize else None
        
        # Get direct URL
        direct_url = best_format.get('url') or info.get('url')
        
        # Format list for frontend
        available_formats = self._parse_formats(formats) if formats else []
        
        return {
            'title': info.get('title', 'Unknown'),
            'duration': duration,
            'duration_string': duration_str,
            'thumbnail': info.get('thumbnail'),
            'direct_url': direct_url,
            'platform': platform.capitalize(),
            'uploader': info.get('uploader') or info.get('channel'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'description': info.get('description', '')[:500] if info.get('description') else None,
            'filesize_mb': filesize_mb,
            'resolution': best_format.get('resolution') or f"{best_format.get('height', 'unknown')}p",
            'ext': best_format.get('ext', 'mp4'),
            'formats': available_formats[:5],  # Top 5 formats
        }
    
    def _select_best_format(self, formats: List[Dict], platform: str) -> Dict:
        """
        Select best format based on platform
        🎯 TikTok: Watermark-free format prioritized
        """
        if not formats:
            return {}
        
        if platform == 'tiktok':
            # TikTok için watermark-free format ara
            for fmt in formats:
                format_note = fmt.get('format_note', '').lower()
                # "download" veya "watermark-free" içeren format
                if 'download' in format_note or 'watermark' not in format_note:
                    if fmt.get('vcodec') != 'none':  # Video olmalı
                        return fmt
        
        # Default: En yüksek kaliteli format
        video_formats = [f for f in formats if f.get('vcodec') != 'none']
        if video_formats:
            # Height'a göre sırala
            video_formats.sort(
                key=lambda x: (x.get('height') or 0, x.get('filesize') or 0),
                reverse=True
            )
            return video_formats[0]
        
        return formats[0]
    
    def _parse_formats(self, formats: List[Dict]) -> List[Dict]:
        """Parse available formats for frontend"""
        parsed = []
        
        for fmt in formats:
            if fmt.get('vcodec') == 'none':  # Skip audio-only
                continue
                
            filesize = fmt.get('filesize')
            parsed.append({
                'format_id': fmt.get('format_id'),
                'format_note': fmt.get('format_note'),
                'ext': fmt.get('ext'),
                'quality': fmt.get('quality'),
                'filesize': filesize,
                'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else None,
                'resolution': fmt.get('resolution') or f"{fmt.get('height', 'unknown')}p",
                'fps': fmt.get('fps'),
                'vcodec': fmt.get('vcodec'),
                'acodec': fmt.get('acodec'),
            })
        
        return parsed


# Singleton instance
downloader = VideoDownloader()
