# Railway Deployment Guide for Device 19 Attendance Monitor

## 🚀 Quick Deploy to Railway

### Step 1: Prepare Repository
1. All files are ready in your repository
2. Push the changes to GitHub

### Step 2: Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Sign in with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `attendance4` repository
6. Click "Deploy"

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```
DB_SERVER=1.22.45.168,19471
DB_DATABASE=etimetrackliteWEB
DB_USERNAME=sa
DB_PASSWORD=sa@123
EMAIL_ENABLED=True
GMAIL_USER=ghoshatanu32309@gmail.com
GMAIL_PASSWORD=oqahvqkuaziufvfb
COMPANY_NAME=Stylo Media Pvt Ltd
ALERT_EMAIL=aghosh09092004@gmail.com
```

### Step 4: Verify Deployment
1. Check the deployment logs in Railway dashboard
2. Ensure the app is running
3. Monitor the logs for attendance checks

## 📋 What's Included

### Railway-Optimized Files:
- `railway_monitor.py` - Main monitoring script for Railway
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `railway.json` - Railway configuration
- `runtime.txt` - Python version specification

### Features:
- ✅ **24/7 Monitoring**: Continuous monitoring with 5-minute intervals
- ✅ **Work Hours Only**: Runs only during 6 AM - 11 PM IST
- ✅ **Email Alerts**: Sends alerts to aghosh09092004@gmail.com
- ✅ **Database Fallback**: Multiple connection methods (ODBC + pymssql)
- ✅ **Error Recovery**: Automatic retry on failures
- ✅ **Cloud Optimized**: Designed for Railway's infrastructure

### Monitoring Schedule:
- **Check Interval**: Every 5 minutes
- **Active Hours**: 6 AM to 11 PM IST (Monday-Friday)
- **Employees**: 8 employees on Device 19
- **Alerts**: Email notifications for late arrivals

## 🔧 Technical Details

### Database Connectivity:
- Primary: ODBC drivers with SSL disabled
- Fallback: pymssql for direct connection
- Handles Railway's Ubuntu environment

### Email System:
- SMTP: Gmail with app password
- Recipient: aghosh09092004@gmail.com
- Content: Late employee details with timestamps

### Error Handling:
- Graceful connection failures
- Automatic retry mechanisms
- Comprehensive logging

## 🎯 Benefits of Railway vs GitHub Actions

### Railway Advantages:
- ✅ **Always On**: Continuous running process
- ✅ **Better Database Support**: Native database connectivity
- ✅ **Real-time Monitoring**: Live logs and metrics
- ✅ **Automatic Restarts**: Service recovery on failures
- ✅ **Environment Management**: Easy variable configuration

### Cost:
- **Free Tier**: 500 hours/month (enough for 24/7 monitoring)
- **Paid Plans**: Available if needed for scaling

## 📊 Expected Results

Once deployed, you'll have:
- ✅ **24/7 automated attendance monitoring**
- ✅ **Real-time email alerts for late employees**
- ✅ **Reliable database connectivity**
- ✅ **Comprehensive logging and monitoring**
- ✅ **Automatic error recovery**

The system will monitor Device 19 attendance every 5 minutes and send immediate email alerts when employees are late!
