# backend/app/schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------- User ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    native_language: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Vocabulary ----------
class VocabularyBase(BaseModel):
    english_word: str
    tamil_word: Optional[str] = None
    french_word: str
    pronunciation: Optional[str] = None
    category: Optional[str] = None


class VocabularyCreate(VocabularyBase):
    pass


class VocabularyResponse(VocabularyBase):
    id: int

    class Config:
        from_attributes = True


# ---------- User Progress ----------
class UserProgressBase(BaseModel):
    user_id: int
    word_id: int
    difficulty_level: Optional[int] = 1
    success_rate: Optional[float] = 0.0


class UserProgressCreate(UserProgressBase):
    pass


class UserProgressResponse(UserProgressBase):
    id: int
    last_practiced: Optional[datetime] = None

    class Config:
        from_attributes = True
