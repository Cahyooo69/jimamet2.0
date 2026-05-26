-- ─────────────────────────────────────────────────────────────────────────────
-- Migrasi: Tabel Chat Konsultasi
-- Jalankan di Supabase SQL Editor
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.chat_konsultasi (
    id_chat       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_konsultasi UUID NOT NULL REFERENCES public.konsultasi(id_konsultasi) ON DELETE CASCADE,
    pengirim      TEXT NOT NULL CHECK (pengirim IN ('user', 'ahli_gizi')),
    pesan         TEXT NOT NULL,
    tanggal       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.chat_konsultasi ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'chat_konsultasi' AND policyname = 'Enable all for API'
    ) THEN
        EXECUTE 'CREATE POLICY "Enable all for API" ON public.chat_konsultasi FOR ALL USING (true)';
    END IF;
END
$$;
