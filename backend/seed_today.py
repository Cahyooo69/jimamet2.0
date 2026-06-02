import os
import random
from datetime import datetime, timedelta
from api.supabase_client import supabase
from api.models.food_record_model import FoodRecordModel

def seed_today():
    # Ambil 1 user sembarang
    res = supabase.select("users", {"limit": 1})
    if not res:
        print("Tidak ada user di database!")
        return
        
    user_id = res[0]["id"]
    
    menus = [
        {"name": "Nasi Kuning Pagi", "cals": 450, "p": 15, "c": 50, "f": 18, "s": 5},
        {"name": "Ayam Geprek Bawang", "cals": 620, "p": 25, "c": 15, "f": 12, "s": 8},
        {"name": "Salad Sayur Segar", "cals": 180, "p": 12, "c": 10, "f": 9, "s": 2},
        {"name": "Kopi Susu Gula Aren", "cals": 280, "p": 10, "c": 45, "f": 5, "s": 15},
    ]
    
    # Hari ini (berdasarkan waktu lokal WIB - di server kita ambil waktu UTC lalu ditambah offset jika perlu)
    # Untuk aman, kita pakai waktu yang pasti jatuh di tanggal 3 Juni 2026 (Hari ini WIB)
    now_utc = datetime.utcnow()
    # Pagi: UTC jam 00:30 (WIB 07:30)
    # Siang: UTC jam 05:00 (WIB 12:00)
    # Malam: UTC jam 12:00 (WIB 19:00)
    # Tapi karena sekarang WIB masih jam 05:30 pagi, kita inject untuk jam 07:00, 12:00, 19:00 WIB hari ini.
    # Waktu UTC saat ini: ~22:30, tanggal 2 Juni. Waktu WIB: ~05:30, tanggal 3 Juni.
    # Agar jatuh di tanggal 3 Juni UTC, kita force tanggal 3 Juni.
    
    base_date = datetime(2026, 6, 3) 
    
    times = [
        base_date.replace(hour=0, minute=30),  # Pagi WIB
        base_date.replace(hour=5, minute=0),   # Siang WIB
        base_date.replace(hour=11, minute=30), # Malam WIB
    ]
    
    count = 0
    for t in times:
        menu = random.choice(menus)
        FoodRecordModel.create({
            "user_id": user_id,
            "food_name": menu["name"],
            "calories": menu["cals"] + random.randint(-10, 10),
            "protein": menu["p"],
            "carbs": menu["c"],
            "fat": menu["f"],
            "sugar": menu["s"],
            "recorded_at": t.isoformat() + "Z"
        })
        count += 1
            
    print(f"Berhasil menambahkan {count} data untuk HARI INI!")

seed_today()
