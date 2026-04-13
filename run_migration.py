#!/usr/bin/env python3
"""
Run Supabase migrations via Management API
Splits SQL by semicolons, sends each as separate API call
"""
import subprocess, json, os, sys, re

TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
PROJECT = "peznevsvvmtdhafursvd"

def sql(q):
    """Execute SQL via Management API. Returns (success, response)."""
    payload = json.dumps({"query": q})
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.supabase.com/v1/projects/{PROJECT}/database/query",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", f"apikey: {TOKEN}",
        "-d", payload
    ], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stdout

def split_sql(content):
    """Split SQL by semicolons, handling newlines and dollar-quoting."""
    statements = []
    # Strip comments first
    lines = [re.sub(r'--.*$', '', line) for line in content.split('\n')]
    content = '\n'.join(lines)

    # Simple split by semicolon, handle $$ quoting
    current = []
    depth = 0
    i = 0
    while i < len(content):
        # Check for $$ quoting
        if i + 1 < len(content) and content[i] == '$' and content[i + 1] == '$':
            if depth == 0:
                depth = 1
                current.append('$$')
                i += 2
                continue
            elif depth == 1:
                depth = 0
                current.append('$$')
                i += 2
                continue
        elif content[i] == ';':
            if depth == 0:
                stmt = ''.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue
        current.append(content[i])
        i += 1

    stmt = ''.join(current).strip()
    if stmt:
        statements.append(stmt)
    return statements

def main():
    if not TOKEN:
        print("ERROR: SUPABASE_ACCESS_TOKEN not set")
        sys.exit(1)

    # Migration 001
    print("[1/2] Applying schema...")
    with open("supabase/migrations/001_init_schema.sql") as f:
        content = f.read()

    content = content.replace("jogjbuoucnbzuoatgwgd", PROJECT)
    stmts = split_sql(content)
    print(f"  Parsed {len(stmts)} statements")
    ok = fail = 0
    for stmt in stmts:
        s, resp = sql(stmt)
        if s:
            ok += 1
        else:
            fail += 1
            if fail <= 3:
                print(f"  WARN: {stmt[:60]}... -> {resp[:100]}")
    print(f"  Schema: {ok} ok, {fail} failed")

    # Migration 002
    print("[2/2] Applying seed...")
    with open("supabase/migrations/002_seed_data.sql") as f:
        content = f.read()

    stmts = split_sql(content)
    print(f"  Parsed {len(stmts)} statements")
    ok = fail = 0
    for stmt in stmts:
        s, resp = sql(stmt)
        if s:
            ok += 1
        else:
            fail += 1
    print(f"  Seed: {ok} ok, {fail} failed")

    # Verify
    print("[VERIFY] Tables...")
    s, resp = sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    if s:
        try:
            tables = json.loads(resp)
            print(f"  Tables ({len(tables)}):")
            for t in tables:
                print(f"    - {t.get('table_name')}")
        except:
            print(f"  Response: {resp[:200]}")
    else:
        print(f"  Verify failed: {resp}")

    print("\nDONE")

if __name__ == "__main__":
    main()
