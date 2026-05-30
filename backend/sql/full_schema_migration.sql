-- ═══════════════════════════════════════════════════════════════════════════
-- FULL MIGRATION: Restructure users table
-- id_user sekarang BIGSERIAL (auto-increment integer)
-- username jadi kolom TERPISAH
-- Jalankan di Supabase Dashboard → SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Drop semua tabel lama (CASCADE menghapus FK dependensi)
DROP TABLE IF EXISTS public.chat_konsultasi CASCADE;
DROP TABLE IF EXISTS public.konsultasi CASCADE;
DROP TABLE IF EXISTS public.recommendation CASCADE;
DROP TABLE IF EXISTS public.food_analysis CASCADE;
DROP TABLE IF EXISTS public.image CASCADE;
DROP TABLE IF EXISTS public.history CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- 2. Buat ulang tabel users dengan id_user BIGSERIAL + username terpisah
CREATE TABLE public.users (
    id_user          BIGSERIAL PRIMARY KEY,
    username         TEXT UNIQUE NOT NULL,
    nama             TEXT NOT NULL DEFAULT '',
    umur             INTEGER DEFAULT 0,
    tinggi_badan     DECIMAL DEFAULT 0,
    berat_badan      DECIMAL DEFAULT 0,
    jenis_kelamin    TEXT DEFAULT 'male',
    aktivitas_harian TEXT DEFAULT 'moderate',
    goal             TEXT DEFAULT 'maintain',
    email            TEXT UNIQUE NOT NULL,
    password         TEXT NOT NULL,
    token            TEXT UNIQUE,
    target_kalori_harian DECIMAL DEFAULT 2000
);

-- 3. Buat ulang tabel history (id_user sekarang BIGINT)
CREATE TABLE public.history (
    id_history     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user        BIGINT REFERENCES public.users(id_user) ON DELETE CASCADE,
    tanggal        DATE NOT NULL,
    total_kalori   DECIMAL DEFAULT 0,
    total_protein  DECIMAL DEFAULT 0,
    total_lemak    DECIMAL DEFAULT 0,
    total_karbohidrat DECIMAL DEFAULT 0,
    UNIQUE(id_user, tanggal)
);

-- 4. Buat ulang tabel image
CREATE TABLE public.image (
    id_image       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user        BIGINT REFERENCES public.users(id_user) ON DELETE CASCADE,
    file_path      TEXT NOT NULL,
    tanggal_upload TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Buat ulang tabel food_analysis
CREATE TABLE public.food_analysis (
    id_analysis  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user      BIGINT REFERENCES public.users(id_user) ON DELETE CASCADE,
    id_image     UUID REFERENCES public.image(id_image) ON DELETE SET NULL,
    nama_makanan TEXT NOT NULL,
    kalori       DECIMAL DEFAULT 0,
    protein      DECIMAL DEFAULT 0,
    lemak        DECIMAL DEFAULT 0,
    karbohidrat  DECIMAL DEFAULT 0,
    gula         DECIMAL DEFAULT 0,
    tanggal      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Buat ulang tabel recommendation
CREATE TABLE public.recommendation (
    id_recommendation UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user           BIGINT REFERENCES public.users(id_user) ON DELETE CASCADE,
    tipe_rekomendasi  TEXT CHECK (tipe_rekomendasi IN ('defisit', 'surplus', 'maintain')),
    isi_rekomendasi   TEXT NOT NULL,
    tanggal           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Buat ulang tabel konsultasi (id_user sekarang BIGINT)
CREATE TABLE public.konsultasi (
    id_konsultasi     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user           BIGINT NOT NULL REFERENCES public.users(id_user) ON DELETE CASCADE,
    pesan_coachbot    TEXT NOT NULL,
    status            TEXT DEFAULT 'menunggu' CHECK (status IN ('menunggu', 'selesai', 'dibatalkan')),
    catatan_ahli_gizi TEXT DEFAULT '',
    tanggal           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Buat ulang tabel chat_konsultasi
CREATE TABLE public.chat_konsultasi (
    id_chat       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_konsultasi UUID NOT NULL REFERENCES public.konsultasi(id_konsultasi) ON DELETE CASCADE,
    pengirim      TEXT NOT NULL CHECK (pengirim IN ('user', 'ahli_gizi')),
    pesan         TEXT NOT NULL,
    tanggal       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. Setup RLS untuk semua tabel
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.image ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.konsultasi ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_konsultasi ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for API" ON public.users FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.history FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.image FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.food_analysis FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.recommendation FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.konsultasi FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.chat_konsultasi FOR ALL USING (true);
