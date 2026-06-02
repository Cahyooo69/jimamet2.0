import os
import random
from datetime import datetime, timedelta
from api.supabase_client import supabase
from api.models.food_record_model import FoodRecordModel

def seed_data():
    # Ambil 1 user sembarang
    res = supabase.select("users", {"limit": 1})
    if not res:
        print("Tidak ada user di database!")
        return
        
    user_id = res[0]["id"]
    print(f"Menambahkan data untuk user_id: {user_id}")
    
    # Menu makanan dummy
    menus = [
        {"name": "Nasi Goreng Spesial", "cals": 450, "p": 15, "c": 50, "f": 18, "s": 5},
        {"name": "Ayam Bakar Madu", "cals": 320, "p": 25, "c": 15, "f": 12, "s": 8},
        {"name": "Salad Sayur & Telur", "cals": 180, "p": 12, "c": 10, "f": 9, "s": 2},
        {"name": "Oatmeal Pisang Susu", "cals": 280, "p": 10, "c": 45, "f": 5, "s": 15},
        {"name": "Sate Taichan", "cals": 250, "p": 30, "c": 5, "f": 10, "s": 1},
        {"name": "Gado-Gado Lontong", "cals": 350, "p": 15, "c": 40, "f": 12, "s": 8},
        {"name": "Roti Gandum Alpukat", "cals": 220, "p": 8, "c": 25, "f": 10, "s": 3},
        {"name": "Soto Ayam Nasi", "cals": 400, "p": 20, "c": 55, "f": 10, "s": 2},
        {"name": "Ikan Salmon Panggang", "cals": 310, "p": 28, "c": 2, "f": 20, "s": 0},
        {"name": "Tumis Brokoli Daging", "cals": 240, "p": 18, "c": 12, "f": 10, "s": 4},
        {"name": "Nasi Padang Rendang", "cals": 650, "p": 25, "c": 60, "f": 30, "s": 2},
        {"name": "Nasi Kuning Komplit", "cals": 550, "p": 20, "c": 65, "f": 15, "s": 5},
    ]
    
    # 7 hari ke belakang
    now = datetime.utcnow()
    
    count = 0
    for day_offset in range(7): # 0 = hari ini, 6 = seminggu lalu
        target_date = now - timedelta(days=day_offset)
        
        # 3 kali makan (Pagi, Siang, Malam)
        # UTC + 7 = WIB.
        # Pagi WIB 07:00 -> UTC 00:00
        # Siang WIB 13:00 -> UTC 06:00
        # Malam WIB 19:00 -> UTC 12:00
        times = [
            target_date.replace(hour=0, minute=random.randint(0, 59)),
            target_date.replace(hour=6, minute=random.randint(0, 59)),
            target_date.replace(hour=12, minute=random.randint(0, 59)),
        ]
        
        for t in times:
            menu = random.choice(menus)
            FoodRecordModel.create({
                "user_id": user_id,
                "food_name": menu["name"],
                "calories": menu["cals"] + random.randint(-30, 30), # Sedikit variasi kalori
                "protein": menu["p"],
                "carbs": menu["c"],
                "fat": menu["f"],
                "sugar": menu["s"],
                "recorded_at": t.isoformat() + "Z"
            })
            count += 1
            
    print(f"Berhasil menambahkan {count} data riwayat makanan!")

seed_data()
