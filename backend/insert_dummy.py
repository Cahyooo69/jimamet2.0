import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.supabase_client import supabase
from datetime import date, timedelta
import random

def insert_dummy():
    username = "memet"
    full_name = "Memet Kurniawan"
    
    # 1. Create User in Django
    try:
        user = User.objects.get(username=username)
        print(f"Found existing Django user: {username} (ID: {user.id})")
    except User.DoesNotExist:
        print(f"Error: User {username} does not exist. Please register via frontend first.")
        return



    user_id_str = str(user.id)

    # 2. Check/Create Supabase Profile
    profiles = supabase.select('users', {'id_user': f'eq.{user_id_str}'})
    if not profiles:
        supabase.insert('users', {
            'id_user': user_id_str,
            'nama': full_name,
            'umur': 25,
            'tinggi_badan': 175,
            'berat_badan': 70,
            'aktivitas_harian': 'moderate',
            'email': user.email,
            'password': '[DUMMY]',
            'target_kalori_harian': 2500
        })
        print("Created Supabase Profile for Memet")

    # 3. Create Dummy Data for the last 3 days
    foods = [
        {"name": "Nasi Goreng Spesial", "cal": 600, "prot": 15, "fat": 25, "carb": 80},
        {"name": "Sate Ayam (10 tusuk)", "cal": 450, "prot": 35, "fat": 20, "carb": 15},
        {"name": "Ayam Penyet + Nasi", "cal": 700, "prot": 40, "fat": 30, "carb": 75},
        {"name": "Gado-Gado", "cal": 350, "prot": 12, "fat": 15, "carb": 40},
        {"name": "Es Teh Manis", "cal": 150, "prot": 0, "fat": 0, "carb": 35},
        {"name": "Bubur Kacang Ijo", "cal": 250, "prot": 8, "fat": 5, "carb": 45},
    ]

    for i in range(3):
        target_date = date.today() - timedelta(days=i)
        target_date_str = target_date.isoformat()
        
        # Pick 2-3 random foods for the day
        daily_foods = random.sample(foods, random.randint(2, 3))
        
        tot_cal = 0
        tot_prot = 0
        tot_fat = 0
        tot_carb = 0

        for f in daily_foods:
            # Insert into food_analysis
            supabase.insert('food_analysis', {
                'id_user': user_id_str,
                'nama_makanan': f["name"],
                'kalori': f["cal"],
                'protein': f["prot"],
                'lemak': f["fat"],
                'karbohidrat': f["carb"],
                'gula': random.randint(5, 20),
                'tanggal': f"{target_date_str}T12:00:00Z"
            })
            tot_cal += f["cal"]
            tot_prot += f["prot"]
            tot_fat += f["fat"]
            tot_carb += f["carb"]
            print(f"Inserted food {f['name']} on {target_date_str}")
            
        # Update or Insert History
        histories = supabase.select('history', {
            'id_user': f'eq.{user_id_str}',
            'tanggal': f'eq.{target_date_str}'
        })
        
        if histories:
            curr = histories[0]
            supabase.update('history', {'id_history': curr['id_history']}, {
                'total_kalori': float(curr.get('total_kalori', 0) or 0) + tot_cal,
                'total_protein': float(curr.get('total_protein', 0) or 0) + tot_prot,
                'total_lemak': float(curr.get('total_lemak', 0) or 0) + tot_fat,
                'total_karbohidrat': float(curr.get('total_karbohidrat', 0) or 0) + tot_carb,
            })
        else:
            supabase.insert('history', {
                'id_user': user_id_str,
                'tanggal': target_date_str,
                'total_kalori': tot_cal,
                'total_protein': tot_prot,
                'total_lemak': tot_fat,
                'total_karbohidrat': tot_carb,
            })
        print(f"Updated history for {target_date_str}")

if __name__ == '__main__':
    insert_dummy()
    print("Done!")
