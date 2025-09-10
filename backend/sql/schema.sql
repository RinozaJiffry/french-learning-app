-- Schema for french_app matching app/models.py

-- users
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  native_language VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_id ON users (id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- vocabulary
CREATE TABLE IF NOT EXISTS vocabulary (
  id SERIAL PRIMARY KEY,
  english_word VARCHAR(100) NOT NULL,
  tamil_word VARCHAR(100),
  french_word VARCHAR(100) NOT NULL,
  pronunciation VARCHAR(200),
  category VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_vocabulary_id ON vocabulary (id);

-- user_progress
CREATE TABLE IF NOT EXISTS user_progress (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  word_id INTEGER NOT NULL REFERENCES vocabulary(id) ON DELETE CASCADE,
  difficulty_level INTEGER DEFAULT 1,
  last_practiced TIMESTAMPTZ,
  success_rate FLOAT DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_user_progress_id ON user_progress (id);
