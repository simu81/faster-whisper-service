from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from faster_whisper import WhisperModel
import tempfile
import shutil
import os

app = FastAPI()

# ===== NEW: API key security =====
API_KEY = os.environ.get("API_KEY")  # set in Coolify
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if API_KEY and api_key == API_KEY:
        return True
    # no key set or wrong key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )
# =================================

# Load the model once on startup
model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8"
)

@app.get("/")
def root():
    return {"status": "ok", "message": "faster-whisper service running"}

# Protect this endpoint with API key
@app.post("/transcribe", dependencies=[Depends(verify_api_key)])
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    segments, info = model.transcribe(tmp_path)
    text = "".join(segment.text for segment in segments)

    return {
        "language": info.language,
        "duration": info.duration,
        "text": text.strip(),
    }
