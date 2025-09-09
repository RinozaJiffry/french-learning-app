"""
PronunciationChecker:
- Uses Whisper for speech-to-text
- Compares transcribed text with expected
- Provides feedback
- Generates TTS audio using gTTS
"""

import whisper
from difflib import SequenceMatcher
from gtts import gTTS
import io
import os

class PronunciationChecker:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)

    def transcribe_speech(self, audio_path: str, language: str = "fr") -> str:
        result = self.model.transcribe(audio_path, language=language)
        return result["text"]

    def check_pronunciation(self, audio_path: str, expected_text: str) -> dict:
        transcribed_text = self.transcribe_speech(audio_path)
        score = self.similarity_score(expected_text, transcribed_text)
        feedback = self.generate_feedback(expected_text, transcribed_text, score)
        return {
            "expected": expected_text,
            "transcribed": transcribed_text,
            "similarity_score": score,
            "feedback": feedback
        }

    def similarity_score(self, expected: str, actual: str) -> float:
        return SequenceMatcher(None, expected.lower(), actual.lower()).ratio()

    def generate_feedback(self, expected: str, actual: str, score: float) -> str:
        if score > 0.9:
            return "Excellent pronunciation!"
        elif score > 0.7:
            return f"Good! Check specific words: {self.differences(expected, actual)}"
        else:
            return f"Keep practicing. Focus on: {self.differences(expected, actual)}"

    def differences(self, expected: str, actual: str) -> str:
        expected_words = expected.split()
        actual_words = actual.split()
        diffs = [w for w, a in zip(expected_words, actual_words) if w != a]
        return ", ".join(diffs) if diffs else "overall pronunciation"

    def generate_tts(self, text: str, lang: str = "fr") -> bytes:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
