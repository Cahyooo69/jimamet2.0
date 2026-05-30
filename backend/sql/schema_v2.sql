-- ═══════════════════════════════════════════════════════════════════════════
-- SCHEMA V2: Full English naming convention migration
-- Run in Supabase Dashboard → SQL Editor
-- WARNING: This drops ALL existing tables and recreates them.
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Drop all old tables (CASCADE removes FK dependencies)
DROP TABLE IF EXISTS public.coach_messages CASCADE;
DROP TABLE IF EXISTS public.coach_sessions CASCADE;
DROP TABLE IF EXISTS public.coachbot_history CASCADE;
DROP TABLE IF EXISTS public.consultation_messages CASCADE;
DROP TABLE IF EXISTS public.chat_konsultasi CASCADE;
DROP TABLE IF EXISTS public.consultations CASCADE;
DROP TABLE IF EXISTS public.konsultasi CASCADE;
DROP TABLE IF EXISTS public.recommendations CASCADE;
DROP TABLE IF EXISTS public.recommendation CASCADE;
DROP TABLE IF EXISTS public.food_records CASCADE;
DROP TABLE IF EXISTS public.food_analysis CASCADE;
DROP TABLE IF EXISTS public.images CASCADE;
DROP TABLE IF EXISTS public.image CASCADE;
DROP TABLE IF EXISTS public.daily_summary CASCADE;
DROP TABLE IF EXISTS public.history CASCADE;
DROP TABLE IF EXISTS public.nutritionists CASCADE;
DROP TABLE IF EXISTS public.ahli_gizi CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Users
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.users (
    id                   BIGSERIAL PRIMARY KEY,
    username             TEXT UNIQUE NOT NULL,
    full_name            TEXT NOT NULL DEFAULT '',
    age                  INTEGER DEFAULT 0,
    height               DECIMAL DEFAULT 0,
    weight               DECIMAL DEFAULT 0,
    gender               TEXT DEFAULT 'male',
    activity_level       TEXT DEFAULT 'moderate',
    goal                 TEXT DEFAULT 'maintain',
    email                TEXT UNIQUE NOT NULL,
    password             TEXT NOT NULL,
    token                TEXT UNIQUE,
    daily_calorie_target DECIMAL DEFAULT 2000
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Daily Summary (one record per user per day)
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.daily_summary (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        BIGINT REFERENCES public.users(id) ON DELETE CASCADE,
    date           DATE NOT NULL,
    total_calories DECIMAL DEFAULT 0,
    total_protein  DECIMAL DEFAULT 0,
    total_fat      DECIMAL DEFAULT 0,
    total_carbs    DECIMAL DEFAULT 0,
    UNIQUE(user_id, date)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Images
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.images (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     BIGINT REFERENCES public.users(id) ON DELETE CASCADE,
    file_path   TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. Food Records
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.food_records (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     BIGINT REFERENCES public.users(id) ON DELETE CASCADE,
    image_id    UUID REFERENCES public.images(id) ON DELETE SET NULL,
    food_name   TEXT NOT NULL,
    calories    DECIMAL DEFAULT 0,
    protein     DECIMAL DEFAULT 0,
    fat         DECIMAL DEFAULT 0,
    carbs       DECIMAL DEFAULT 0,
    sugar       DECIMAL DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. Recommendations
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.recommendations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             BIGINT REFERENCES public.users(id) ON DELETE CASCADE,
    recommendation_type TEXT CHECK (recommendation_type IN ('deficit', 'surplus', 'maintain')),
    content             TEXT NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. Nutritionists
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.nutritionists (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name      TEXT NOT NULL,
    username       TEXT NOT NULL UNIQUE,
    password       TEXT NOT NULL,
    email          TEXT NOT NULL,
    specialization TEXT DEFAULT 'Clinical Nutrition',
    license_number TEXT DEFAULT '',
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 8. Consultations (CoachBot → Nutritionist referral)
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.consultations (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           BIGINT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    coach_message     TEXT NOT NULL,
    status            TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
    nutritionist_notes TEXT DEFAULT '',
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 9. Consultation Messages (User ↔ Nutritionist chat)
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.consultation_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID NOT NULL REFERENCES public.consultations(id) ON DELETE CASCADE,
    sender          TEXT NOT NULL CHECK (sender IN ('user', 'nutritionist')),
    message         TEXT NOT NULL,
    sent_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 10. Coach Sessions (NutriCoach AI conversation sessions)
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.coach_sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    BIGINT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title      TEXT NOT NULL DEFAULT 'New Consultation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 11. Coach Messages (individual messages within a coach session)
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE public.coach_messages (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id         UUID NOT NULL REFERENCES public.coach_sessions(id) ON DELETE CASCADE,
    sender             TEXT NOT NULL CHECK (sender IN ('user', 'ai')),
    message            TEXT NOT NULL,
    needs_consultation BOOLEAN DEFAULT FALSE,
    sent_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 12. Enable Row Level Security for all tables
-- ═══════════════════════════════════════════════════════════════════════════
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nutritionists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consultations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consultation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coach_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coach_messages ENABLE ROW LEVEL SECURITY;

-- Policies: allow full API access (service role)
CREATE POLICY "Enable all for API" ON public.users FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.daily_summary FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.images FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.food_records FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.recommendations FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.nutritionists FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.consultations FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.consultation_messages FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.coach_sessions FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.coach_messages FOR ALL USING (true);

-- ═══════════════════════════════════════════════════════════════════════════
-- 13. Seed data: sample nutritionist
-- ═══════════════════════════════════════════════════════════════════════════
INSERT INTO public.nutritionists (full_name, username, password, email, specialization, license_number)
VALUES (
    'Dr. Sarah Amelia, S.Gz',
    'drsarah',
    'Gizi1234!',
    'sarah.amelia@jimamet.id',
    'Clinical Nutrition & Dietetics',
    'STR-GZ-2024-001'
) ON CONFLICT (username) DO NOTHING;
