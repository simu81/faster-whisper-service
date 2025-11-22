from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import tempfile
import shutil

app = FastAPI()

# Load the model once on startup
# With 8 GB RAM, "medium" + int8 should be fine.
# If you hit memory issues, change to "small".
model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8"
)

@app.get("/")
def root():
    return {"status": "ok", "message": "faster-whisper service running"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded file to temp file
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