@echo off
title Menjalankan Jimamet 2.0
echo ==============================================
echo       Memulai Server Jimamet 2.0
echo ==============================================
echo.

echo Menyiapkan Backend (Django + Daphne di Port 8000)...
:: Mematikan proses lama di port 8000 jika ada
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($conn) { $conn | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }"
start "Jimamet - Backend" cmd /k "cd backend && title Jimamet Backend && python -m daphne -b 127.0.0.1 -p 8000 config.asgi:application"

echo Menyiapkan Frontend (Next.js di Port 3000)...
start "Jimamet - Frontend" cmd /k "cd frontend && title Jimamet Frontend && npm run dev"

echo.
echo Selesai! Frontend dan Backend sedang berjalan di jendela (window) terpisah.
echo Anda bisa menutup jendela ini.
