# backend/app/cache.py
import os
import json
from typing import Optional, Dict, Any

import redis
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from . import models

# Load environment variables
load_dotenv()

# Initialize Redis client from REDIS_URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL)


def get_vocab_cached(db: Session, word_id: int) -> Optional[Dict[str, Any]]:
    """Fetch vocabulary by id with Redis caching for 1 hour.

    Cache key format: "vocab:{id}"
    Cached value: JSON with a subset of columns.
    """
    key = f"vocab:{word_id}"
    cached = r.get(key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            # If cache is corrupted, ignore and rebuild
            pass

    v = (
        db.query(models.Vocabulary)
        .filter(models.Vocabulary.id == word_id)
        .first()
    )
    if not v:
        return None

    data = {
        "id": v.id,
        "english_word": v.english_word,
        "tamil_word": getattr(v, "tamil_word", None),
        "french_word": v.french_word,
        "pronunciation": getattr(v, "pronunciation", None),
        "category": getattr(v, "category", None),
    }

    # Cache for 1 hour
    r.set(key, json.dumps(data), ex=3600)
    return data


def invalidate_vocab_cache(word_id: int) -> None:
    """Remove a vocab entry from cache."""
    key = f"vocab:{word_id}"
    r.delete(key)
