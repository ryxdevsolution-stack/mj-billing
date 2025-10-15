# 🔧 Troubleshooting Guide - RYX Billing Software

## Common Issues and Solutions

### 1. ❌ Circular Import Error
**Error**: `The current Flask app is not registered with this 'SQLAlchemy' instance`

**Solution**: This was fixed by creating `extensions.py`. Always run:
```bash
python run.py
```
**NOT** `python app.py`

**What was fixed**:
- Created `extensions.py` with separate `db` instance
- Updated all imports from `from app import db` to `from extensions import db`
- Added proper `run.py` with application context

---

### 2. ❌ psql command not found
**Error**: `psql: command not found`

**Solution**: Use Supabase Dashboard SQL Editor instead:
1. Go to: https://app.supabase.com/project/habjhxjutlgnjwjbpkvl/sql/new
2. Copy content from migration files
3. Paste and run each migration

**Alternative**: Install PostgreSQL:
```bash
winget install PostgreSQL.PostgreSQL
```

---

### 3. ❌ No tables in database
**Error**: Database is empty when checking

**Solution**: Run all migrations (001-009) in order:
```bash
# From Supabase SQL Editor, run each file:
migration/001_create_client_entry.sql
migration/002_create_users.sql
...through...
migration/009_create_stock_reduction_trigger.sql
```

**Verify**: Run `backend/check_database.py`
```bash
cd backend
python check_database.py
```

---

### 4. ❌ Cannot login - No test user
**Error**: `Invalid credentials` when trying to login

**Solution**: Create test user by running migration 011:
```sql
-- Run this in Supabase SQL Editor
-- Copy content from: migration/011_create_test_client_and_user.sql
```

**Test Credentials**:
- Email: `admin@testcompany.com`
- Password: `password123`

---

### 5. ❌ Frontend cannot connect to backend
**Error**: `Network Error` or `CORS error`

**Solution**:
1. Check backend is running: `python run.py` (should show port 5000)
2. Check frontend .env.local:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```
3. CORS is already configured in `app.py`

---

### 6. ❌ JWT Token expired
**Error**: `Token has expired` or automatic logout

**Solution**: Tokens expire after 24 hours (configured in `config.py`)
- Simply login again
- Token is auto-refreshed on page reload if still valid

---

### 7. ❌ Module not found errors
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install requirements:
```bash
cd backend
pip install -r requirements.txt
```

For frontend:
```bash
cd frontend
npm install
```

---

### 8. ❌ Database connection failed
**Error**: `could not connect to server`

**Solution**: Check `.env` file in backend folder:
```bash
DB_URL=postgresql://postgres:Ryx%402025@db.habjhxjutlgnjwjbpkvl.supabase.co:5432/postgres
SUPABASE_URL=https://habjhxjutlgnjwjbpkvl.supabase.co
SUPABASE_KEY=your-key-here
```

---

### 9. ❌ Port already in use
**Error**: `Address already in use: 5000` or `3000`

**Solution**:

For backend (port 5000):
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or change port in run.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

For frontend (port 3000):
```bash
# Kill process or change port
npm run dev -- -p 3001
```

---

### 10. ❌ Stock not reducing after billing
**Error**: Stock quantity stays the same after creating bill

**Solution**: Check if trigger is created:
```sql
-- Run in Supabase SQL Editor
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- Should show:
-- trigger_reduce_stock_gst_billing
-- trigger_reduce_stock_non_gst_billing
```

If missing, run `migration/009_create_stock_reduction_trigger.sql`

---

## Quick Verification Commands

### Check Database Tables
```bash
cd backend
python check_database.py
```

### Test Backend Health
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"healthy","message":"RYX Billing API is running"}
```

### Test Login API
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@testcompany.com","password":"password123"}'
```

### Check Frontend
```bash
# Open browser to:
http://localhost:3000
# Should see RYX logo animation
```

---

## Still Having Issues?

1. **Check all services are running**:
   - Backend: `python run.py` (port 5000)
   - Frontend: `npm run dev` (port 3000)
   - Database: Supabase (online)

2. **Verify environment variables**:
   - Backend: `backend/.env` exists
   - Frontend: `frontend/.env.local` exists

3. **Check logs**:
   - Backend: Terminal where `python run.py` is running
   - Frontend: Browser console (F12)
   - Database: Supabase Dashboard logs

4. **Review documentation**:
   - [readme.md](readme.md) - Main guide
   - [backend/README.md](backend/README.md) - API docs
   - [frontend/README.md](frontend/README.md) - Frontend docs
   - [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Full status

---

**Last Updated**: 2025-10-15
