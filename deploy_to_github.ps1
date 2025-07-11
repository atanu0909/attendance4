# Device 19 Attendance Monitor - PowerShell Deployment Script
# Repository: https://github.com/atanu0909/attendance4

Write-Host "🚀 Device 19 Attendance Monitor - GitHub Deployment" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Repository: https://github.com/atanu0909/attendance4" -ForegroundColor Cyan
Write-Host "Alert Email: aghosh09092004@gmail.com" -ForegroundColor Cyan
Write-Host ""

# Check if git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/atanu0909/attendance4.git
}

# Check if files exist
$requiredFiles = @(
    ".github/workflows/device_19_monitor.yml",
    "device_19_github_monitor.py",
    "requirements.txt",
    "README_setup.md"
)

Write-Host "📄 Checking required files..." -ForegroundColor Yellow
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
    }
}

# Add all files
Write-Host "📄 Adding files to Git..." -ForegroundColor Yellow
git add .github/workflows/device_19_monitor.yml
git add device_19_github_monitor.py
git add requirements.txt
git add README_setup.md
git add DEPLOYMENT_GUIDE.md

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Add Device 19 Attendance Monitor with GitHub Actions

- 24/7 monitoring every 5 minutes during work hours
- Email alerts to aghosh09092004@gmail.com for late employees
- Monitors 8 employees on Device 19 (codes: 3,595,593,695,641,744,20,18)
- Automated GitHub Actions workflow
- Professional HTML email alerts
- Daily attendance reports"

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/atanu0909/attendance4" -ForegroundColor White
Write-Host "2. Click Settings → Secrets and variables → Actions" -ForegroundColor White
Write-Host "3. Add the required secrets (see README_setup.md)" -ForegroundColor White
Write-Host "4. The monitoring will start automatically!" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Required secrets to add:" -ForegroundColor Cyan
Write-Host "- DB_SERVER: 1.22.45.168,19471" -ForegroundColor White
Write-Host "- DB_DATABASE: etimetrackliteWEB" -ForegroundColor White
Write-Host "- DB_USERNAME: sa" -ForegroundColor White
Write-Host "- DB_PASSWORD: sa@123" -ForegroundColor White
Write-Host "- EMAIL_ENABLED: true" -ForegroundColor White
Write-Host "- GMAIL_USER: ghoshatanu32309@gmail.com" -ForegroundColor White
Write-Host "- GMAIL_PASSWORD: oqahvqkuaziufvfb" -ForegroundColor White
Write-Host "- COMPANY_NAME: Stylo Media Pvt Ltd" -ForegroundColor White
Write-Host "- ALERT_EMAIL: aghosh09092004@gmail.com" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Your Device 19 monitoring system is ready!" -ForegroundColor Green
