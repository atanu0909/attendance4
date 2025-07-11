# Device 19 Attendance Monitoring with GitHub Actions

This project provides 24/7 real-time monitoring of employee attendance on Device 19 using GitHub Actions. It automatically checks for late arrivals and sends email alerts.

## Features

- **24/7 Monitoring**: Runs every 5 minutes during work hours (6 AM - 11 PM IST)
- **Real-time Alerts**: Email notifications for late employees
- **Daily Reports**: Generates comprehensive attendance reports
- **Duplicate Prevention**: Avoids sending multiple alerts for the same employee
- **Cloud-based**: Completely runs in GitHub Actions, no local infrastructure needed

## Setup Instructions

### 1. Repository Setup

1. Fork or clone this repository
2. Ensure all files are in the correct structure:
   ```
   attendance_tracker/
   ├── .github/
   │   └── workflows/
   │       └── device_19_monitor.yml
   ├── device_19_github_monitor.py
   ├── requirements.txt
   └── README_github_actions.md
   ```

### 2. GitHub Secrets Configuration

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DB_SERVER` | Database server address | `1.22.45.168,19471` |
| `DB_DATABASE` | Database name | `etimetrackliteWEB` |
| `DB_USERNAME` | Database username | `sa` |
| `DB_PASSWORD` | Database password | `your_password` |
| `EMAIL_ENABLED` | Enable email alerts | `true` |
| `GMAIL_USER` | Gmail username for alerts | `your_email@gmail.com` |
| `GMAIL_PASSWORD` | Gmail app password | `your_app_password` |
| `COMPANY_NAME` | Company name for emails | `Stylo Media Pvt Ltd` |

### 3. Gmail Setup for Email Alerts

1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" for this application:
   - Go to Google Account Settings → Security → App passwords
   - Generate a new app password
   - Use this password in the `GMAIL_PASSWORD` secret

### 4. Employee Configuration

The system monitors these employees on Device 19:

| Code | Name | Machine | Expected IN Time |
|------|------|---------|------------------|
| 3 | Swarup Mahapatra | Ryobi 3 | 09:00:00 |
| 595 | Santanu Das | Ryobi 3 | 07:00:00 |
| 593 | Rohit Kabiraj | Ryobi 3 | 07:00:00 |
| 695 | Soumen Ghoshal | Ryobi 2 | 09:00:00 |
| 641 | Souvik Ghosh | Ryobi 2 | 07:00:00 |
| 744 | Manoj Maity | Ryobi 2 | 07:00:00 |
| 20 | Bablu Rajak | Flat Bed | 07:00:00 |
| 18 | Somen Bhattacharjee | Flat Bed | 07:00:00 |

To modify employee settings, edit the `EMPLOYEES_TO_MONITOR` list in `device_19_github_monitor.py`.

## How It Works

### Schedule
- **Automatic**: Runs every 5 minutes during work hours (Monday-Friday, 6 AM - 11 PM IST)
- **Manual**: Can be triggered manually from the Actions tab

### Monitoring Process
1. Connects to the SQL Server database
2. Queries Device 19 logs for the current day
3. Identifies first punch time for each employee
4. Compares with expected IN time
5. Sends email alerts for late employees (once per day)
6. Generates daily attendance reports

### Outputs
- **Logs**: Available in GitHub Actions run details
- **Reports**: Daily attendance reports uploaded as artifacts
- **Alerts**: Email notifications for late arrivals

## Monitoring Dashboard

To view the monitoring status:

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Click on "Device 19 Attendance Monitor"
4. View the latest runs and logs

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DB_SERVER`, `DB_USERNAME`, `DB_PASSWORD` secrets
   - Ensure database server allows connections from GitHub Actions IPs

2. **Email Alerts Not Sending**
   - Verify `GMAIL_USER` and `GMAIL_PASSWORD` secrets
   - Ensure Gmail app password is correctly generated
   - Check if `EMAIL_ENABLED` is set to `true`

3. **No Data Found**
   - Verify the DeviceLogs table exists for current month
   - Check if employees are actually punching on Device 19
   - Ensure employee codes are correct

### Viewing Logs

- Go to Actions → Latest run → Click on "monitor-attendance" job
- Expand "Run Device 19 Attendance Monitor" step
- View detailed logs and error messages

### Manual Testing

To test the system manually:
1. Go to Actions tab
2. Click "Device 19 Attendance Monitor"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Customization

### Modify Schedule
Edit `.github/workflows/device_19_monitor.yml`:
```yaml
schedule:
  - cron: '*/5 0-17 * * 1-5'  # Every 5 minutes, 6 AM - 11 PM IST
```

### Change Employee List
Edit `device_19_github_monitor.py`:
```python
EMPLOYEES_TO_MONITOR = [
    {'code': '123', 'name': 'New Employee', 'machine': 'Machine X', 'expected_in': '08:00:00'},
    # Add more employees...
]
```

### Modify Email Template
Edit the `send_late_alert()` function in `device_19_github_monitor.py`.

## Cost Considerations

- GitHub Actions provides 2,000 minutes/month free for public repositories
- Each monitoring run takes ~2-3 minutes
- Running every 5 minutes during work hours ≈ 2,880 minutes/month
- Consider using a paid GitHub plan or reducing frequency for heavy usage

## Security Notes

- Never commit database credentials to the repository
- Use GitHub Secrets for all sensitive information
- Regularly rotate database passwords and email app passwords
- Monitor GitHub Actions usage to detect unusual activity

## Support

For issues or questions:
1. Check the GitHub Actions logs for detailed error messages
2. Review the troubleshooting section above
3. Verify all secrets are correctly configured
4. Test database connectivity separately if needed
