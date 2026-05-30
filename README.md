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

### ⚡ Sinkronisasi Otomatis via Supabase Webhook

Saat user dihapus dari Supabase, sistem dapat **otomatis** menghapus Django user dari SQLite menggunakan **Supabase Database Webhook**.

#### Cara Setup (sekali saja):

**Langkah 1 — Isi `.env` backend:**
```env
SUPABASE_WEBHOOK_SECRET=isi-bebas-kata-sandi-rahasia
```

**Langkah 2 — Buka Supabase Dashboard:**
1. Masuk ke [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Pilih project → **Database** → **Webhooks**
3. Klik **"Create a new webhook"**

**Langkah 3 — Konfigurasi webhook:**

| Field | Nilai |
|---|---|
| **Name** | `sync-delete-django-user` |
| **Table** | `users` |
| **Events** | ✅ `DELETE` saja |
| **Type** | HTTP Request |
| **Method** | `POST` |
| **URL** | `http://<IP-SERVER-KAMU>:8000/api/auth/webhook/supabase/` |

**Langkah 4 — Tambah HTTP Header (untuk keamanan):**

| Header | Value |
|---|---|
| `x-webhook-secret` | nilai `SUPABASE_WEBHOOK_SECRET` di `.env` |

**Langkah 5 — Klik "Create webhook" → Selesai!** ✅

Sekarang setiap kali user dihapus dari Supabase, Django user di SQLite akan **langsung terhapus otomatis**.

---

> ⚠️ **Catatan untuk development lokal:** Supabase tidak bisa memanggil `localhost`. Gunakan [ngrok](https://ngrok.com/) untuk expose server lokal:
> ```bash
> ngrok http 8000
> # Gunakan URL ngrok (contoh: https://abc123.ngrok-free.app) sebagai base URL webhook
> ```

---

### 🔧 Sinkronisasi Manual (alternatif / cadangan)

Jika webhook belum disetup, gunakan cara manual berikut:

**Hapus 1 user via Django Shell:**
```bash
cd backend
python manage.py shell
```
```python
from django.contrib.auth.models import User

user = User.objects.get(username="nama_user")
try:
    user.auth_token.delete()
except Exception:
    pass
user.delete()
exit()
```

**Hapus semua orphan sekaligus (management command):**
```bash
cd backend

# Lihat siapa saja yang perlu dihapus (dry-run, tidak ada yang dihapus)
python manage.py sync_users

# Hapus semua orphan user dari SQLite secara permanen
python manage.py sync_users --delete
```

### 🔄 Sinkronisasi Otomatis Saat Login/Register

Selain webhook, sistem juga sudah dilengkapi sync otomatis pada dua titik:

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
