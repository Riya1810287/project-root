# backend/app.py
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
import sqlite3
import uuid
from typing import Optional
import aiofiles

app = FastAPI(title="AI Meeting Summarizer")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
def init_db():
    db = sqlite3.connect("summaries.db")
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY, 
                    meeting_id TEXT UNIQUE,
                    transcript TEXT,
                    summary TEXT,
                    wordcloud_path TEXT,
                    pdf_path TEXT)""")
    db.commit()
    db.close()

init_db()

class MeetingRequest(BaseModel):
    meeting_id: Optional[str] = None
    audio_url: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    async with aiofiles.open('static/index.html', mode='r') as f:
        html = await f.read()
    return HTMLResponse(content=html, status_code=200)

@app.post("/process-meeting")
async def process_meeting(request: MeetingRequest):
    meeting_id = request.meeting_id or str(uuid.uuid4())
    
    # In a real app, you would:
    # 1. Download/process audio
    # 2. Generate transcript
    # 3. Create summary
    # 4. Generate wordcloud and PDF
    
    # For demo purposes, we'll create mock data
    transcript = "This is a sample transcript from the meeting discussing project timelines and deliverables."
    summary = "The team discussed project timelines and agreed to deliver Phase 1 by next Friday."
    
    # Save to database
    db = sqlite3.connect("summaries.db")
    cursor = db.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO summaries (meeting_id, transcript, summary) VALUES (?, ?, ?)",
        (meeting_id, transcript, summary)
    )
    db.commit()
    db.close()
    
    return {
        "meeting_id": meeting_id,
        "status": "processed",
        "summary": summary
    }

@app.get("/summary/{meeting_id}")
async def get_summary(meeting_id: str):
    db = sqlite3.connect("summaries.db")
    cursor = db.cursor()
    cursor.execute(
        "SELECT transcript, summary FROM summaries WHERE meeting_id = ?",
        (meeting_id,)
    )
    result = cursor.fetchone()
    db.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting_id": meeting_id,
        "transcript": result[0],
        "summary": result[1]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)