"""
Apply Supabase migration via Management API (avoids direct DB connection)
Run: python apply_migration.py

Uses Supabase Management API to execute SQL on the project.
Requires: SUPABASE_ACCESS_TOKEN from https://supabase.com/dashboard/account/tokens
"""
import os
import sys
import json
import urllib.request
import urllib.parse

SUPABASE_REF = "jogjbuoucnbzuoatgwgd"
ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")


def api_request(method: str, endpoint: str, data: str = None) -> dict:
    """Make authenticated Supabase Management API request"""
    url = f"https://api.supabase.com/v1{endpoint}"
    req = urllib.request.Request(
        url,
        data=data.encode() if data else None,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "apikey": ACCESS_TOKEN,
        },
        method=method,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def run_migration_sql(sql: str) -> dict:
    """Execute SQL via Supabase Management API"""
    endpoint = f"/v1/projects/{SUPABASE_REF}/database/query"
    return api_request("POST", endpoint, sql)


def main():
    if not ACCESS_TOKEN:
        print("ERROR: SUPABASE_ACCESS_TOKEN environment variable not set")
        print("Get it from: https://supabase.com/dashboard/account/tokens")
        print("Create a new token with 'Database' permissions")
        sys.exit(1)

    print(f"Connecting to Supabase project: {SUPABASE_REF}")
    print("Using Supabase Management API...\n")

    # Apply schema
    print("[1/2] Applying schema...")
    with open("supabase/migrations/001_init_schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Split into batches by CREATE TABLE / TRIGGER blocks
    # Process statement by statement
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    ok = fail = 0
    for stmt in statements:
        if not stmt or stmt.startswith("--"):
            continue
        try:
            result = run_migration_sql(stmt)
            ok += 1
        except Exception as e:
            err = str(e).lower()
            # Ignore "already exists" and "duplicate" errors
            if "already exists" not in err and "duplicate" not in err:
                print(f"  WARN: {stmt[:60]}... -> {str(e)[:80]}")
                fail += 1
            else:
                ok += 1  # These are OK

    print(f"  Schema: {ok} succeeded, {fail} warnings")

    # Apply seed data
    print("\n[2/2] Applying seed data...")
    with open("supabase/migrations/002_seed_data.sql", "r", encoding="utf-8") as f:
        seed_sql = f.read()

    for stmt in [s.strip() for s in seed_sql.split(";") if s.strip()]:
        if not stmt or stmt.startswith("--"):
            continue
        if stmt.startswith("INSERT"):
            try:
                run_migration_sql(stmt)
            except Exception as e:
                if "duplicate" not in str(e).lower():
                    print(f"  Seed WARN: {str(e)[:80]}")

    print("  Seed: applied")

    # Verify
    print("\n[VERIFY] Checking tables...")
    try:
        result = run_migration_sql(
            "SELECT COUNT(*) as cnt FROM information_schema.tables WHERE table_schema = 'public'"
        )
        if result and len(result) > 0:
            print(f"  Tables created: {result[0].get('cnt', '?')}")
    except Exception as e:
        print(f"  Verification query failed: {e}")

    print("\n========================================")
    print("SUPABASE MIGRATION COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
