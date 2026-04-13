"""Verify Supabase migration - count tables"""
import psycopg2, os

db_pass = os.environ.get("DB_PASS", "")
url = f"postgresql://postgres:{db_pass}@db.jogjbuoucnbzuoatgwgd.supabase.co:5432/postgres"

conn = psycopg2.connect(url)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
count = cur.fetchone()[0]
print(f"Tables created: {count}")

if count > 0:
    print("\nTables:")
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    for row in cur.fetchall():
        print(f"  - {row[0]}")

cur.close()
conn.close()
