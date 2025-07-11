import pyodbc
import pandas as pd
from datetime import datetime, timedelta, time
import os
import time as time_module
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_19_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database connection parameters
server = '1.22.45.168,19471'
database = 'etimetrackliteWEB'
username = 'sa'
password = 'sa@123'

conn_str = (
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

# Email configuration (optional - set to False to disable)
EMAIL_ENABLED = True
GMAIL_USER = 'ghoshatanu32309@gmail.com'
GMAIL_PASSWORD = 'oqahvqkuaziufvfb'
COMPANY_NAME = 'Stylo Media Pvt Ltd'

# Employee configuration with expected IN times
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

# Global variables to track daily state
daily_status = {}
alerted_employees = set()
current_monitoring_date = None

def get_db_connection():
    """Get database connection"""
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def reset_daily_tracking():
    """Reset tracking for new day"""
    global daily_status, alerted_employees, current_monitoring_date
    
    new_date = datetime.now().strftime('%Y-%m-%d')
    if current_monitoring_date != new_date:
        logger.info(f"Starting new day monitoring: {new_date}")
        daily_status = {}
        alerted_employees = set()
        current_monitoring_date = new_date
        
        # Initialize daily status for all employees
        for emp in EMPLOYEES_TO_MONITOR:
            daily_status[emp['code']] = {
                'name': emp['name'],
                'machine': emp['machine'],
                'expected_in': emp['expected_in'],
                'first_punch': None,
                'first_punch_time': None,
                'has_punched': False,
                'is_late': None,
                'lateness_minutes': 0,
                'status': 'Waiting for punch'
            }

def check_device_19_punches():
    """Check for new punches on device 19"""
    today = datetime.now().strftime('%Y-%m-%d')
    current_dt = datetime.now()
    month_year = f"{current_dt.month}_{current_dt.year}"
    
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to connect to database")
        return False
    
    try:
        employee_codes = [emp['code'] for emp in EMPLOYEES_TO_MONITOR]
        employee_codes_str = "', '".join(employee_codes)
        
        # Query to get all punch records from device 19 for today
        query = f"""
        SELECT 
            CAST(dl.UserId as varchar) as EmployeeCode,
            dl.LogDate,
            dl.DeviceId,
            e.EmployeeName
        FROM dbo.DeviceLogs_{month_year} dl
        LEFT JOIN dbo.Employees e ON CAST(e.EmployeeCode as varchar) = CAST(dl.UserId as varchar)
        WHERE CAST(dl.LogDate as DATE) = '{today}'
            AND dl.DeviceId = 19
            AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
        ORDER BY CAST(dl.UserId as varchar), dl.LogDate
        """
        
        df = pd.read_sql(query, connection)
        
        if not df.empty:
            # Process each employee's punches
            for emp_code in employee_codes:
                emp_punches = df[df['EmployeeCode'] == emp_code]
                
                if not emp_punches.empty and not daily_status[emp_code]['has_punched']:
                    # Get first punch for this employee
                    first_punch = emp_punches['LogDate'].min()
                    
                    # Update daily status
                    daily_status[emp_code]['first_punch'] = first_punch
                    daily_status[emp_code]['first_punch_time'] = first_punch.strftime('%H:%M:%S')
                    daily_status[emp_code]['has_punched'] = True
                    
                    # Calculate lateness
                    expected_time_str = daily_status[emp_code]['expected_in']
                    expected_hour, expected_min, expected_sec = map(int, expected_time_str.split(':'))
                    
                    # Create expected datetime for today
                    expected_datetime = datetime.combine(
                        first_punch.date(),
                        time(expected_hour, expected_min, expected_sec)
                    )
                    
                    # Calculate lateness in minutes
                    lateness_seconds = (first_punch - expected_datetime).total_seconds()
                    lateness_minutes = int(lateness_seconds / 60)
                    
                    daily_status[emp_code]['lateness_minutes'] = lateness_minutes
                    
                    if lateness_minutes > 0:
                        # Late
                        daily_status[emp_code]['is_late'] = True
                        hours, mins = divmod(lateness_minutes, 60)
                        daily_status[emp_code]['status'] = f"Late by {hours:02d}:{mins:02d}"
                        
                        logger.warning(f"Employee {daily_status[emp_code]['name']} (Code: {emp_code}) is LATE by {hours:02d}:{mins:02d}")
                        
                        # Send alert if enabled and not already alerted
                        if EMAIL_ENABLED and emp_code not in alerted_employees:
                            send_late_alert(emp_code, daily_status[emp_code])
                            alerted_employees.add(emp_code)
                            
                    else:
                        # On time or early
                        daily_status[emp_code]['is_late'] = False
                        if lateness_minutes < 0:
                            early_minutes = abs(lateness_minutes)
                            hours, mins = divmod(early_minutes, 60)
                            daily_status[emp_code]['status'] = f"Early by {hours:02d}:{mins:02d}"
                        else:
                            daily_status[emp_code]['status'] = "On time"
                        
                        logger.info(f"Employee {daily_status[emp_code]['name']} (Code: {emp_code}) arrived {daily_status[emp_code]['status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking punches: {e}")
        return False
    finally:
        connection.close()

def send_late_alert(emp_code, emp_status):
    """Send email alert for late employee"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER  # Change this to actual employee email if available
        msg['Subject'] = f"ATTENDANCE ALERT - {emp_status['name']} Late on Device 19"
        
        # Message body
        body = f"""
        <html>
        <body>
        <h2>Device 19 Attendance Alert - {COMPANY_NAME}</h2>
        <p><strong>Employee:</strong> {emp_status['name']} (Code: {emp_code})</p>
        <p><strong>Machine:</strong> {emp_status['machine']}</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
        <p><strong>Expected IN Time:</strong> {emp_status['expected_in']}</p>
        <p><strong>Actual IN Time:</strong> {emp_status['first_punch_time']}</p>
        <p><strong>Status:</strong> <span style="color: red;">{emp_status['status']}</span></p>
        
        <p>This employee punched in late on Device 19.</p>
        <p>Please take appropriate action.</p>
        
        <p>Regards,<br>Automated Attendance Monitor<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Late alert sent for {emp_status['name']} (Code: {emp_code})")
        
    except Exception as e:
        logger.error(f"Error sending email alert: {e}")

def print_current_status():
    """Print current status of all employees"""
    print(f"\n{'='*80}")
    print(f"DEVICE 19 REAL-TIME MONITORING STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    for emp_code, status in daily_status.items():
        status_color = ""
        if status['has_punched']:
            if status['is_late']:
                status_color = "🔴"  # Red for late
            else:
                status_color = "🟢"  # Green for on time/early
        else:
            status_color = "🟡"  # Yellow for waiting
        
        print(f"{status_color} Code: {emp_code:<4} | {status['name']:<25} | {status['machine']:<10} | Status: {status['status']}")
    
    print(f"{'='*80}")

def check_missed_employees():
    """Check for employees who haven't punched in by certain time"""
    current_time = datetime.now().time()
    cutoff_time = time(10, 0, 0)  # 10:00 AM cutoff
    
    if current_time > cutoff_time:
        for emp_code, status in daily_status.items():
            if not status['has_punched'] and emp_code not in alerted_employees:
                logger.warning(f"Employee {status['name']} (Code: {emp_code}) has not punched in by {cutoff_time}")
                
                # Send missing punch alert
                if EMAIL_ENABLED:
                    send_missing_punch_alert(emp_code, status)
                    alerted_employees.add(emp_code)

def send_missing_punch_alert(emp_code, emp_status):
    """Send alert for employee who hasn't punched in"""
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER
        msg['Subject'] = f"ATTENDANCE ALERT - {emp_status['name']} Missing Punch on Device 19"
        
        body = f"""
        <html>
        <body>
        <h2>Device 19 Missing Punch Alert - {COMPANY_NAME}</h2>
        <p><strong>Employee:</strong> {emp_status['name']} (Code: {emp_code})</p>
        <p><strong>Machine:</strong> {emp_status['machine']}</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
        <p><strong>Expected IN Time:</strong> {emp_status['expected_in']}</p>
        <p><strong>Current Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
        <p><strong>Status:</strong> <span style="color: red;">No punch recorded on Device 19</span></p>
        
        <p>This employee has not punched in on Device 19 yet.</p>
        <p>Please verify their attendance.</p>
        
        <p>Regards,<br>Automated Attendance Monitor<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Missing punch alert sent for {emp_status['name']} (Code: {emp_code})")
        
    except Exception as e:
        logger.error(f"Error sending missing punch alert: {e}")

def main_monitoring_loop():
    """Main 24/7 monitoring loop"""
    logger.info("=== STARTING DEVICE 19 REAL-TIME MONITORING ===")
    logger.info("Monitoring employees: " + ", ".join([f"{emp['name']} ({emp['code']})" for emp in EMPLOYEES_TO_MONITOR]))
    logger.info("Press Ctrl+C to stop monitoring")
    
    check_interval = 30  # Check every 30 seconds
    status_display_interval = 300  # Display status every 5 minutes
    last_status_display = datetime.now()
    
    while True:
        try:
            # Reset daily tracking if new day
            reset_daily_tracking()
            
            # Check for new punches
            check_device_19_punches()
            
            # Check for missed employees (after 10 AM)
            check_missed_employees()
            
            # Display status periodically
            if (datetime.now() - last_status_display).total_seconds() >= status_display_interval:
                print_current_status()
                last_status_display = datetime.now()
            
            # Sleep before next check
            time_module.sleep(check_interval)
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            logger.info("Continuing monitoring after error...")
            time_module.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main_monitoring_loop()
