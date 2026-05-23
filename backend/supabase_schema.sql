-- ═══════════════════════════════════════════════════
--  Jimamet Medical Nutrition Platform
--  Supabase Database Schema
-- ═══════════════════════════════════════════════════

-- 1. User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT DEFAULT '',
    email TEXT DEFAULT '',
    username TEXT DEFAULT '',
    age INTEGER,
    weight REAL,
    height REAL,
    gender TEXT DEFAULT 'male' CHECK (gender IN ('male', 'female')),
    activity_level TEXT DEFAULT 'moderate' CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'veryActive')),
    goal TEXT DEFAULT 'maintain' CHECK (goal IN ('lose', 'maintain', 'gain')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Food Consumption Records
CREATE TABLE IF NOT EXISTS food_records (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    food_name TEXT NOT NULL,
    emoji TEXT DEFAULT '🍽️',
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    fiber REAL DEFAULT 0,
    sugar REAL DEFAULT 0,
    sodium REAL DEFAULT 0,
    portion TEXT DEFAULT '1 porsi',
    consumed_at TIMESTAMPTZ DEFAULT now(),
    confidence REAL,
    image_url TEXT,
    tags JSONB DEFAULT '[]',
    recommendation TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_food_records_user_id ON food_records(user_id);
CREATE INDEX IF NOT EXISTS idx_food_records_consumed_at ON food_records(consumed_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Auto-update updated_at on user_profiles
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (optional, for direct client access)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_records ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (our Django backend uses the service key)
CREATE POLICY "Service role full access on user_profiles" ON user_profiles
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on food_records" ON food_records
    FOR ALL USING (true) WITH CHECK (true);
