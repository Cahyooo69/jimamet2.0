-- ─────────────────────────────────────────────────────────────────────────────
-- Migrasi Tambahan: Tabel Konsultasi SAJA
-- Jalankan ini jika tabel ahli_gizi sudah ada sebelumnya
-- ─────────────────────────────────────────────────────────────────────────────

-- Tabel Konsultasi (Rujukan CoachBot → Ahli Gizi)
CREATE TABLE IF NOT EXISTS public.konsultasi (
    id_konsultasi      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user            TEXT NOT NULL REFERENCES public.users(id_user) ON DELETE CASCADE,
    pesan_coachbot     TEXT NOT NULL,
    status             TEXT DEFAULT 'menunggu' CHECK (status IN ('menunggu', 'selesai', 'dibatalkan')),
    catatan_ahli_gizi  TEXT DEFAULT '',
    tanggal            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Setup RLS
ALTER TABLE public.konsultasi ENABLE ROW LEVEL SECURITY;

-- Cegah error jika policy sudah ada
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'konsultasi' AND policyname = 'Enable all for API'
    ) THEN
        EXECUTE 'CREATE POLICY "Enable all for API" ON public.konsultasi FOR ALL USING (true)';
    END IF;
END
$$;
