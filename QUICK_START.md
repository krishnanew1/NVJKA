# 🚀 Quick Start - Upload to GitHub

## ⚠️ CRITICAL: Do This First!

Your project has **PASSWORDS** in the code that will be public on GitHub!

**Location**: `backend/config/settings.py`
- Line 24: SECRET_KEY
- Line 102: Database PASSWORD = 'Krishna@2210'

---

## 🎯 3 Simple Steps

### Step 1: Clean Up (2 minutes)
```cmd
cd backend
rmdir /s /q apps\portal
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
```

### Step 2: Hide Passwords (3 minutes)

Open `backend/config/settings.py` and change:

**Line 24:**
```python
SECRET_KEY = 'your-secret-key-here-change-in-production'
```

**Line 102:**
```python
'PASSWORD': 'your-database-password',
```

### Step 3: Upload to GitHub (5 minutes)
```cmd
cd C:\NVJKA\NVJKA\NVJKA
git init
git add .
git commit -m "Initial commit: Academic ERP Backend"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## ✅ That's It!

Your project is now on GitHub without exposing your passwords.

**For detailed instructions**, see: `GITHUB_UPLOAD_CHECKLIST.md`

---

## 📝 What Gets Uploaded

✅ All your code  
✅ Documentation  
✅ Tests  
✅ Configuration templates  

❌ Passwords (you changed them!)  
❌ Cache files (cleaned up!)  
❌ Database files (.gitignore handles this)  

---

## 🆘 Quick Help

**Problem**: Git says "fatal: not a git repository"  
**Solution**: Run `git init` first

**Problem**: Can't delete portal folder  
**Solution**: Close any editors/terminals using those files

**Problem**: Worried about security  
**Solution**: Follow Step 2 carefully - replace actual passwords with placeholders

---

**Total Time**: ~10 minutes  
**Difficulty**: Easy  
**Result**: Professional GitHub repository ready to share!
