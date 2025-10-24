# 🔧 FIX NETWORK ERROR - Connect Vercel to Supabase

## ❌ PROBLEM:
- Vercel frontend shows "Network Error"
- Heroku backend is returning 503 (Service Unavailable)
- Backend needs Supabase DATABASE_URL

## ✅ SOLUTION - UPDATE HEROKU ENVIRONMENT VARIABLES:

### **Step 1: Login to Heroku**
```bash
heroku login
```

### **Step 2: Find Your App Name**
```bash
heroku apps
```

### **Step 3: Update Environment Variables**
Replace `YOUR-APP-NAME` with your actual Heroku app name:

```bash
# Set Supabase DATABASE_URL (Connection Pooler for better performance)
heroku config:set DATABASE_URL="postgresql://postgres.zaqonwxzoafewoloexsk:MandaSolana123!@aws-0-us-west-1.pooler.supabase.com:6543/postgres" -a YOUR-APP-NAME

# Or use direct connection:
heroku config:set DATABASE_URL="postgresql://postgres:MandaSolana123!@db.zaqonwxzoafewoloexsk.supabase.co:5432/postgres" -a YOUR-APP-NAME

# Set OpenAI API Key
heroku config:set OPENAI_API_KEY="YOUR-OPENAI-API-KEY-HERE" -a YOUR-APP-NAME

# Set Supabase URL
heroku config:set SUPABASE_URL="https://zaqonwxzoafewoloexsk.supabase.co" -a YOUR-APP-NAME

# Set Supabase Anon Key
heroku config:set SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDExODUsImV4cCI6MjA3Njg3NzE4NX0.fKR28ijcpk0XfD1hbEdv9rqPmrnmrIf6S8t0JuuZoeA" -a YOUR-APP-NAME

# Set Supabase Service Role Key
heroku config:set SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTE4NSwiZXhwIjoyMDc2ODc3MTg1fQ.hGygXYHIqt8ipZR2Kytzj-xGxGHhBuN2fZp86ytaVgk" -a YOUR-APP-NAME
```

### **Step 4: Restart Heroku App**
```bash
heroku restart -a YOUR-APP-NAME
```

### **Step 5: Check Logs**
```bash
heroku logs --tail -a YOUR-APP-NAME
```

### **Step 6: Test Backend**
```bash
curl https://YOUR-APP-NAME.herokuapp.com/health
```

## 🚀 ALTERNATIVE: Deploy to Railway (RECOMMENDED)

Railway is better than Heroku for this use case:

### **Why Railway?**
- ✅ No 30-second timeout
- ✅ Better PostgreSQL support  
- ✅ Free tier more generous
- ✅ Easier configuration
- ✅ Better performance

### **Deploy to Railway:**

1. **Go to**: https://railway.app
2. **Connect GitHub**: Link your repo
3. **Add PostgreSQL**: Railway provides managed Postgres
4. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=sk-proj-gM17...
   DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-populated
   SUPABASE_URL=https://zaqonwxzoafewoloexsk.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOi...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
   ```
5. **Deploy**: Automatic!

## 🔍 DEBUGGING STEPS:

### **Check if Backend is Running:**
```bash
curl https://solana-rfp-271974794838.herokuapp.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### **Check if Database is Accessible:**
```bash
curl -X GET "https://solana-rfp-271974794838.herokuapp.com/api/v1/knowledge/stats" \
  -H "Authorization: Bearer mock-jwt-token-demo"
```

Expected response:
```json
{"total_entries": 28, ...}
```

### **Test Question Processing:**
```bash
curl -X POST "https://solana-rfp-271974794838.herokuapp.com/api/v1/questions/process-text" \
  -H "Authorization: Bearer mock-jwt-token-demo" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is Solana?"}'
```

## 📝 MANUAL CONFIGURATION (Heroku Dashboard):

1. Go to: https://dashboard.heroku.com/apps
2. Click on your app
3. Go to "Settings" tab
4. Click "Reveal Config Vars"
5. Add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://postgres:MandaSolana123!@db.zaqonwxzoafewoloexsk.supabase.co:5432/postgres` |
| `OPENAI_API_KEY` | `YOUR-OPENAI-API-KEY-HERE` |
| `SUPABASE_URL` | `https://zaqonwxzoafewoloexsk.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDExODUsImV4cCI6MjA3Njg3NzE4NX0.fKR28ijcpk0XfD1hbEdv9rqPmrnmrIf6S8t0JuuZoeA` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTE4NSwiZXhwIjoyMDc2ODc3MTg1fQ.hGygXYHIqt8ipZR2Kytzj-xGxGHhBuN2fZp86ytaVgk` |

6. Restart the app (More → Restart all dynos)

## ✅ VERIFICATION:

After updating, test these URLs:

1. **Health Check**: https://YOUR-APP.herokuapp.com/health
2. **API Docs**: https://YOUR-APP.herokuapp.com/docs
3. **Knowledge Base**: https://YOUR-APP.herokuapp.com/api/v1/knowledge/stats

All should work!

## 🎯 QUICK FIX (If Heroku is Down):

The backend might be sleeping or crashed. You can:

1. **Restart it manually** via Heroku dashboard
2. **Check logs** for errors: `heroku logs --tail -a YOUR-APP`
3. **Redeploy**: `git push heroku main`

The data is safe in Supabase - just need to connect the backend!
