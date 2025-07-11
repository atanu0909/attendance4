import pyodbc
import pandas as pd
from datetime import datetime, timedelta, time
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import sys

# Setup logging for GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_19_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database connection parameters from environment variables
DB_SERVER = os.getenv('DB_SERVER', '1.22.45.168,19471')
DB_DATABASE = os.getenv('DB_DATABASE', 'etimetrackliteWEB')
DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sa@123')

# Email configuration
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'True').lower() == 'true'
GMAIL_USER = os.getenv('GMAIL_USER', 'ghoshatanu32309@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'oqahvqkuaziufvfb')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Stylo Media Pvt Ltd')
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'aghosh09092004@gmail.com')  # Email to receive alerts

# Connection string for Ubuntu/Linux
conn_str = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    f'SERVER={DB_SERVER};'
    f'DATABASE={DB_DATABASE};'
    f'UID={DB_USERNAME};'
    f'PWD={DB_PASSWORD};'
    'TrustServerCertificate=yes;'
)

# Employee configuration
EMPLOYEES_TO_MONITOR = [
    {'code': '3', 'name': 'Swarup Mahapatra', 'machine': 'Ryobi 3', 'expected_in': '09:00:00'},
    {'code': '595', 'name': 'Santanu Das', 'machine': 'Ryobi 3', 'expected_in': '07:00:00'},
    {'code': '593', 'name': 'Rohit Kabiraj', 'machine': 'Ryobi 3', 'expected_in': '07:00:00'},
    {'code': '695', 'name': 'Soumen Ghoshal', 'machine': 'Ryobi 2', 'expected_in': '09:00:00'},
    {'code': '641', 'name': 'Souvik Ghosh', 'machine': 'Ryobi 2', 'expected_in': '07:00:00'},
    {'code': '744', 'name': 'Manoj Maity', 'machine': 'Ryobi 2', 'expected_in': '07:00:00'},
    {'code': '20', 'name': 'Bablu Rajak', 'machine': 'Flat Bed', 'expected_in': '07:00:00'},
    {'code': '18', 'name': 'Somen Bhattacharjee', 'machine': 'Flat Bed', 'expected_in': '07:00:00'}
]

def get_db_connection():
    """Get database connection"""
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def load_previous_alerts():
    """Load previous alerts from file to avoid duplicate notifications"""
    try:
        if os.path.exists('alerts_sent.json'):
            with open('alerts_sent.json', 'r') as f:
                data = json.load(f)
                return set(data.get(datetime.now().strftime('%Y-%m-%d'), []))
        return set()
    except Exception as e:
        logger.error(f"Error loading previous alerts: {e}")
        return set()

def save_alert(emp_code):
    """Save alert to file to avoid duplicate notifications"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        alerts = {}
        
        if os.path.exists('alerts_sent.json'):
            with open('alerts_sent.json', 'r') as f:
                alerts = json.load(f)
        
        if today not in alerts:
            alerts[today] = []
        
        if emp_code not in alerts[today]:
            alerts[today].append(emp_code)
        
        with open('alerts_sent.json', 'w') as f:
            json.dump(alerts, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving alert: {e}")

def check_device_19_attendance():
    """Check Device 19 attendance for all employees"""
    today = datetime.now().strftime('%Y-%m-%d')
    current_dt = datetime.now()
    month_year = f"{current_dt.month}_{current_dt.year}"
    
    logger.info(f"Checking Device 19 attendance for {today}")
    
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to connect to database")
        return
    
    try:
        employee_codes = [emp['code'] for emp in EMPLOYEES_TO_MONITOR]
        employee_codes_str = "', '".join(employee_codes)
        
        # Query to get first punch for each employee from device 19
        query = f"""
        WITH FirstPunches AS (
            SELECT 
                CAST(dl.UserId as varchar) as EmployeeCode,
                MIN(dl.LogDate) as FirstPunch,
                e.EmployeeName
            FROM dbo.DeviceLogs_{month_year} dl
            LEFT JOIN dbo.Employees e ON CAST(e.EmployeeCode as varchar) = CAST(dl.UserId as varchar)
            WHERE CAST(dl.LogDate as DATE) = '{today}'
                AND dl.DeviceId = 19
                AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
            GROUP BY CAST(dl.UserId as varchar), e.EmployeeName
        )
        SELECT * FROM FirstPunches
        ORDER BY EmployeeCode
        """
        
        df = pd.read_sql(query, connection)
        
        # Load previous alerts to avoid duplicates
        alerted_today = load_previous_alerts()
        
        attendance_status = []
        
        for emp in EMPLOYEES_TO_MONITOR:
            emp_code = emp['code']
            emp_punch = df[df['EmployeeCode'] == emp_code]
            
            status = {
                'code': emp_code,
                'name': emp['name'],
                'machine': emp['machine'],
                'expected_in': emp['expected_in'],
                'actual_in': None,
                'status': 'No punch',
                'is_late': None,
                'lateness_minutes': 0
            }
            
            if not emp_punch.empty:
                first_punch = emp_punch.iloc[0]['FirstPunch']
                status['actual_in'] = first_punch.strftime('%H:%M:%S')
                
                # Calculate lateness
                expected_time_str = emp['expected_in']
                expected_hour, expected_min, expected_sec = map(int, expected_time_str.split(':'))
                
                expected_datetime = datetime.combine(
                    first_punch.date(),
                    time(expected_hour, expected_min, expected_sec)
                )
                
                lateness_seconds = (first_punch - expected_datetime).total_seconds()
                lateness_minutes = int(lateness_seconds / 60)
                
                status['lateness_minutes'] = lateness_minutes
                
                if lateness_minutes > 0:
                    # Late
                    status['is_late'] = True
                    hours, mins = divmod(lateness_minutes, 60)
                    status['status'] = f"Late by {hours:02d}:{mins:02d}"
                    
                    # Send alert if not already sent today
                    if emp_code not in alerted_today:
                        send_late_alert(status)
                        save_alert(emp_code)
                        alerted_today.add(emp_code)
                    
                else:
                    # On time or early
                    status['is_late'] = False
                    if lateness_minutes < 0:
                        early_minutes = abs(lateness_minutes)
                        hours, mins = divmod(early_minutes, 60)
                        status['status'] = f"Early by {hours:02d}:{mins:02d}"
                    else:
                        status['status'] = "On time"
            
            attendance_status.append(status)
        
        # Log results
        logger.info("="*80)
        logger.info(f"DEVICE 19 ATTENDANCE REPORT - {today}")
        logger.info("="*80)
        
        for status in attendance_status:
            status_icon = "🔴" if status['is_late'] else "🟢" if status['actual_in'] else "🟡"
            logger.info(f"{status_icon} {status['code']:<4} | {status['name']:<25} | {status['status']:<20} | IN: {status['actual_in'] or 'N/A'}")
        
        # Summary
        total_employees = len(attendance_status)
        punched_employees = sum(1 for s in attendance_status if s['actual_in'])
        late_employees = sum(1 for s in attendance_status if s['is_late'])
        
        logger.info("="*80)
        logger.info(f"SUMMARY: {punched_employees}/{total_employees} punched in, {late_employees} late")
        logger.info("="*80)
        
        # Generate daily report
        generate_daily_report(attendance_status)
        
    except Exception as e:
        logger.error(f"Error checking attendance: {e}")
        raise
    finally:
        connection.close()

def send_late_alert(status):
    """Send email alert for late employee"""
    if not EMAIL_ENABLED:
        logger.info(f"Email disabled - Would send alert for {status['name']}")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL  # Send to your specified email
        msg['Subject'] = f"🚨 DEVICE 19 LATE ALERT - {status['name']} is Late!"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="border: 2px solid #ff4444; padding: 20px; border-radius: 10px; background-color: #fff5f5;">
            <h2 style="color: #ff4444; margin-top: 0;">🚨 URGENT: Employee Late Alert</h2>
            
            <div style="background-color: #ffffff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="color: #333; margin-top: 0;">Company Information</h3>
                <p><strong>Company:</strong> {COMPANY_NAME}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                <p><strong>Alert Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                <p><strong>Device:</strong> Device 19</p>
            </div>
            
            <div style="background-color: #fff0f0; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ff4444;">
                <h3 style="color: #ff4444; margin-top: 0;">Employee Details</h3>
                <p><strong>Employee Code:</strong> {status['code']}</p>
                <p><strong>Employee Name:</strong> {status['name']}</p>
                <p><strong>Machine Assignment:</strong> {status['machine']}</p>
                <p><strong>Expected IN Time:</strong> {status['expected_in']}</p>
                <p><strong>Actual IN Time:</strong> {status['actual_in']}</p>
                <p><strong>Status:</strong> <span style="color: #ff4444; font-weight: bold; font-size: 16px;">{status['status']}</span></p>
            </div>
            
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="color: #0066cc; margin-top: 0;">Action Required</h3>
                <p>Please take appropriate action regarding this late arrival:</p>
                <ul>
                    <li>Contact the employee if necessary</li>
                    <li>Update attendance records</li>
                    <li>Review if this is a recurring issue</li>
                </ul>
            </div>
            
            <hr style="margin: 20px 0; border: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px; margin-bottom: 0;">
                <em>This alert was generated automatically by the Device 19 Attendance Monitor running on GitHub Actions.</em><br>
                <em>Repository: https://github.com/atanu0909/attendance4</em><br>
                <em>Alert sent to: {ALERT_EMAIL}</em>
            </p>
        </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"📧 Late alert sent for {status['name']} (Code: {status['code']})")
        
    except Exception as e:
        logger.error(f"Error sending email alert: {e}")

def generate_daily_report(attendance_status):
    """Generate daily report file"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        report_filename = f"device_19_report_{today}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(f"DEVICE 19 ATTENDANCE REPORT - {today}\n")
            f.write("="*60 + "\n\n")
            
            for status in attendance_status:
                f.write(f"Code: {status['code']:<4} | Name: {status['name']:<25}\n")
                f.write(f"Machine: {status['machine']:<15} | Expected: {status['expected_in']}\n")
                f.write(f"Actual IN: {status['actual_in'] or 'Not punched':<10} | Status: {status['status']}\n")
                f.write("-" * 60 + "\n")
            
            # Summary
            total = len(attendance_status)
            punched = sum(1 for s in attendance_status if s['actual_in'])
            late = sum(1 for s in attendance_status if s['is_late'])
            
            f.write(f"\nSUMMARY:\n")
            f.write(f"Total employees monitored: {total}\n")
            f.write(f"Employees punched in: {punched}\n")
            f.write(f"Late employees: {late}\n")
            f.write(f"On-time/Early employees: {punched - late}\n")
            f.write(f"Not punched in: {total - punched}\n")
        
        logger.info(f"📋 Daily report generated: {report_filename}")
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")

def main():
    """Main function for GitHub Actions"""
    try:
        logger.info("🚀 Starting Device 19 Attendance Monitor (GitHub Actions)")
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"👥 Monitoring {len(EMPLOYEES_TO_MONITOR)} employees")
        
        check_device_19_attendance()
        
        logger.info("✅ Monitoring completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
