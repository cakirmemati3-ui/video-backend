#!/usr/bin/env python
"""
🔥 Video Downloader Pro - Quick Start Script
Run this to start the server instantly!
"""
import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from app.config import settings
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    # ASCII Art
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🔥 VIDEO DOWNLOADER PRO 🔥                        ║
    ║                                                           ║
    ║   Instagram • TikTok • YouTube Downloader API            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    
    console.print(banner, style="bold cyan")
    
    # Server info panel
    info = f"""
    [bold green]✅ Starting Server...[/bold green]
    
    [cyan]Server:[/cyan] {settings.HOST}:{settings.PORT}
    [cyan]Environment:[/cyan] {settings.ENVIRONMENT}
    [cyan]Debug Mode:[/cyan] {settings.DEBUG}
    
    [yellow]📡 Endpoints:[/yellow]
    • API Docs: http://localhost:{settings.PORT}/docs
    • Root: http://localhost:{settings.PORT}/
    • Health: http://localhost:{settings.PORT}/api/health
    • Fetch: http://localhost:{settings.PORT}/api/fetch
    
    [yellow]🎯 Supported Platforms:[/yellow]
    • Instagram (Reels, Posts, Stories)
    • TikTok (Watermark-free!)
    • YouTube (Videos, Shorts)
    
    [green]Press CTRL+C to stop[/green]
    """
    
    console.print(Panel(info, title="Server Information", border_style="green"))
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
    
except KeyboardInterrupt:
    console.print("\n[bold red]👋 Server stopped by user[/bold red]")
    sys.exit(0)
    
except ImportError as e:
    print(f"\n❌ Missing dependency: {e}")
    print("\n💡 Solution:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
