-- users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    native_language VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- vocabulary
CREATE TABLE vocabulary (
    id SERIAL PRIMARY KEY,
    english_word VARCHAR(100),
    tamil_word VARCHAR(100),
    french_word VARCHAR(100),
    pronunciation VARCHAR(200),
    category VARCHAR(50)
);

-- user progress (recommended: add FK to vocabulary)
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES vocabulary(id) ON DELETE SET NULL,
    difficulty_level INTEGER,
    last_practiced TIMESTAMP,
    success_rate FLOAT
);
