import psycopg2
conn = psycopg2.connect('postgresql://postgres:jimametmbkm6@db.mldkftqbtmlkcmjganmj.supabase.co:5432/postgres')
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
print([r[0] for r in cur.fetchall()])
