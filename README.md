# Jimamet 2.0 - Medical Nutrition Platform

Jimamet adalah platform analisis nutrisi klinis berbasis AI yang memungkinkan pengguna untuk melacak konsumsi makanan harian, mengelola profil kesehatan, dan mendapatkan rekomendasi nutrisi cerdas secara real-time.

Proyek ini dibangun menggunakan:
- **Frontend**: Next.js (React), TypeScript, CSS Modules
- **Backend**: Django (Python), Django REST Framework
- **Database**: Supabase (PostgreSQL)
- **AI Engine**: Google Gemini 2.5 Flash (untuk NutriCoach AI)

---

## 🛠️ Persyaratan Sistem (Prerequisites)

Sebelum menjalankan proyek ini, pastikan komputer Anda telah menginstal:
1. **Node.js** (Minimal versi 18.x) & **npm**
2. **Python** (Minimal versi 3.10)
3. Akun **Supabase** (untuk database)

---

## 🚀 Cara Menjalankan Proyek Secara Lokal

### 1. Clone Repository
Buka terminal dan jalankan perintah berikut:
```bash
git clone https://github.com/Cahyooo69/jimamet2.0.git
cd jimamet2.0
```

### 2. Setup Database Supabase
1. Buat project baru di [Supabase Dashboard](https://supabase.com/dashboard).
2. Buka menu **SQL Editor**.
3. Salin seluruh isi file `backend/supabase_schema.sql` lalu *paste* ke SQL Editor.
4. Klik **Run** untuk membuat tabel `user_profiles` dan `food_records`.
5. Buka menu **Project Settings -> API** di Supabase untuk mendapatkan URL dan Service Role Key.

---

### 3. Setup Backend (Django)

Buka terminal baru untuk backend:

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
1. Duplikat/copy file `backend/.env.example` dan ubah namanya menjadi `backend/.env` (jika belum ada).
2. Isi nilai yang ada di `.env` sesuai dengan kredensial Supabase dan Gemini AI Anda:
   ```env
   SECRET_KEY=your-django-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   
   SUPABASE_URL=https://[YOUR_PROJECT_REF].supabase.co
   SUPABASE_KEY=[YOUR_SUPABASE_SERVICE_ROLE_KEY]
   SUPABASE_REST_URL=https://[YOUR_PROJECT_REF].supabase.co/rest/v1
   
   GEMINI_API_KEY=your-google-gemini-api-key
   ```
*(Catatan: `SUPABASE_REST_URL` digunakan untuk panggilan REST API aplikasi, sedangkan `GEMINI_API_KEY` digunakan untuk fitur AI CoachBot).*

**Jalankan Migrasi Database Lokal (SQLite):**
```bash
python manage.py migrate
```
*(Catatan: Sistem autentikasi / akun pengguna secara default menggunakan database SQLite bawaan Django, sementara data lainnya menggunakan Supabase).*

**Jalankan Server Backend:**
```bash
python manage.py runserver 8000
```
Server backend akan berjalan di `http://localhost:8000`.

---

### 4. Setup Frontend (Next.js)

Buka terminal baru untuk frontend (biarkan terminal backend tetap berjalan):

```bash
cd frontend
```

**Install Dependencies:**
```bash
npm install
```

**Konfigurasi Environment Frontend:**
1. Buat file baru bernama `.env.local` di dalam folder `frontend/`.
2. Masukkan URL API backend lokal Anda:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

**Jalankan Server Frontend:**
```bash
npm run dev
```
Buka browser dan akses **`http://localhost:3000`**. 

---

## 💡 Arsitektur Singkat
- **Autentikasi**: Menggunakan sistem Token dari Django REST Framework. Token disimpan secara lokal di `localStorage` frontend.
- **Komunikasi Data**: Frontend meminta data melalui API Django (`/api/...`), lalu Django akan bertindak sebagai *proxy* aman yang berkomunikasi dengan Supabase menggunakan `SupabaseClient` (REST API).
- **Food Analysis**: Menerima input gambar/teks di frontend, dikirim ke AI Backend, yang kemudian hasil nutrisinya akan disimpan ke Supabase melalui endpoint Django.

---

## 🔑 Akun Uji Coba (Test Credentials)

Untuk mencoba fitur aplikasi, Anda dapat menggunakan kredensial berikut:

**👨‍⚕️ Ahli Gizi (Nutritionist Portal)**
- **Username:** `drsarah`
- **Password:** `Gizi1234!`

**👤 Pasien (User Dashboard)**
- *Belum ada akun default.* Silakan klik **"Belum punya akun? Daftar"** di halaman Login untuk membuat akun pasien baru.

---

## 🗄️ Manajemen Data User (SQLite ↔ Supabase)

Sistem ini menggunakan **dua database**:
- **Django SQLite** (`backend/db.sqlite3`) — menyimpan akun & autentikasi user
- **Supabase** — menyimpan profil & data user (sumber kebenaran / *source of truth*)

> ⚠️ Jika kamu menghapus user di Supabase, data di SQLite **tidak otomatis terhapus**. Gunakan cara-cara di bawah untuk sinkronisasi manual.

### Cara Hapus User dari SQLite

**Opsi 1 — Django Shell (hapus 1 user):**
```bash
cd backend
python manage.py shell
```
```python
from django.contrib.auth.models import User

user = User.objects.get(username="nama_user")  # cari berdasarkan username
try:
    user.auth_token.delete()  # hapus token login dulu
except Exception:
    pass
user.delete()  # hapus user dari SQLite
exit()
```

**Opsi 2 — Management Command `sync_users` (hapus semua orphan sekaligus):**

Orphan = user yang ada di SQLite tapi **sudah dihapus dari Supabase**.

```bash
cd backend

# Lihat siapa saja yang perlu dihapus (dry-run, aman, tidak ada yang dihapus)
python manage.py sync_users

# Hapus semua orphan user dari SQLite secara permanen
python manage.py sync_users --delete
```

### Sinkronisasi Otomatis

Sistem sudah dilengkapi sync otomatis pada dua titik:

| Aksi User | Perilaku Sistem |
|---|---|
| User dihapus dari Supabase → **coba login** | Login ditolak, Django user & token auto-dihapus dari SQLite |
| User dihapus dari Supabase → **coba register ulang** | Django user lama (orphan) di-cleanup otomatis, registrasi baru berhasil |

---

## 🔑 Akun Uji Coba (Test Credentials)

Untuk mencoba fitur aplikasi, Anda dapat menggunakan kredensial berikut:

**👨‍⚕️ Ahli Gizi (Nutritionist Portal)**
- **Username:** `drsarah`
- **Password:** `Gizi1234!`

**👤 Pasien (User Dashboard)**
- *Belum ada akun default.* Silakan klik **"Belum punya akun? Daftar"** di halaman Login untuk membuat akun pasien baru.

---

Selamat mengembangkan! 🚀
