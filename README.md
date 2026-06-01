# Jimamet 2.0 - Medical Nutrition Platform

Jimamet adalah platform analisis nutrisi klinis berbasis AI yang memungkinkan pengguna untuk melacak konsumsi makanan harian, mengelola profil kesehatan, dan mendapatkan rekomendasi nutrisi cerdas secara real-time.

Proyek ini dibangun menggunakan:
- **Frontend**: Next.js (React), TypeScript, CSS Modules
- **Backend**: Django (Python), Django REST Framework
- **Database**: Supabase (PostgreSQL) — satu-satunya database, tidak ada SQLite
- **AI Engine**: Google Gemini 2.5 Flash (untuk NutriCoach AI)

---

## 🛠️ Persyaratan Sistem (Prerequisites)

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
3. Salin seluruh isi file **`backend/sql/schema_v2.sql`** lalu *paste* ke SQL Editor.
4. Klik **Run** untuk membuat semua tabel + data dummy ahli gizi.
5. Buka menu **Project Settings → API** untuk mendapatkan **Project URL** dan **Service Role Key**.

> ⚠️ File `schema_v2.sql` sudah mencakup **semua** tabel dan seed data. Hanya perlu dijalankan **sekali saja**.

---

### 3. Setup Backend (Django)

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

**Jalankan Migrasi Django (struktur internal Django saja):**
```bash
python manage.py migrate
```

> 💡 Perintah ini hanya membuat tabel internal Django (sesi, admin). **Semua data aplikasi disimpan di Supabase**.

**Jalankan Server Backend:**
```bash
python manage.py runserver 8000
```
Server berjalan di `http://localhost:8000`.

---

### 4. Setup Frontend (Next.js)

Buka terminal baru:

```bash
cd frontend
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

### Backend — MVC Architecture

Backend menggunakan arsitektur **Model–Controller–Service** yang memisahkan tanggung jawab secara jelas:

```
Request → Controller → Service → Model → Supabase
                                           ↓
Response ← Controller ← Service ← Model ← Supabase
```

| Layer | Folder | Tanggung Jawab |
|---|---|---|
| **Controller** | `api/controllers/` | Menerima HTTP request, mengirim response |
| **Service** | `api/services/` | Business logic (validasi, kalkulasi, dsb.) |
| **Model** | `api/models/` | Data access layer (query ke Supabase) |
| **Cache** | `api/cache.py` | Caching token & data sering diakses |
| **Auth** | `api/supabase_auth.py` | Custom DRF authentication backend |

### Database — Supabase Only (Schema V2)

Seluruh data disimpan di **Supabase (PostgreSQL)** dengan penamaan English:

| Tabel | Isi |
|---|---|
| `users` | Akun user (id, username, email, password hash, token) |
| `food_records` | Riwayat makanan yang dianalisis |
| `daily_summary` | Rekapitulasi nutrisi harian per user |
| `images` | Gambar makanan yang di-upload |
| `recommendations` | Rekomendasi nutrisi |
| `nutritionists` | Akun ahli gizi |
| `consultations` | Sesi konsultasi user → ahli gizi |
| `consultation_messages` | Chat antar user & ahli gizi |
| `coach_sessions` | Sesi chat NutriCoach AI |
| `coach_messages` | Pesan chat dalam sesi NutriCoach AI |

### Autentikasi — Custom Supabase Token Auth

- Tidak menggunakan Django User model atau `rest_framework.authtoken`
- Password di-hash menggunakan **PBKDF2** (Django hasher)
- Token sesi disimpan di kolom `users.token` di Supabase
- Setiap login, token **dirotasi** (token baru digenerate)
- Token auth di-**cache** 5 menit untuk performa
- Header: `Authorization: Token <token>`
- Mendukung 2 role: **user** (pasien) dan **ahli_gizi** (nutritionist)

### Alur Register & Login
```
Register:
  Input (username, email, password)
    → Controller menerima request
    → AuthService.register() — validasi, hash, generate token
    → UserModel.create() — INSERT ke Supabase
    → Return token + id (BIGSERIAL auto-increment)

Login:
  Input (username, password)
    → Cek tabel nutritionists dulu (plain password)
    → Jika bukan, cek tabel users (verify PBKDF2 hash)
    → Rotate token → Return token baru + role
```

---

## 🔑 Akun Uji Coba (Test Credentials)

**👨‍⚕️ Ahli Gizi (Nutritionist Portal — `/ahli-gizi`)**
- **Username:** `drsarah`
- **Password:** `Gizi1234!`

**👤 Pasien (User Dashboard — `/dashboard`)**
- *Belum ada akun default.* Klik **"Belum punya akun? Daftar"** di halaman Login untuk membuat akun pasien baru.

---

## 📁 Struktur Project

```
jimamet2.0/
├── backend/
│   ├── api/
│   │   ├── controllers/        # HTTP layer (request → response)
│   │   │   ├── auth_controller.py
│   │   │   ├── profile_controller.py
│   │   │   ├── analysis_controller.py
│   │   │   ├── consultation_controller.py
│   │   │   ├── coach_chat_controller.py
│   │   │   └── prediction_controller.py
│   │   ├── services/           # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── profile_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── consultation_service.py
│   │   │   ├── coach_chat_service.py
│   │   │   └── prediction_service.py
│   │   ├── models/             # Data access layer (Supabase queries)
│   │   │   ├── user_model.py
│   │   │   ├── food_record_model.py
│   │   │   ├── consultation_model.py
│   │   │   ├── coach_session_model.py
│   │   │   └── ...
│   │   ├── supabase_auth.py    # Custom DRF auth backend
│   │   ├── supabase_client.py  # REST client untuk Supabase
│   │   ├── cache.py            # Caching layer (TTL-based)
│   │   └── urls.py             # API route definitions
│   ├── config/                 # Django settings, wsgi
│   ├── sql/
│   │   └── schema_v2.sql       # ← Jalankan ini di Supabase SQL Editor
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/      # User dashboard (pasien)
│   │   │   ├── ahli-gizi/      # Nutritionist portal
│   │   │   ├── login/          # Login & Register page
│   │   │   └── page.tsx        # Landing page
│   │   └── lib/api.ts          # API client (fetch helper)
│   └── .env.local              # Buat sendiri (tidak di-commit)
└── README.md
```

---

## 🌐 API Endpoints

### Auth
| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/health/` | Health check | ❌ |
| POST | `/api/auth/register/` | Registrasi user baru | ❌ |
| POST | `/api/auth/login/` | Login (user atau ahli gizi) | ❌ |
| POST | `/api/auth/logout/` | Logout (hapus token) | ✅ |
| GET | `/api/auth/me/` | Info user yang sedang login | ✅ |

### Profile
| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/profile/` | Ambil profil user | ✅ |
| PUT | `/api/profile/update/` | Update profil user | ✅ |

### Food Analysis & Dashboard
| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/food/` | List riwayat makanan | ✅ |
| POST | `/api/food/create/` | Tambah catatan makanan | ✅ |
| GET | `/api/food/<id>/` | Detail satu makanan | ✅ |
| DELETE | `/api/food/<id>/delete/` | Hapus catatan makanan | ✅ |
| GET | `/api/dashboard/summary/` | Ringkasan nutrisi harian | ✅ |

### NutriCoach AI (Session-based)
| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/coach/sessions/` | List sesi chat AI | ✅ |
| POST | `/api/coach/sessions/create/` | Buat sesi baru | ✅ |
| GET | `/api/coach/sessions/<id>/` | Detail sesi + pesan | ✅ |
| DELETE | `/api/coach/sessions/<id>/delete/` | Hapus sesi | ✅ |
| POST | `/api/coach/sessions/<id>/chat/` | Kirim pesan ke AI | ✅ |

### Konsultasi (User ↔ Ahli Gizi)
| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/consultations/` | Daftar semua konsultasi | ❌ |
| POST | `/api/consultations/create/` | Buat permintaan konsultasi | ✅ |
| PATCH | `/api/consultations/<id>/update/` | Update status konsultasi | ❌ |
| DELETE | `/api/consultations/<id>/delete/` | Hapus konsultasi | ❌ |
| GET | `/api/consultations/<id>/chat/` | List pesan chat | ❌ |
| POST | `/api/consultations/<id>/chat/send/` | Kirim pesan chat | ❌ |
| DELETE | `/api/chat/<id>/delete/` | Hapus pesan chat | ❌ |

---

Selamat mengembangkan! 🚀
