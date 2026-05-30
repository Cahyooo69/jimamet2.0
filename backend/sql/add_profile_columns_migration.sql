-- ═══════════════════════════════════════════════════════════════════════════
-- MIGRATION: Add missing profile columns to 'users' table
-- Columns: jenis_kelamin (gender), goal (health goal)
-- Run in Supabase Dashboard → SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════

-- Add gender column
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS jenis_kelamin TEXT DEFAULT 'male';

-- Add health goal column
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS goal TEXT DEFAULT 'maintain';
