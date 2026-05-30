import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith('"') and db_url.endswith('"'):
    db_url = db_url[1:-1] # strip quotes

if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

# we need to inject the password into the url since it is not in DATABASE_URL
parsed = urlparse(db_url)
password = os.getenv("DATABASE_PASSWORD")

conn_string = f"postgresql://postgres:{password}@{parsed.hostname}:{parsed.port}{parsed.path}"

try:
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    with open('sql/coachbot_chat_migration.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    cursor.execute(sql)
    print("Migration applied successfully!")
    
except Exception as e:
    print(f"Error applying migration: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
