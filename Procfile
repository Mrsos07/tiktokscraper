web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
dashboard: streamlit run admin/dashboard.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
