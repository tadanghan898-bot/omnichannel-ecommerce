#!/usr/bin/env python3
"""
Run Supabase migrations via Management API
"""
import subprocess, json, os, sys

TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
PROJECT = "peznevsvvmtdhafursvd"

def sql(q):
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.supabase.com/v1/projects/{PROJECT}/database/query",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", f"apikey: {TOKEN}",
        "-d", json.dumps({"query": q})
    ], capture_output=True, text=True, timeout=30)
    return r.returncode == 0

def main():
    if not TOKEN:
        print("ERROR: SUPABASE_ACCESS_TOKEN not set")
        sys.exit(1)

    # Migration 001
    print("[1/2] Applying schema...")
    with open("supabase/migrations/001_init_schema.sql") as f:
        content = f.read()

    ok = fail = 0
    for stmt in content.split(";"):
        s = stmt.strip()
        if not s or s.startswith("--"):
            continue
        if sql(s):
            ok += 1
        else:
            fail += 1
        if (ok + fail) % 20 == 0:
            print(f"  Progress: {ok} ok, {fail} fail")

    print(f"  Schema: {ok} ok, {fail} failed")

    # Migration 002
    print("[2/2] Applying seed...")
    with open("supabase/migrations/002_seed_data.sql") as f:
        content = f.read()

    ok = fail = 0
    for stmt in content.split(";"):
        s = stmt.strip()
        if not s or s.startswith("--") or not s.startswith("INSERT"):
            continue
        if sql(s):
            ok += 1
        else:
            fail += 1

    print(f"  Seed: {ok} ok, {fail} failed")

    # Verify
    print("[VERIFY] Checking tables...")
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.supabase.com/v1/projects/{PROJECT}/database/query",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", f"apikey: {TOKEN}",
        "-d", json.dumps({"query": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"})
    ], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            tables = json.loads(r.stdout)
            print(f"  Tables ({len(tables)}):")
            for t in tables:
                print(f"    - {t.get('table_name')}")
        except:
            print(f"  Response: {r.stdout}")

    print("\nMIGRATION COMPLETE")

if __name__ == "__main__":
    main()
