#!/bin/bash

# Device 19 Attendance Monitor - GitHub Deployment Script
# Repository: https://github.com/atanu0909/attendance4

echo "🚀 Device 19 Attendance Monitor - GitHub Deployment"
echo "=================================================="
echo "Repository: https://github.com/atanu0909/attendance4"
echo "Alert Email: aghosh09092004@gmail.com"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git remote add origin https://github.com/atanu0909/attendance4.git
fi

# Add all files
echo "📄 Adding files to Git..."
git add .github/workflows/device_19_monitor.yml
git add device_19_github_monitor.py
git add requirements.txt
git add README_setup.md
git add test_email.py

# Commit changes
echo "💾 Committing changes..."
git commit -m "Add Device 19 Attendance Monitor with GitHub Actions

- 24/7 monitoring every 5 minutes during work hours
- Email alerts to aghosh09092004@gmail.com for late employees
- Monitors 8 employees on Device 19
- Automated GitHub Actions workflow
- Professional HTML email alerts
- Daily attendance reports"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/atanu0909/attendance4"
echo "2. Click Settings → Secrets and variables → Actions"
echo "3. Add the required secrets (see README_setup.md)"
echo "4. The monitoring will start automatically!"
echo ""
echo "Required secrets to add:"
echo "- DB_SERVER: 1.22.45.168,19471"
echo "- DB_DATABASE: etimetrackliteWEB"
echo "- DB_USERNAME: sa"
echo "- DB_PASSWORD: sa@123"
echo "- EMAIL_ENABLED: true"
echo "- GMAIL_USER: ghoshatanu32309@gmail.com"
echo "- GMAIL_PASSWORD: oqahvqkuaziufvfb"
echo "- COMPANY_NAME: Stylo Media Pvt Ltd"
echo "- ALERT_EMAIL: aghosh09092004@gmail.com"
echo ""
echo "🎯 Your Device 19 monitoring system is ready!"
