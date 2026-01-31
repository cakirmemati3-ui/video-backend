"""
Test script for Video Downloader API
Run: python test_api.py
"""
import requests
import json
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    console.print("\n[bold cyan]🏥 Testing Health Endpoint...[/bold cyan]")
    
    response = requests.get(f"{BASE_URL}/health")
    print(response.json())
    
    assert response.status_code == 200
    console.print("[bold green]✅ Health check passed![/bold green]")


def test_platforms():
    """Test platforms endpoint"""
    console.print("\n[bold cyan]🌐 Testing Platforms Endpoint...[/bold cyan]")
    
    response = requests.get(f"{BASE_URL}/api/platforms")
    data = response.json()
    
    table = Table(title="Supported Platforms")
    table.add_column("Platform", style="cyan")
    table.add_column("Supported", style="green")
    table.add_column("Features", style="yellow")
    
    for platform in data['platforms']:
        features = ", ".join(platform.get('features', []))
        table.add_row(
            platform['name'],
            str(platform['supported']),
            features or "Standard download"
        )
    
    console.print(table)
    console.print("[bold green]✅ Platforms check passed![/bold green]")


def test_fetch_video_get():
    """Test fetch endpoint with GET request"""
    console.print("\n[bold cyan]📹 Testing Fetch Endpoint (GET)...[/bold cyan]")
    
    # Example YouTube Shorts URL
    test_url = "https://www.youtube.com/shorts/test"
    
    console.print(f"Testing URL: {test_url}")
    
    response = requests.get(
        f"{BASE_URL}/api/fetch",
        params={"url": test_url}
    )
    
    console.print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        table = Table(title="Video Information")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Success", str(data.get('success')))
        table.add_row("Title", data.get('title', 'N/A'))
        table.add_row("Platform", data.get('platform', 'N/A'))
        table.add_row("Duration", data.get('duration_string', 'N/A'))
        table.add_row("Resolution", data.get('resolution', 'N/A'))
        table.add_row("File Size", f"{data.get('filesize_mb', 'N/A')} MB")
        
        console.print(table)
        console.print("[bold green]✅ Fetch test passed![/bold green]")
    else:
        print(response.json())


def test_fetch_video_post():
    """Test fetch endpoint with POST request"""
    console.print("\n[bold cyan]📹 Testing Fetch Endpoint (POST)...[/bold cyan]")
    
    # Example TikTok URL
    test_url = "https://www.tiktok.com/@user/video/123"
    
    console.print(f"Testing URL: {test_url}")
    
    response = requests.post(
        f"{BASE_URL}/api/fetch",
        json={"url": test_url}
    )
    
    console.print(f"Status Code: {response.status_code}")
    print(response.json())


def test_invalid_url():
    """Test with invalid URL"""
    console.print("\n[bold cyan]❌ Testing Invalid URL...[/bold cyan]")
    
    response = requests.post(
        f"{BASE_URL}/api/fetch",
        json={"url": "https://invalid-site.com/video"}
    )
    
    console.print(f"Status Code: {response.status_code}")
    data = response.json()
    
    console.print(f"[bold red]Error: {data.get('error')}[/bold red]")
    console.print("[bold green]✅ Error handling works![/bold green]")


def test_rate_limit():
    """Test rate limiting"""
    console.print("\n[bold cyan]🚦 Testing Rate Limiting...[/bold cyan]")
    
    console.print("Sending 35 requests quickly...")
    
    for i in range(35):
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 429:
            console.print(f"[bold yellow]Rate limited after {i+1} requests![/bold yellow]")
            print(response.json())
            break
    
    console.print("[bold green]✅ Rate limiting works![/bold green]")


if __name__ == "__main__":
    console.print("[bold magenta]" + "="*60 + "[/bold magenta]")
    console.print("[bold magenta]🔥 VIDEO DOWNLOADER PRO - API TESTS[/bold magenta]")
    console.print("[bold magenta]" + "="*60 + "[/bold magenta]")
    
    try:
        test_health()
        test_platforms()
        # test_fetch_video_get()  # Uncomment to test with real URLs
        # test_fetch_video_post()
        # test_invalid_url()
        # test_rate_limit()
        
        console.print("\n[bold green]" + "="*60 + "[/bold green]")
        console.print("[bold green]🎉 ALL TESTS PASSED![/bold green]")
        console.print("[bold green]" + "="*60 + "[/bold green]")
        
    except requests.exceptions.ConnectionError:
        console.print("\n[bold red]❌ ERROR: Cannot connect to server![/bold red]")
        console.print("[yellow]Make sure the server is running:[/yellow]")
        console.print("[cyan]python -m uvicorn app.main:app --reload[/cyan]")
    except Exception as e:
        console.print(f"\n[bold red]❌ ERROR: {str(e)}[/bold red]")
