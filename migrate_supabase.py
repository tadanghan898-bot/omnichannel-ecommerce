"""
Supabase Migration Runner
Run: python migrate_supabase.py

Requires:
  pip install psycopg2-binary

Environment:
  SUPABASE_DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
"""
import os
import sys

DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL", "")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def run_migration():
    if not DATABASE_URL:
        print("ERROR: SUPABASE_DATABASE_URL environment variable not set")
        print("Get it from: Supabase Dashboard > Settings > Database")
        sys.exit(1)

    import psycopg2

    print("Connecting to Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # Migration 001: Schema
    print("\n[1/2] Applying schema migration...")
    with open("supabase/migrations/001_init_schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Split by table and execute each
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    for i, stmt in enumerate(statements):
        if stmt.startswith("CREATE") or stmt.startswith("ALTER") or stmt.startswith("INSERT"):
            try:
                cur.execute(stmt)
            except Exception as e:
                # Ignore "already exists" errors
                if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                    print(f"  Warning: {e}")

    print("  Schema applied (tables, indexes, triggers, RLS)")

    # Migration 002: Seed data
    print("\n[2/2] Applying seed data...")
    with open("supabase/migrations/002_seed_data.sql", "r", encoding="utf-8") as f:
        seed_sql = f.read()

    statements = [s.strip() for s in seed_sql.split(";") if s.strip()]
    for stmt in statements:
        if stmt.startswith("INSERT"):
            try:
                cur.execute(stmt)
            except Exception as e:
                if "duplicate" not in str(e).lower():
                    print(f"  Warning: {e}")

    print("  Seed data applied (admin user, categories, brands, plans)")

    cur.close()
    conn.close()

    print("\n========================================")
    print("SUPABASE MIGRATION COMPLETE")
    print("========================================")
    print("\nYour Supabase PostgreSQL database is now ready.")
    print("\nNext:")
    print("  1. Deploy to Vercel: npx vercel --prod")
    print("  2. Set environment variables in Vercel dashboard")
    print("  3. Connect marketplace accounts at /marketplace")


if __name__ == "__main__":
    run_migration()
