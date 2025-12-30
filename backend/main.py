from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routers import screening

# Load environment variables
load_dotenv()

app = FastAPI(
    title="ElevenLabs Screening Backend",
    description="Backend API for candidate screening with ElevenLabs integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(screening.router)


@app.get("/")
async def root():
    return {
        "message": "ElevenLabs Screening Backend API",
        "version": "1.0.0",
        "endpoints": {
            "start_screening": "POST /api/screening/start",
            "get_context": "GET /api/screening/{session_id}/context",
            "get_questions": "GET /api/screening/{session_id}/questions"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

