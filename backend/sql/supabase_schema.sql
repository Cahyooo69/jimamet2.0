-- Drop existing tables if any (Warning: This will delete existing data)
DROP TABLE IF EXISTS public.recommendation CASCADE;
DROP TABLE IF EXISTS public.food_analysis CASCADE;
DROP TABLE IF EXISTS public.image CASCADE;
DROP TABLE IF EXISTS public.history CASCADE;
DROP TABLE IF EXISTS public.user CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;
DROP TABLE IF EXISTS public.food_records CASCADE;
DROP TABLE IF EXISTS public.user_profiles CASCADE;

-- 1. Tabel User (Sesuai diagram, menggunakan 'users' karena 'user' adalah reserved keyword di PostgreSQL)
CREATE TABLE public.users (
    id_user TEXT PRIMARY KEY, -- Menggunakan text agar bisa sinkron dengan username/id dari Django Auth
    nama TEXT NOT NULL,
    umur INTEGER DEFAULT 0,
    tinggi_badan DECIMAL DEFAULT 0,
    berat_badan DECIMAL DEFAULT 0,
    aktivitas_harian TEXT DEFAULT 'sedentary',
    email TEXT NOT NULL,
    password TEXT NOT NULL, -- Catatan: Secara praktik nyata, ini disimpan ter-hash di backend Django, namun ditambahkan di sini sesuai ERD
    target_kalori_harian DECIMAL DEFAULT 2000
);

-- 2. Tabel History
CREATE TABLE public.history (
    id_history UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user TEXT REFERENCES public.users(id_user) ON DELETE CASCADE,
    tanggal DATE NOT NULL,
    total_kalori DECIMAL DEFAULT 0,
    total_protein DECIMAL DEFAULT 0,
    total_lemak DECIMAL DEFAULT 0,
    total_karbohidrat DECIMAL DEFAULT 0,
    UNIQUE(id_user, tanggal) -- Memastikan 1 user hanya punya 1 record history per hari
);

-- 3. Tabel Image
CREATE TABLE public.image (
    id_image UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user TEXT REFERENCES public.users(id_user) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    tanggal_upload TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabel Food Analysis (Memperbaiki typo kalori_protein menjadi kalori dan protein)
CREATE TABLE public.food_analysis (
    id_analysis UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user TEXT REFERENCES public.users(id_user) ON DELETE CASCADE,
    id_image UUID REFERENCES public.image(id_image) ON DELETE SET NULL,
    nama_makanan TEXT NOT NULL,
    kalori DECIMAL DEFAULT 0,
    protein DECIMAL DEFAULT 0,
    lemak DECIMAL DEFAULT 0,
    karbohidrat DECIMAL DEFAULT 0,
    gula DECIMAL DEFAULT 0,
    tanggal TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tabel Recommendation
CREATE TABLE public.recommendation (
    id_recommendation UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user TEXT REFERENCES public.users(id_user) ON DELETE CASCADE,
    tipe_rekomendasi TEXT CHECK (tipe_rekomendasi IN ('defisit', 'surplus', 'maintain')),
    isi_rekomendasi TEXT NOT NULL,
    tanggal TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Setup RLS (Row Level Security) - Optional tapi direkomendasikan
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.image ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendation ENABLE ROW LEVEL SECURITY;

-- Buat policy agar service role / API bisa mengakses semuanya
CREATE POLICY "Enable all for API" ON public.users FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.history FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.image FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.food_analysis FOR ALL USING (true);
CREATE POLICY "Enable all for API" ON public.recommendation FOR ALL USING (true);
