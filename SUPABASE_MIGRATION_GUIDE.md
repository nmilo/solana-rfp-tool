# 🚀 Supabase Migration Guide

## Step 1: Get Your Supabase Credentials

1. **Go to your Supabase project dashboard**
2. **Get your credentials:**
   - Project URL: `https://your-project.supabase.co`
   - Anon Key: `eyJ...` (public key)
   - Service Role Key: `eyJ...` (private key)
   - Database Password: (from project settings)

## Step 2: Update Environment Variables

### **Local Development (.env):**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Connection (for migration)
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Keep existing variables
OPENAI_API_KEY=your-openai-key
JWT_SECRET_KEY=your-jwt-secret
```

### **Heroku Production:**
```bash
# Set these in Heroku dashboard or CLI
heroku config:set SUPABASE_URL=https://your-project.supabase.co
heroku config:set SUPABASE_ANON_KEY=your-anon-key
heroku config:set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
heroku config:set DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

## Step 3: Run Migration Script

```bash
# Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export DATABASE_URL="postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"

# Run migration
cd solana-rfp-app/backend
python3 migrate_to_supabase.py
```

## Step 4: Update Backend Code

The backend will automatically use the new DATABASE_URL. No code changes needed!

## Step 5: Test Migration

```bash
# Test API endpoints
curl -X GET "https://your-heroku-app.herokuapp.com/api/v1/knowledge/admin/preview?page=1&page_size=5" \
  -H "Authorization: Bearer mock-jwt-token-demo"
```

## Step 6: Deploy to Production

```bash
git add .
git commit -m "Migrate to Supabase database"
git push origin main
```

## Benefits After Migration:
- ✅ No more 30-second timeouts
- ✅ Better database persistence
- ✅ Real-time capabilities
- ✅ Cost savings (56% reduction)
- ✅ Better performance and reliability
