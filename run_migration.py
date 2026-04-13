#!/usr/bin/env python3
"""
Run Supabase migrations via Management API
Smart parsing: split on semicolons while handling multi-line statements
"""
import subprocess, json, os, sys, re

TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
PROJECT = "peznevsvvmtdhafursvd"

def sql(q):
    """Execute SQL via Management API. Returns (success, response)."""
    payload = json.dumps({"query": q}).encode()
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.supabase.com/v1/projects/{PROJECT}/database/query",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", f"apikey: {TOKEN}",
        "--data-binary", "@-"
    ], input=payload, capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stdout

def parse_statements(content):
    """Split SQL content into statements, handling multi-line correctly."""
    # Remove SQL comments
    lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    content = "\n".join(lines)

    # Split on semicolons, tracking $$ dollar-quoting
    statements = []
    current = []
    in_dollar = False
    dollar_char = None
    i = 0
    while i < len(content):
        c = content[i]
        if not in_dollar and c == '$':
            # Check for dollar quote start/end
            j = i + 1
            while j < len(content) and content[j] == '$':
                j += 1
            tag = content[i:j]
            if not current and tag:  # Start of $$...$$
                in_dollar = True
                dollar_char = tag
                current.append(content[i:j])
                i = j
                continue
            elif in_dollar and current and "".join(current).count(dollar_char) % 2 == 1:
                # Check if this closes the dollar quote
                prev_content = "".join(current)
                # Count occurrences of dollar_char in current buffer
                if prev_content.count(dollar_char) % 2 == 1:
                    current.append(content[i:j])
                    i = j
                    in_dollar = False
                    dollar_char = None
                    continue
        elif not in_dollar and c == ';':
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue
        current.append(c)
        i += 1
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
    stmts = parse_statements(content)
    print(f"  Parsed {len(stmts)} statements")
    ok = fail = 0
    for stmt in stmts:
        s, resp = sql(stmt)
        if s:
            ok += 1
        else:
            fail += 1
            if fail <= 3:
                print(f"  FAIL: {stmt[:60]}... -> {resp[:100]}")
    print(f"  Schema: {ok} ok, {fail} failed")

    # Migration 002
    print("[2/2] Applying seed...")
    with open("supabase/migrations/002_seed_data.sql") as f:
        content = f.read()

    stmts = parse_statements(content)
    print(f"  Parsed {len(stmts)} statements")
    ok = fail = 0
    for stmt in stmts:
        s, resp = sql(stmt)
        if s:
            ok += 1
        else:
            fail += 1
            if fail <= 3:
                print(f"  FAIL: {stmt[:60]}... -> {resp[:100]}")
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
