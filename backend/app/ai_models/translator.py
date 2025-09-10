"""
SmartTranslator using MarianMT (Helsinki-NLP)
Supports:
- EN -> FR
- TA -> FR (direct if available, fallback: TA -> EN -> FR)
- Batch translation and n-best candidates
"""

from __future__ import annotations
from typing import List, Optional
import os
import torch
from transformers import MarianMTModel, MarianTokenizer

def _get_device() -> torch.device:
    return torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

class SmartTranslator:
    def __init__(
        self,
        en_fr_model: str = os.getenv("EN_FR_MODEL", "Helsinki-NLP/opus-mt-en-fr"),
        ta_fr_model: Optional[str] = os.getenv("TA_FR_MODEL", "Helsinki-NLP/opus-mt-ta-fr"),
        ta_en_model: Optional[str] = os.getenv("TA_EN_MODEL", "Helsinki-NLP/opus-mt-ta-en"),
        device: Optional[torch.device] = None,
    ):
        self.device = device or _get_device()

        # EN → FR
        self.en_fr_tokenizer = MarianTokenizer.from_pretrained(en_fr_model)
        self.en_fr_model = MarianMTModel.from_pretrained(en_fr_model).to(self.device).eval()

        # FR → EN (optional for reverse translation)
        self.fr_en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-en")
        self.fr_en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-fr-en").to(self.device).eval()

        # TA → FR
        self.ta_fr_tokenizer = None
        self.ta_fr_model = None
        if ta_fr_model:
            try:
                self.ta_fr_tokenizer = MarianTokenizer.from_pretrained(ta_fr_model)
                self.ta_fr_model = MarianMTModel.from_pretrained(ta_fr_model).to(self.device).eval()
            except Exception:
                pass

        # TA → EN fallback
        self.ta_en_tokenizer = None
        self.ta_en_model = None
        if ta_en_model:
            try:
                self.ta_en_tokenizer = MarianTokenizer.from_pretrained(ta_en_model)
                self.ta_en_model = MarianMTModel.from_pretrained(ta_en_model).to(self.device).eval()
            except Exception:
                pass

    # ------------------- Public API --------------------------------------

    def translate(self, text: str, source_language: str = "en") -> str:
        return self.translate_batch([text], source_language)[0]

    def translate_batch(self, texts: List[str], source_language: str = "en") -> List[str]:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        src = source_language.lower()
        if src.startswith("en"):
            return self._translate_with(self.en_fr_tokenizer, self.en_fr_model, texts)
        elif src.startswith("fr"):
            return self._translate_with(self.fr_en_tokenizer, self.fr_en_model, texts)
        elif src.startswith("ta"):
            # Direct TA→FR if available
            if self.ta_fr_model and self.ta_fr_tokenizer:
                return self._translate_with(self.ta_fr_tokenizer, self.ta_fr_model, texts)
            # Fallback: TA → EN → FR
            if self.ta_en_model and self.ta_en_tokenizer:
                en_texts = self._translate_with(self.ta_en_tokenizer, self.ta_en_model, texts)
                return self._translate_with(self.en_fr_tokenizer, self.en_fr_model, en_texts)
            return [f"[no-ta-fr-model] {t}" for t in texts]
        else:
            return self._translate_with(self.en_fr_tokenizer, self.en_fr_model, texts)

    # Convenience wrapper for quick tests
    def translate_english_to_french(self, text: str) -> str:
        """Translate English to French (helper used by quick-start command)."""
        return self.translate(text, source_language="en")

    def translate_with_confidence(
        self,
        texts: List[str],
        source_language: str = "en",
        num_return_sequences: int = 3,
        num_beams: int = 5,
        temperature: float = 1.0,
    ) -> List[List[str]]:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        src = source_language.lower()
        if src.startswith("en"):
            tok, model = self.en_fr_tokenizer, self.en_fr_model
        elif src.startswith("fr"):
            tok, model = self.fr_en_tokenizer, self.fr_en_model
        elif src.startswith("ta"):
            if self.ta_fr_model and self.ta_fr_tokenizer:
                tok, model = self.ta_fr_tokenizer, self.ta_fr_model
            elif self.ta_en_model and self.ta_en_tokenizer:
                # TA → EN → FR fallback
                intermediate = self._translate_with(self.ta_en_tokenizer, self.ta_en_model, texts)
                return [self._translate_with(self.en_fr_tokenizer, self.en_fr_model, [t]) for t in intermediate]
            else:
                return [[f"[no-ta-fr-model] {t}"] for t in texts]
        else:
            tok, model = self.en_fr_tokenizer, self.en_fr_model

        results = []
        for text in texts:
            inputs = tok([text], return_tensors="pt", padding=True, truncation=True).to(self.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    num_return_sequences=num_return_sequences,
                    num_beams=num_beams,
                    do_sample=False if num_beams > 1 else True,
                    temperature=temperature,
                    early_stopping=True,
                    max_new_tokens=128,
                )
            candidates = [tok.decode(o, skip_special_tokens=True) for o in outputs]
            results.append(candidates)
        return results

    # ------------------- Internal ----------------------------------------

    def _translate_with(self, tok: MarianTokenizer, model: MarianMTModel, batch: List[str]) -> List[str]:
        inputs = tok(batch, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            gen = model.generate(**inputs, max_new_tokens=128, num_beams=4, early_stopping=True)
        return [tok.decode(g, skip_special_tokens=True) for g in gen]
