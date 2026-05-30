import os
import sys
import requests
import psycopg2
from urllib.parse import urlparse
import django

sys.path.append("d:/projects/jimamet/codes/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.conf import settings


def main():
    rest_url = settings.SUPABASE_REST_URL.rstrip("/")
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    # 1. Fetch old users
    print("Fetching old users...")
    resp = requests.get(f"{rest_url}/users", headers=headers)
    if resp.status_code == 200:
        old_users = resp.json()
    else:
        print("Failed to fetch users:", resp.text)
        old_users = []

    print(f"Found {len(old_users)} users.")

    # 2. Apply schema migration
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith('"') and db_url.endswith('"'):
        db_url = db_url[1:-1]

    parsed = urlparse(db_url)
    password = os.getenv("DATABASE_PASSWORD")
    conn_string = f"postgresql://postgres:{password}@{parsed.hostname}:{parsed.port}{parsed.path}"

    print("Applying schema_v2.sql...")
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()

    with open("sql/schema_v2.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    cursor.execute(sql)
    print("Migration applied successfully!")
    conn.close()

    # 3. Restore users
    if old_users:
        print("Restoring users...")
        for u in old_users:
            new_u = {
                "id": u.get("id_user"),
                "username": u.get("username"),
                "full_name": u.get("nama") or "",
                "age": u.get("umur") or 0,
                "height": u.get("tinggi_badan") or 0,
                "weight": u.get("berat_badan") or 0,
                "activity_level": u.get("aktivitas_harian") or "moderate",
                "email": u.get("email"),
                "password": u.get("password"),
                "token": u.get("token"),
                "daily_calorie_target": u.get("target_kalori_harian") or 2000,
                "gender": u.get("jenis_kelamin") or "male",
                "goal": u.get("goal") or "maintain",
            }
            # drop None
            new_u = {k: v for k, v in new_u.items() if v is not None}

            resp = requests.post(f"{rest_url}/users", headers=headers, json=new_u)
            if resp.status_code in (200, 201):
                print(f"Restored user {new_u['username']}")
            else:
                print(f"Failed to restore user {new_u['username']}:", resp.text)


if __name__ == "__main__":
    main()
