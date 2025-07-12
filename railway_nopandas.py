#!/usr/bin/env python3
"""
Railway-optimized Device 19 Attendance Monitor - No Pandas Version
Uses pure Python with pymssql for maximum compatibility
"""

import os
import sys
import time
import logging
from datetime import datetime, time as dt_time
import pymssql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Setup logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
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
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'aghosh09092004@gmail.com')

# Employee configuration - UPDATED WITH ACTUAL SHIFT TIMES FROM DATABASE
EMPLOYEES_TO_MONITOR = [
    {'code': '3', 'name': 'Swarup Mahapatra', 'machine': 'Ryobi 3', 'expected_in': '09:30:00'},
    {'code': '595', 'name': 'Santanu Das', 'machine': 'Ryobi 3', 'expected_in': '09:00:00'},
    {'code': '593', 'name': 'Rohit Kabiraj', 'machine': 'Ryobi 3', 'expected_in': '09:00:00'},
    {'code': '695', 'name': 'Soumen Ghoshal', 'machine': 'Ryobi 2', 'expected_in': '09:00:00'},
    {'code': '641', 'name': 'Souvik Ghosh', 'machine': 'Ryobi 2', 'expected_in': '08:30:00'},
    {'code': '744', 'name': 'Manoj Maity', 'machine': 'Ryobi 2', 'expected_in': '08:30:00'},
    {'code': '20', 'name': 'Bablu Rajak', 'machine': 'Flat Bed', 'expected_in': '09:30:00'},
    {'code': '18', 'name': 'Somen Bhattacharjee', 'machine': 'Flat Bed', 'expected_in': '09:00:00'}
]

def get_db_connection():
    """Get database connection using pymssql"""
    try:
        # Extract server and port from DB_SERVER
        server_parts = DB_SERVER.split(',')
        server = server_parts[0]
        port = int(server_parts[1]) if len(server_parts) > 1 else 1433
        
        logger.info(f"Connecting to database: {server}:{port}")
        
        conn = pymssql.connect(
            server=server,
            port=port,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            timeout=30,
            login_timeout=30
        )
        
        logger.info("✅ Database connection successful!")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def send_email_alert(subject, body):
    """Send email alert"""
    if not EMAIL_ENABLED:
        logger.info("Email notifications disabled")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {ALERT_EMAIL}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False

def check_device_19_attendance():
    """Check attendance for Device 19 employees"""
    logger.info("🔍 Checking Device 19 attendance...")
    
    conn = get_db_connection()
    if not conn:
        logger.error("Cannot proceed without database connection")
        return
    
    try:
        current_dt = datetime.now()
        today = current_dt.strftime('%Y-%m-%d')
        month_year = f"{current_dt.month}_{current_dt.year}"
        
        # Get employee codes as string
        employee_codes = [emp['code'] for emp in EMPLOYEES_TO_MONITOR]
        codes_str = "', '".join(employee_codes)
        
        # Query for Device 19 attendance
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
            AND CAST(dl.UserId as varchar) IN ('{codes_str}')
        ORDER BY CAST(dl.UserId as varchar), dl.LogDate
        """
        
        logger.info(f"Executing query for {len(employee_codes)} employees on {today}")
        
        # Execute query using pymssql
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            logger.info("No records found for Device 19 today")
            
            # Check if employees are late
            current_time = current_dt.time()
            late_employees = []
            
            for emp in EMPLOYEES_TO_MONITOR:
                expected_time = datetime.strptime(emp['expected_in'], '%H:%M:%S').time()
                if current_time > expected_time:
                    late_employees.append(emp)
            
            if late_employees:
                logger.warning(f"🚨 {len(late_employees)} employees are late!")
                
                # Send email alert
                subject = f"🚨 LATE ALERT - Device 19 Attendance - {today}"
                body = f"""
                <h2>🚨 Late Employee Alert - {COMPANY_NAME}</h2>
                <p><strong>Date:</strong> {today}</p>
                <p><strong>Time:</strong> {current_dt.strftime('%H:%M:%S')}</p>
                <p><strong>Device:</strong> Device 19</p>
                
                <h3>Late Employees:</h3>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f0f0f0;">
                        <th>Code</th>
                        <th>Name</th>
                        <th>Machine</th>
                        <th>Expected Time</th>
                    </tr>
                """
                
                for emp in late_employees:
                    body += f"""
                    <tr>
                        <td>{emp['code']}</td>
                        <td>{emp['name']}</td>
                        <td>{emp['machine']}</td>
                        <td>{emp['expected_in']}</td>
                    </tr>
                    """
                
                body += """
                </table>
                <p><em>This is an automated alert from the Device 19 Attendance Monitor.</em></p>
                """
                
                send_email_alert(subject, body)
            else:
                logger.info("✅ No late employees detected")
        else:
            logger.info(f"✅ Found {len(results)} records for Device 19")
            
            # Process results without pandas
            first_punches = {}
            for record in results:
                emp_code = record['EmployeeCode']
                log_date = record['LogDate']
                
                if emp_code not in first_punches or log_date < first_punches[emp_code]['LogDate']:
                    first_punches[emp_code] = record
            
            for emp_code, record in first_punches.items():
                first_time = record['LogDate']
                
                # Find employee details
                emp_details = next((emp for emp in EMPLOYEES_TO_MONITOR if emp['code'] == emp_code), None)
                if emp_details:
                    logger.info(f"✅ {emp_details['name']} (Code: {emp_code}) - First IN: {first_time.strftime('%H:%M:%S')}")
        
        cursor.close()
        
    except Exception as e:
        logger.error(f"❌ Error checking attendance: {e}")
    finally:
        conn.close()

class AttendanceMonitor:
    """Railway-optimized attendance monitoring class"""
    
    def __init__(self):
        self.check_interval = 5 * 60  # 5 minutes in seconds
        self.last_check = None
        self.running = True
        
    def is_work_hours(self):
        """Check if current time is within work hours (6 AM to 11 PM IST)"""
        now = datetime.now()
        work_start = dt_time(6, 0)  # 6 AM
        work_end = dt_time(23, 0)   # 11 PM
        current_time = now.time()
        
        return work_start <= current_time <= work_end
    
    def should_check(self):
        """Determine if we should run a check now"""
        if not self.is_work_hours():
            return False
            
        if self.last_check is None:
            return True
            
        time_since_last = time.time() - self.last_check
        return time_since_last >= self.check_interval
    
    def run_check(self):
        """Run the attendance check"""
        try:
            logger.info("🔄 Starting attendance check...")
            logger.info(f"👥 Monitoring {len(EMPLOYEES_TO_MONITOR)} employees")
            
            check_device_19_attendance()
            
            self.last_check = time.time()
            logger.info("✅ Attendance check completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in attendance check: {e}")
    
    def run(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting Device 19 Attendance Monitor on Railway (No Pandas)")
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("🔧 Starting continuous monitoring...")
        
        while self.running:
            try:
                if self.should_check():
                    self.run_check()
                else:
                    if not self.is_work_hours():
                        logger.info("⏰ Outside work hours - monitoring paused")
                    else:
                        logger.info("⏳ Waiting for next check cycle...")
                
                # Sleep for 30 seconds before checking again
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping attendance monitor...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main entry point for Railway"""
    try:
        monitor = AttendanceMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
