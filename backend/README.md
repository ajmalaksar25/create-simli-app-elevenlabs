# ElevenLabs Screening Backend

FastAPI backend service for processing candidate resumes and generating screening context for ElevenLabs agents.

## Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set environment variables in `.env` (in project root):
```
OPENAI_API_KEY=your-openai-api-key
FASTAPI_PORT=8000  # Optional, defaults to 8000
```

## Running the Backend

From the `backend` directory:
```bash
python run.py
```

Or from project root:
```bash
cd backend && python run.py
```

Or using uvicorn directly:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/screening/start` - Start a new screening session
- `GET /api/screening/{session_id}/context` - Get session context
- `GET /api/screening/{session_id}/questions` - Get screening questions
- `GET /health` - Health check

## Usage

The backend processes resumes (PDF, DOCX, or text), generates:
- Candidate-job match analysis
- Condensed resume summary
- Dynamic screening questions

All using LangChain with OpenAI GPT-4.

