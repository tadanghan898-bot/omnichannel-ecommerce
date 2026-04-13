"""Verify Supabase migration - count tables"""
import psycopg2, os, urllib.parse

db_pass = os.environ.get("DB_PASS", "")
encoded_pass = urllib.parse.quote(db_pass, safe='')
url = f"postgresql://postgres:{encoded_pass}@db.peznevsvvmtdhafursvd.supabase.co:6543/postgres?sslmode=require"

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
