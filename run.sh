#!/bin/bash
# TikTok Scraper - Linux/Mac Run Script

echo "========================================"
echo "TikTok Scraper - Starting Services"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    playwright install chromium
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ".env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your settings and run again."
    exit 1
fi

# Check if database exists
if [ ! -f "tiktok_scraper.db" ]; then
    echo "Database not found. Initializing..."
    python scripts/init_db.py
fi

echo ""
echo "Select service to run:"
echo "1. API Server (FastAPI)"
echo "2. Admin Dashboard (Streamlit)"
echo "3. Both (API + Admin)"
echo "4. Test Scraper"
echo "5. Setup Google Drive"
echo "6. Exit"
echo ""

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting API Server on http://localhost:8000"
        echo "API Documentation: http://localhost:8000/docs"
        echo ""
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo ""
        echo "Starting Admin Dashboard on http://localhost:8501"
        echo ""
        streamlit run admin/dashboard.py --server.port 8501
        ;;
    3)
        echo ""
        echo "Starting both services..."
        echo "API: http://localhost:8000"
        echo "Admin: http://localhost:8501"
        echo ""
        
        # Start API in background
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
        API_PID=$!
        
        # Wait a bit for API to start
        sleep 3
        
        # Start Streamlit
        streamlit run admin/dashboard.py --server.port 8501 &
        STREAMLIT_PID=$!
        
        echo ""
        echo "Services started."
        echo "API PID: $API_PID"
        echo "Streamlit PID: $STREAMLIT_PID"
        echo ""
        echo "Press Ctrl+C to stop all services..."
        
        # Wait for Ctrl+C
        trap "kill $API_PID $STREAMLIT_PID; exit" INT
        wait
        ;;
    4)
        echo ""
        read -p "Enter mode (profile/hashtag): " mode
        read -p "Enter username or hashtag: " value
        read -p "Enter limit (default 5): " limit
        limit=${limit:-5}
        echo ""
        python scripts/test_scraper.py --mode $mode --value $value --limit $limit
        ;;
    5)
        echo ""
        echo "Setting up Google Drive authentication..."
        echo ""
        python scripts/setup_google_drive.py
        ;;
    6)
        echo ""
        echo "Goodbye!"
        deactivate
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

deactivate
