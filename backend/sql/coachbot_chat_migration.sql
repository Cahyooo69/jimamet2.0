-- ═══════════════════════════════════════════════════════════════════════════
-- MIGRATION: Create coachbot_history table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.coachbot_history (
    id_chat       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user       BIGINT NOT NULL REFERENCES public.users(id_user) ON DELETE CASCADE,
    pengirim      TEXT NOT NULL CHECK (pengirim IN ('user', 'ai')),
    pesan         TEXT NOT NULL,
    needs_consultation BOOLEAN DEFAULT FALSE,
    tanggal       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.coachbot_history ENABLE ROW LEVEL SECURITY;

-- Create policy for API access
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'coachbot_history' AND policyname = 'Enable all for API'
    ) THEN
        CREATE POLICY "Enable all for API" ON public.coachbot_history FOR ALL USING (true);
    END IF;
END $$;
