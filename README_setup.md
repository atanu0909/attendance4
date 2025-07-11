# 🚨 Device 19 Attendance Monitor Setup Guide

## Repository: https://github.com/atanu0909/attendance4

This guide will help you set up 24/7 automated monitoring for Device 19 attendance with email alerts sent to **aghosh09092004@gmail.com** when employees are late.

---

## 📋 Step 1: Upload Files to GitHub

Upload these files to your repository `https://github.com/atanu0909/attendance4`:

```
attendance4/
├── .github/
│   └── workflows/
│       └── device_19_monitor.yml
├── device_19_github_monitor.py
├── requirements.txt
├── README_setup.md
└── (other existing files)
```

---

## 🔐 Step 2: Configure GitHub Secrets

Go to your GitHub repository: `https://github.com/atanu0909/attendance4`

1. Click **Settings** (top menu)
2. Click **Secrets and variables** → **Actions** (left sidebar)
3. Click **New repository secret**
4. Add each secret below:

### Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DB_SERVER` | `1.22.45.168,19471` | Database server address |
| `DB_DATABASE` | `etimetrackliteWEB` | Database name |
| `DB_USERNAME` | `sa` | Database username |
| `DB_PASSWORD` | `sa@123` | Database password |
| `EMAIL_ENABLED` | `true` | Enable email alerts |
| `GMAIL_USER` | `ghoshatanu32309@gmail.com` | Gmail account for sending emails |
| `GMAIL_PASSWORD` | `oqahvqkuaziufvfb` | Gmail app password |
| `COMPANY_NAME` | `Stylo Media Pvt Ltd` | Company name for emails |
| `ALERT_EMAIL` | `aghosh09092004@gmail.com` | **YOUR EMAIL** - where alerts will be sent |

---

## 📧 Step 3: Gmail Configuration

The system will use `ghoshatanu32309@gmail.com` to send emails to `aghosh09092004@gmail.com`.

### Verify Gmail App Password:
1. Go to [Google Account Settings](https://myaccount.google.com)
2. Click **Security** → **App passwords**
3. Verify the app password: `oqahvqkuaziufvfb`
4. If it doesn't work, generate a new app password

---

## 👥 Step 4: Monitored Employees

The system monitors these 8 employees on Device 19:

| Code | Name | Machine | Expected IN Time |
|------|------|---------|------------------|
| **3** | Swarup Mahapatra | Ryobi 3 | 09:00:00 |
| **595** | Santanu Das | Ryobi 3 | 07:00:00 |
| **593** | Rohit Kabiraj | Ryobi 3 | 07:00:00 |
| **695** | Soumen Ghoshal | Ryobi 2 | 09:00:00 |
| **641** | Souvik Ghosh | Ryobi 2 | 07:00:00 |
| **744** | Manoj Maity | Ryobi 2 | 07:00:00 |
| **20** | Bablu Rajak | Flat Bed | 07:00:00 |
| **18** | Somen Bhattacharjee | Flat Bed | 07:00:00 |

---

## ⚡ Step 5: Activate GitHub Actions

1. Go to your repository: `https://github.com/atanu0909/attendance4`
2. Click **Actions** tab
3. If prompted, click **Enable GitHub Actions**
4. The workflow will automatically start running

---

## 📅 Step 6: Monitoring Schedule

The system will run:
- **Automatically**: Every 5 minutes during work hours (6 AM - 11 PM IST)
- **Days**: Monday to Friday
- **Manual**: You can trigger it manually from Actions tab

---

## 🔔 Step 7: Email Alert System

### When You'll Get Alerts:
- Any of the 8 employees arrives late on Device 19
- One email per employee per day (no spam)
- Rich HTML email with all details

### Email Format:
```
Subject: 🚨 DEVICE 19 LATE ALERT - [Employee Name] is Late!

Content:
- Company information
- Employee details (code, name, machine)
- Expected vs actual IN time
- How late they are
- Action required suggestions
```

---

## 📊 Step 8: Monitor System Status

### View Logs:
1. Go to `https://github.com/atanu0909/attendance4`
2. Click **Actions** tab
3. Click on latest **Device 19 Attendance Monitor** run
4. Click **monitor-attendance** job
5. Expand **Run Device 19 Attendance Monitor** to see logs

### Sample Log Output:
```
🚀 Starting Device 19 Attendance Monitor (GitHub Actions)
📅 Date: 2025-07-11
⏰ Time: 07:15:00
👥 Monitoring 8 employees

================================================================================
DEVICE 19 ATTENDANCE REPORT - 2025-07-11
================================================================================
🟢 18   | Somen Bhattacharjee       | On time              | IN: 07:03:14
🟢 20   | Bablu Rajak               | Early by 00:02       | IN: 07:02:23
🔴 3    | Swarup Mahapatra          | Late by 00:44        | IN: 09:44:24
🟢 593  | Rohit Kabiraj             | Early by 00:01       | IN: 07:01:11
📧 Late alert sent for Swarup Mahapatra (Code: 3)
================================================================================
```

---

## 🧪 Step 9: Test the System

### Manual Test:
1. Go to Actions tab
2. Click **Device 19 Attendance Monitor**
3. Click **Run workflow** button
4. Select **main** branch
5. Click **Run workflow**
6. Watch the execution and logs

### Check Email:
- Check `aghosh09092004@gmail.com` for test alerts
- Check spam folder if needed

---

## 🛠️ Step 10: Troubleshooting

### Common Issues:

1. **No emails received:**
   - Check Gmail app password is correct
   - Verify `ALERT_EMAIL` secret is set to `aghosh09092004@gmail.com`
   - Check spam folder

2. **Database connection failed:**
   - Verify database server is accessible from internet
   - Check database credentials

3. **No attendance data:**
   - Verify employees are punching on Device 19
   - Check if DeviceLogs table exists for current month

### Debug Steps:
1. Check Actions logs for error messages
2. Verify all secrets are set correctly
3. Test database connection separately
4. Check if the workflow file is in correct path

---

## 📈 Step 11: Expected Results

### Daily Operations:
- System runs every 5 minutes during work hours
- Checks Device 19 for new punches
- Compares with expected IN times
- Sends alerts for late employees to `aghosh09092004@gmail.com`
- Generates daily reports

### Success Indicators:
- ✅ GitHub Actions runs successfully
- ✅ Database connection works
- ✅ Email alerts sent for late employees
- ✅ Daily reports generated
- ✅ No duplicate alerts

---

## 🎯 Final Checklist

Before going live, verify:

- [ ] All files uploaded to GitHub repository
- [ ] All 9 secrets configured correctly
- [ ] Gmail app password works
- [ ] `ALERT_EMAIL` set to `aghosh09092004@gmail.com`
- [ ] Test run executed successfully
- [ ] Received test email
- [ ] Database connectivity confirmed

---

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs first
2. Verify all secrets are correctly set
3. Test email functionality separately
4. Check database connectivity

The system is designed to be robust and will automatically retry on failures.

---

**Repository:** https://github.com/atanu0909/attendance4  
**Alert Email:** aghosh09092004@gmail.com  
**Monitoring:** Device 19 - 8 employees  
**Schedule:** Every 5 minutes during work hours  
**Status:** Ready for deployment! 🚀
