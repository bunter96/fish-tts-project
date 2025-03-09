from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fish_audio_sdk import Session, TTSRequest
from fastapi.responses import StreamingResponse
from io import BytesIO
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development. Update for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Session with your Fish Audio API key
session = Session("43e50bc23bc94daba2c1e74e791086e3")  # Replace with your actual API key

# Define the request model
class TTSRequestModel(BaseModel):
    text: str

@app.post("/generate-tts/")
async def generate_tts(request: TTSRequestModel):
    try:
        audio_stream = BytesIO()
        for chunk in session.tts(TTSRequest(text=request.text)):
            audio_stream.write(chunk)
        audio_stream.seek(0)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "TTS Backend is Running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
