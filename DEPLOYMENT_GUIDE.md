# 🚀 QUICK DEPLOYMENT GUIDE

## Upload these files to: https://github.com/atanu0909/attendance4

### Method 1: Using GitHub Web Interface

1. Go to https://github.com/atanu0909/attendance4
2. Click "Add file" → "Upload files"
3. Upload these files:
   - `.github/workflows/device_19_monitor.yml`
   - `device_19_github_monitor.py`
   - `requirements.txt`
   - `README_setup.md`

### Method 2: Using Git Commands

```bash
# Navigate to your project folder
cd attendance_tracker

# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/atanu0909/attendance4.git

# Add files
git add .github/workflows/device_19_monitor.yml
git add device_19_github_monitor.py
git add requirements.txt
git add README_setup.md

# Commit
git commit -m "Add Device 19 Attendance Monitor with GitHub Actions"

# Push to GitHub
git push -u origin main
```

## 🔐 CONFIGURE SECRETS

After uploading files, go to:
https://github.com/atanu0909/attendance4/settings/secrets/actions

Add these 9 secrets:

| Secret Name | Value |
|-------------|-------|
| DB_SERVER | 1.22.45.168,19471 |
| DB_DATABASE | etimetrackliteWEB |
| DB_USERNAME | sa |
| DB_PASSWORD | sa@123 |
| EMAIL_ENABLED | true |
| GMAIL_USER | ghoshatanu32309@gmail.com |
| GMAIL_PASSWORD | oqahvqkuaziufvfb |
| COMPANY_NAME | Stylo Media Pvt Ltd |
| ALERT_EMAIL | aghosh09092004@gmail.com |

## ✅ VERIFICATION

After deployment:
1. Go to "Actions" tab in your repository
2. You should see "Device 19 Attendance Monitor" workflow
3. It will start running automatically every 5 minutes during work hours
4. Manual trigger: Click "Run workflow" to test immediately

## 📧 EXPECTED RESULT

When any of these 8 employees are late on Device 19:
- Codes: 3, 595, 593, 695, 641, 744, 20, 18
- Email alert sent to: aghosh09092004@gmail.com
- Professional HTML email with all details

## 🎯 STATUS

✅ Files created and ready
✅ Email system tested and working
❌ **NEEDS DEPLOYMENT** - Upload to GitHub now!
