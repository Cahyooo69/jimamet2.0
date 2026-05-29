-- ─────────────────────────────────────────────────────────────────────────────
-- Migrasi: Tambah Tabel ahli_gizi + konsultasi
-- Jalankan skrip ini di Supabase SQL Editor
-- ─────────────────────────────────────────────────────────────────────────────

-- 6. Tabel Ahli Gizi
CREATE TABLE IF NOT EXISTS public.ahli_gizi (
    id_ahli_gizi UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama          TEXT NOT NULL,
    username      TEXT NOT NULL UNIQUE,
    password      TEXT NOT NULL,
    email         TEXT NOT NULL,
    spesialisasi  TEXT DEFAULT 'Gizi Klinik',
    no_str        TEXT DEFAULT '',
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Tabel Konsultasi (Rujukan CoachBot → Ahli Gizi)
CREATE TABLE IF NOT EXISTS public.konsultasi (
    id_konsultasi      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user            TEXT NOT NULL REFERENCES public.users(id_user) ON DELETE CASCADE,
    pesan_coachbot     TEXT NOT NULL,
    status             TEXT DEFAULT 'menunggu' CHECK (status IN ('menunggu', 'selesai', 'dibatalkan')),
    catatan_ahli_gizi  TEXT DEFAULT '',
    tanggal            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Setup RLS
ALTER TABLE public.ahli_gizi ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for API" ON public.ahli_gizi FOR ALL USING (true);

ALTER TABLE public.konsultasi ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for API" ON public.konsultasi FOR ALL USING (true);

-- Dummy data ahli gizi
INSERT INTO public.ahli_gizi (nama, username, password, email, spesialisasi, no_str)
VALUES (
    'Dr. Sarah Amelia, S.Gz',
    'drsarah',
    'Gizi1234!',
    'sarah.amelia@jimamet.id',
    'Gizi Klinik & Dietetik',
    'STR-GZ-2024-001'
) ON CONFLICT (username) DO NOTHING;
