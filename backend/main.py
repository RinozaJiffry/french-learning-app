from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from app.ai_models.translator import SmartTranslator
from app.ai_models.pronunciation_checker import PronunciationChecker
from app.ai_models.conversation_bot import FrenchConversationBot

# ------------------- FastAPI Setup -----------------------------------
app = FastAPI(title="AI Language Learning API")

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Initialize AI Modules ---------------------------
translator = SmartTranslator()
pronunciation_checker = PronunciationChecker()
conversation_bot = FrenchConversationBot()

# ------------------- Request Models ---------------------------------
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "en"

class ConversationRequest(BaseModel):
    message: str
    scenario: str = "general"

# ------------------- Endpoints --------------------------------------

@app.post("/translate")
async def translate(request: TranslationRequest):
    try:
        translation = translator.translate(request.text, request.source_language)
        return {
            "original": request.text,
            "translation": translation,
            "source_language": request.source_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate-batch")
async def translate_batch(request: TranslationRequest):
    try:
        translations = translator.translate_batch([request.text], request.source_language)
        return {
            "original": request.text,
            "translations": translations,
            "source_language": request.source_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-pronunciation")
async def check_pronunciation(audio: UploadFile = File(...), expected_text: str = ""):
    try:
        temp_path = f"temp_{audio.filename}"
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
        result = pronunciation_checker.check_pronunciation(temp_path, expected_text)
        os.remove(temp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def generate_tts(text: str):
    try:
        audio_bytes = pronunciation_checker.generate_tts(text)
        return {"audio_bytes": audio_bytes.hex()}  # Can convert to base64 in frontend if needed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation")
async def conversation(request: ConversationRequest):
    try:
        response = conversation_bot.generate_response(request.message, request.scenario)
        return {"user_message": request.message, "bot_response": response, "scenario": request.scenario}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Language Learning API is running!"}
