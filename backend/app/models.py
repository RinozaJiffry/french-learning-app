# backend/app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    native_language = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    progress = relationship("UserProgress", back_populates="user")


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    english_word = Column(String(100), nullable=False)
    tamil_word = Column(String(100))
    french_word = Column(String(100), nullable=False)
    pronunciation = Column(String(200))
    category = Column(String(50))

    progress = relationship("UserProgress", back_populates="word")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False)
    difficulty_level = Column(Integer, default=1)
    last_practiced = Column(TIMESTAMP(timezone=True))
    success_rate = Column(Float, default=0.0)

    user = relationship("User", back_populates="progress")
    word = relationship("Vocabulary", back_populates="progress")
