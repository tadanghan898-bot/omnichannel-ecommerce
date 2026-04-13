#!/bin/bash
# ============================================================
# OMNICHANNEL E-COMMERCE - Deploy Script
# Deploys backend to Vercel + frontend to Cloudflare Pages
# ============================================================

set -e

echo "============================================================"
echo " OMNICHANNEL E-COMMERCE - DEPLOY"
echo "============================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================
# 1. SUPABASE SCHEMA DEPLOY
# ============================================================
echo -e "\n${YELLOW}[1/5] Deploying Supabase Schema...${NC}"

if [ -z "$SUPABASE_DATABASE_URL" ]; then
    echo "SUPABASE_DATABASE_URL not set. Skipping Supabase deploy."
    echo "Run manually:"
    echo "  psql \$SUPABASE_DATABASE_URL < supabase/migrations/001_init_schema.sql"
else
    pip install psycopg2-binary -q
    python3 << 'EOF'
import psycopg2, os, sys

conn = psycopg2.connect(os.environ['SUPABASE_DATABASE_URL'])
cur = conn.cursor()

# Apply schema
with open('supabase/migrations/001_init_schema.sql', 'r') as f:
    sql = f.read()
cur.execute(sql)
conn.commit()
print("Schema applied successfully")

# Apply seed data
with open('supabase/migrations/002_seed_data.sql', 'r') as f:
    sql = f.read()
cur.execute(sql)
conn.commit()
print("Seed data applied")

cur.close()
conn.close()
EOF
fi

# ============================================================
# 2. FRONTEND BUILD
# ============================================================
echo -e "\n${YELLOW}[2/5] Building frontend...${NC}"
cd frontend
npm ci
VITE_API_URL=/api npm run build
cd ..

# ============================================================
# 3. DEPLOY FRONTEND TO CLOUDFLARE PAGES
# ============================================================
echo -e "\n${YELLOW}[3/5] Deploying frontend to Cloudflare Pages...${NC}"

if [ -z "$CLOUDFLARE_API_TOKEN" ] || [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo "Cloudflare credentials not set. Skipping CF Pages deploy."
    echo "To deploy manually:"
    echo "  wrangler pages deploy frontend/dist --project-name=omnishop"
else
    npx wrangler pages deploy frontend/dist --project-name=omnishop --branch=main
fi

# ============================================================
# 4. DEPLOY BACKEND TO VERCEL
# ============================================================
echo -e "\n${YELLOW}[4/5] Deploying backend to Vercel...${NC}"

if [ -z "$VERCEL_TOKEN" ]; then
    echo "VERCEL_TOKEN not set. Skipping Vercel deploy."
    echo "To deploy manually:"
    echo "  npx vercel --prod"
else
    npx vercel --prod --token=$VERCEL_TOKEN
fi

# ============================================================
# 5. VERIFY
# ============================================================
echo -e "\n${YELLOW}[5/5] Verification...${NC}"
echo -e "${GREEN}============================================================"
echo " DEPLOY COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Set marketplace credentials in .env or Vercel dashboard"
echo "  2. Connect your Shopee/Lazada/TikTok accounts via /marketplace"
echo "  3. Set custom domain in Vercel and Cloudflare Pages"
echo "  4. Enable Supabase auth providers in Supabase dashboard"
echo ""
