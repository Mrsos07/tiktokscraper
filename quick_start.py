"""
Quick Start Script - TikTok Scraper
Run this to check installation and start the server
"""
import sys
import subprocess
import os

def check_installation():
    """Check if required packages are installed"""
    print("🔍 Checking installation...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'httpx'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing")
            missing.append(package)
    
    return missing

def install_packages():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    print("This may take a few minutes...\n")
    
    subprocess.check_call([
        sys.executable, 
        '-m', 
        'pip', 
        'install', 
        '-q',
        'fastapi',
        'uvicorn[standard]',
        'sqlalchemy',
        'aiosqlite',
        'pydantic',
        'pydantic-settings',
        'httpx',
        'python-dotenv',
        'loguru'
    ])
    
    print("✅ Installation complete!\n")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# TikTok Scraper Configuration
APP_NAME=TikTok Scraper
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=sqlite+aiosqlite:///./tiktok_scraper.db

TIKTOK_MAX_VIDEOS_PER_REQUEST=50
TIKTOK_REQUEST_DELAY_MIN=2
TIKTOK_REQUEST_DELAY_MAX=5
""")
        print("✅ .env file created!\n")

def init_database():
    """Initialize database"""
    print("🗄️  Initializing database...")
    try:
        import asyncio
        from app.models.database import init_db
        asyncio.run(init_db())
        print("✅ Database initialized!\n")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}\n")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting TikTok Scraper API Server...")
    print("=" * 60)
    print("📡 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 60)
    print("\n⏹️  Press CTRL+C to stop the server\n")
    
    subprocess.call([
        sys.executable,
        '-m',
        'uvicorn',
        'app.main:app',
        '--host',
        '0.0.0.0',
        '--port',
        '8000',
        '--reload'
    ])

def main():
    """Main function"""
    print("=" * 60)
    print("🎵 TikTok Scraper - Quick Start")
    print("=" * 60)
    print()
    
    # Check installation
    missing = check_installation()
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        response = input("\n📦 Install missing packages? (y/n): ")
        if response.lower() == 'y':
            install_packages()
        else:
            print("❌ Cannot start without required packages.")
            sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    init_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
