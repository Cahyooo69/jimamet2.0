# Jimamet 2.0 - Medical Nutrition Platform

Jimamet adalah platform analisis nutrisi klinis berbasis AI yang memungkinkan pengguna untuk melacak konsumsi makanan harian, mengelola profil kesehatan, dan mendapatkan rekomendasi nutrisi cerdas secara real-time.

Proyek ini dibangun menggunakan:
- **Frontend**: Next.js (React), TypeScript, CSS Modules
- **Backend**: Django (Python), Django REST Framework
- **Database**: Supabase (PostgreSQL) — satu-satunya database, tidak ada SQLite
- **AI Engine**: Google Gemini 2.5 Flash (untuk NutriCoach AI)

---

## 🛠️ Persyaratan Sistem (Prerequisites)

Sebelum menjalankan proyek ini, pastikan komputer Anda telah menginstal:
1. **Node.js** (Minimal versi 18.x) & **npm**
2. **Python** (Minimal versi 3.10)
3. Akun **Supabase** (untuk database)
4. Akun **Google AI Studio** (untuk Gemini API Key)

---

## 🚀 Cara Menjalankan Proyek Secara Lokal

### 1. Clone Repository
```bash
git clone https://github.com/Cahyooo69/jimamet2.0.git
cd jimamet2.0
```

---

### 2. Setup Database Supabase

1. Buat project baru di [Supabase Dashboard](https://supabase.com/dashboard).
2. Buka menu **SQL Editor**.
3. Salin seluruh isi file **`backend/sql/full_schema_migration.sql`** lalu *paste* ke SQL Editor.
4. Klik **Run** untuk membuat semua tabel yang dibutuhkan.
5. Jalankan juga file **`backend/sql/ahli_gizi_migration.sql`** untuk membuat tabel ahli gizi & konsultasi (beserta data dummy ahli gizi).
6. Jalankan juga file **`backend/sql/chat_konsultasi_migration.sql`** untuk membuat tabel chat konsultasi.
7. Buka menu **Project Settings → API** untuk mendapatkan **Project URL** dan **Service Role Key**.

> ⚠️ Urutan eksekusi SQL: `full_schema_migration.sql` → `ahli_gizi_migration.sql` → `chat_konsultasi_migration.sql`

---

### 3. Setup Backend (Django)

Buka terminal di folder `backend/`:

```bash
cd backend
```

**Buat Virtual Environment & Install Dependencies:**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Mac/Linux
python3 -m venv env
source env/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Konfigurasi Environment Backend:**

Copy file `.env.example` menjadi `.env`, lalu isi dengan kredensial Anda:
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

SUPABASE_URL=https://[YOUR_PROJECT_REF].supabase.co
SUPABASE_KEY=[YOUR_SUPABASE_SERVICE_ROLE_KEY]
SUPABASE_REST_URL=https://[YOUR_PROJECT_REF].supabase.co/rest/v1/

GEMINI_API_KEY=your-google-gemini-api-key
SUPABASE_WEBHOOK_SECRET=isi-bebas-rahasia-anda
```

**Jalankan Migrasi Django (hanya untuk struktur internal Django):**
```bash
python manage.py migrate
```

> 💡 Perintah ini hanya membuat tabel internal Django (sesi, admin, dll). **Data user dan semua data aplikasi disimpan di Supabase**, bukan SQLite.

**Jalankan Server Backend:**
```bash
python manage.py runserver 8000
```
Server berjalan di `http://localhost:8000`.

---

### 4. Setup Frontend (Next.js)

Buka terminal baru di folder `frontend/`:

```bash
cd frontend
```

**Install Dependencies:**
```bash
npm install
```

**Konfigurasi Environment Frontend:**

Buat file `.env.local` di dalam folder `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Jalankan Server Frontend:**
```bash
npm run dev
```
Buka browser dan akses **`http://localhost:3000`**.

---

## 💡 Arsitektur Sistem

### Database — Supabase Only
Seluruh data aplikasi disimpan di **Supabase (PostgreSQL)**. Tidak ada data user di SQLite.

| Tabel | Isi |
|---|---|
| `users` | Akun user (id_user, username, email, password hash, token sesi) |
| `food_analysis` | Riwayat makanan yang dianalisis |
| `history` | Rekapitulasi nutrisi harian |
| `konsultasi` | Sesi konsultasi ke ahli gizi |
| `chat_konsultasi` | Pesan chat antar user & ahli gizi |
| `ahli_gizi` | Data akun ahli gizi |

### Autentikasi — Custom Supabase Token Auth
- Tidak menggunakan Django User model atau `rest_framework.authtoken`
- Password di-hash menggunakan **PBKDF2** (Django hasher)
- Token sesi disimpan di kolom `users.token` di Supabase
- Setiap login, token **dirotasi** (token baru digenerate)
- Token diklaim melalui header: `Authorization: Token <token>`

### Alur Register & Login
```
Register:
  Input (username, email, password)
    → Hash password (PBKDF2)
    → Generate token acak
    → INSERT ke Supabase users table
    → Return token + id_user (auto-increment)

Login:
  Input (username, password)
    → SELECT dari Supabase by username
    → Verify password hash
    → Rotate token (generate baru, simpan ke Supabase)
    → Return token baru
```

### Komunikasi Data
```
Frontend (Next.js)
  → HTTP Request dengan Authorization: Token <token>
  → Django REST Framework
  → SupabaseTokenAuthentication (validasi token ke Supabase)
  → View logic
  → Supabase REST API
  → Response ke Frontend
```

---

## 🔑 Akun Uji Coba (Test Credentials)

**👨‍⚕️ Ahli Gizi (Nutritionist Portal)**
- **Username:** `drsarah`
- **Password:** `Gizi1234!`

**👤 Pasien (User Dashboard)**
- *Belum ada akun default.* Klik **"Belum punya akun? Daftar"** di halaman Login untuk membuat akun pasien baru.

---

## 📁 Struktur Project

```
jimamet2.0/
├── backend/
│   ├── api/
│   │   ├── views/          # auth, profile, food, dashboard, konsultasi, coachbot
│   │   ├── supabase_auth.py    # Custom DRF auth backend (Supabase-based)
│   │   └── supabase_client.py  # REST client untuk Supabase
│   ├── config/             # Django settings, urls, wsgi
│   ├── sql/                # SQL migration files untuk Supabase
│   │   ├── full_schema_migration.sql   ← Jalankan ini dulu
│   │   ├── ahli_gizi_migration.sql     ← Lalu ini
│   │   └── chat_konsultasi_migration.sql ← Terakhir ini
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # Reusable UI components
│   │   └── lib/api/        # API client modules
│   └── .env.local          # Buat sendiri (tidak di-commit)
└── README.md
```

---

## 🌐 API Endpoints

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/health/` | Health check | ❌ |
| POST | `/api/auth/register/` | Registrasi user baru | ❌ |
| POST | `/api/auth/login/` | Login | ❌ |
| POST | `/api/auth/logout/` | Logout | ✅ |
| GET | `/api/auth/me/` | Info user saat ini | ✅ |
| GET | `/api/profile/` | Ambil profil user | ✅ |
| PUT | `/api/profile/update/` | Update profil user | ✅ |
| GET | `/api/food/` | List riwayat makanan | ✅ |
| POST | `/api/food/create/` | Tambah makanan | ✅ |
| DELETE | `/api/food/<id>/delete/` | Hapus makanan | ✅ |
| GET | `/api/dashboard/summary/` | Ringkasan nutrisi harian | ✅ |
| POST | `/api/coachbot/chat/` | Chat dengan NutriCoach AI | ✅ |
| POST | `/api/konsultasi/create/` | Buat sesi konsultasi | ✅ |
| GET | `/api/konsultasi/` | Daftar semua konsultasi | ❌ |

---

Selamat mengembangkan! 🚀
