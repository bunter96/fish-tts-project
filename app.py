from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth

app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate("firebase-creds.json")
firebase_admin.initialize_app(cred)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Firebase Auth Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

FISH_API_KEY = "43e50bc23bc94daba2c1e74e791086e3"

@app.post("/upload-model/")
async def upload_model(
    model_name: str = Form(...),
    voice_1: UploadFile = File(...),
    voice_2: UploadFile = File(...),
    cover_image: UploadFile = File(None),
    user: dict = Depends(get_current_user)
):
    try:
        unique_title = model_name.strip() or f"MyModel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        files = [
            ("voices", (voice_1.filename, voice_1.file, "audio/mpeg")),
            ("voices", (voice_2.filename, voice_2.file, "audio/mpeg")),
        ]

        if cover_image:
            files.append(("cover_image", (cover_image.filename, cover_image.file, "image/jpeg")))

        response = requests.post(
            "https://api.fish.audio/model",
            files=files,
            data={
                "visibility": "private",
                "type": "tts",
                "title": unique_title,
                "train_mode": "fast",
                "enhance_audio_quality": "true",
                "texts": ["Sample text 1", "Sample text 2"],
            },
            headers={"Authorization": f"Bearer {FISH_API_KEY}"},
        )

        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))