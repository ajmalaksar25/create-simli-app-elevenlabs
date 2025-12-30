"""
Run script for the FastAPI backend
Run from project root: python -m backend.run
Or from backend directory: python run.py
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    # Run from backend directory context
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

