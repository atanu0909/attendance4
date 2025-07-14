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

# Employee configuration - WILL BE LOADED FROM DATABASE
EMPLOYEES_TO_MONITOR = [
    {'code': '3', 'name': 'Swarup Mahapatra', 'machine': 'Ryobi 3', 'expected_in': '09:30:00', 'email': None},
    {'code': '595', 'name': 'Santanu Das', 'machine': 'Ryobi 3', 'expected_in': '09:00:00', 'email': None},
    {'code': '593', 'name': 'Rohit Kabiraj', 'machine': 'Ryobi 3', 'expected_in': '09:00:00', 'email': None},
    {'code': '695', 'name': 'Soumen Ghoshal', 'machine': 'Ryobi 2', 'expected_in': '09:00:00', 'email': None},
    {'code': '641', 'name': 'Souvik Ghosh', 'machine': 'Ryobi 2', 'expected_in': '08:30:00', 'email': None},
    {'code': '744', 'name': 'Manoj Maity', 'machine': 'Ryobi 2', 'expected_in': '08:30:00', 'email': None},
    {'code': '20', 'name': 'Bablu Rajak', 'machine': 'Flat Bed', 'expected_in': '09:30:00', 'email': None},
    {'code': '18', 'name': 'Somen Bhattacharjee', 'machine': 'Flat Bed', 'expected_in': '09:00:00', 'email': None}
]

# Fallback email configuration if database doesn't have emails
FALLBACK_EMAILS = {
    '3': 'aghosh09092004@gmail.com',
    '595': 'aghosh09092004@gmail.com',
    '593': 'aghosh09092004@gmail.com',
    '695': 'aghosh09092004@gmail.com',
    '641': 'aghosh09092004@gmail.com',
    '744': 'aghosh09092004@gmail.com',
    '20': 'aghosh09092004@gmail.com',
    '18': 'aghosh09092004@gmail.com'
}

# Daily notification tracking (reset each day)
daily_notifications = {
    'date': None,
    'notified_employees': set()
}

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

def load_employee_emails():
    """Load employee email addresses from database"""
    global EMPLOYEES_TO_MONITOR
    
    logger.info("📧 Loading employee email addresses from database...")
    
    conn = get_db_connection()
    if not conn:
        logger.warning("⚠️ Cannot load emails from database, using fallback emails")
        apply_fallback_emails()
        return
    
    try:
        # Get employee codes
        employee_codes = [emp['code'] for emp in EMPLOYEES_TO_MONITOR]
        codes_str = "', '".join(employee_codes)
        
        # Query for employee emails
        query = f"""
        SELECT 
            CAST(EmployeeCode as varchar) as EmployeeCode,
            EmployeeName,
            Email,
            ContactNo
        FROM dbo.Employees 
        WHERE CAST(EmployeeCode as varchar) IN ('{codes_str}')
        """
        
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            emails_loaded = 0
            emails_missing = 0
            
            logger.info(f"✅ Found {len(results)} employee records in database")
            
            # Create email lookup
            db_emails = {}
            for emp in results:
                code = emp['EmployeeCode']
                email = emp.get('Email', '').strip() if emp.get('Email') else ''
                name = emp.get('EmployeeName', '')
                contact = emp.get('ContactNo', '')
                
                if email:
                    db_emails[code] = email
                    logger.info(f"📧 {name} ({code}): {email}")
                    emails_loaded += 1
                else:
                    logger.warning(f"⚠️ {name} ({code}): No email in database")
                    emails_missing += 1
            
            # Update EMPLOYEES_TO_MONITOR with database emails
            for emp in EMPLOYEES_TO_MONITOR:
                if emp['code'] in db_emails:
                    emp['email'] = db_emails[emp['code']]
                else:
                    # Use fallback email
                    emp['email'] = FALLBACK_EMAILS.get(emp['code'])
                    logger.info(f"🔄 Using fallback email for {emp['name']} ({emp['code']}): {emp['email']}")
            
            logger.info(f"📊 Email loading summary:")
            logger.info(f"   • Emails loaded from database: {emails_loaded}")
            logger.info(f"   • Emails missing in database: {emails_missing}")
            logger.info(f"   • Using fallback emails: {emails_missing}")
            
        else:
            logger.warning("⚠️ No employee records found in database")
            apply_fallback_emails()
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error loading emails from database: {e}")
        apply_fallback_emails()

def apply_fallback_emails():
    """Apply fallback email configuration"""
    global EMPLOYEES_TO_MONITOR
    
    logger.info("🔄 Applying fallback email configuration...")
    
    for emp in EMPLOYEES_TO_MONITOR:
        emp['email'] = FALLBACK_EMAILS.get(emp['code'])
        logger.info(f"📧 {emp['name']} ({emp['code']}): {emp['email']}")
    
    logger.info("✅ Fallback emails applied successfully")

def send_email_alert(subject, body):
    """Send email alert to management"""
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

def send_individual_late_email(employee):
    """Send personalized late arrival email to individual employee"""
    if not EMAIL_ENABLED:
        logger.info("Email notifications disabled")
        return False
    
    # Check if employee has email address
    email_address = employee.get('email')
    if not email_address:
        logger.warning(f"⚠️ No email address for {employee['name']} ({employee['code']}) - skipping individual email")
        return False
    
    try:
        current_dt = datetime.now()
        today = current_dt.strftime('%Y-%m-%d')
        
        subject = f"⏰ Late Arrival Notice - {today}"
        
        # Create personalized email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid #ff6b6b; padding-left: 20px;">
                <h2 style="color: #ff6b6b;">⏰ Late Arrival Notice</h2>
            </div>
            
            <p>Dear <strong>{employee['name']}</strong>,</p>
            
            <p>This is to inform you that you arrived late today.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">Attendance Details:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Employee Code:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{employee['code']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Date:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{today}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Machine Assignment:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{employee['machine']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Expected Arrival Time:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{employee['expected_in']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>Actual Arrival Time:</strong></td>
                        <td style="padding: 8px;">{employee.get('actual_in', 'Not yet arrived')}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #856404;">📋 Reminder:</h4>
                <p style="margin-bottom: 0;">Please ensure to arrive on time to maintain productivity and team coordination. If you have any ongoing issues affecting your punctuality, please discuss with your supervisor.</p>
            </div>
            
            <p>Thank you for your attention to this matter.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <div style="color: #666; font-size: 12px;">
                <p><strong>{COMPANY_NAME}</strong><br>
                HR Department<br>
                <em>This is an automated notice from the Attendance Monitoring System.</em></p>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email_address
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Individual late notice sent to {employee['name']} ({email_address})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send individual email to {employee['name']}: {e}")
        return False

def send_management_summary_email(late_employees, today):
    """Send summary email to management with all late employees"""
    if not late_employees:
        return True
        
    subject = f"📊 Daily Late Arrival Summary - Device 19 - {today}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="border-left: 4px solid #007bff; padding-left: 20px;">
            <h2 style="color: #007bff;">📊 Daily Late Arrival Summary</h2>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Summary Information:</h3>
            <p><strong>Company:</strong> {COMPANY_NAME}</p>
            <p><strong>Date:</strong> {today}</p>
            <p><strong>Device:</strong> Device 19</p>
            <p><strong>Total Late Employees:</strong> {len(late_employees)}</p>
            <p><strong>Report Generated:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
        </div>
        
        <h3>Late Employees Details:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%; background-color: white;">
            <tr style="background-color: #007bff; color: white;">
                <th style="padding: 12px; text-align: left;">Code</th>
                <th style="padding: 12px; text-align: left;">Name</th>
                <th style="padding: 12px; text-align: left;">Machine</th>
                <th style="padding: 12px; text-align: left;">Expected Time</th>
                <th style="padding: 12px; text-align: left;">Actual Time</th>
                <th style="padding: 12px; text-align: left;">Email Sent</th>
            </tr>
    """
    
    for emp in late_employees:
        body += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">{emp['code']}</td>
            <td style="padding: 10px;">{emp['name']}</td>
            <td style="padding: 10px;">{emp['machine']}</td>
            <td style="padding: 10px;">{emp['expected_in']}</td>
            <td style="padding: 10px;">{emp.get('actual_in', 'Not arrived')}</td>
            <td style="padding: 10px;">✅ Yes</td>
        </tr>
        """
    
    body += """
        </table>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #155724;">📧 Action Taken:</h4>
            <p style="margin-bottom: 0;">Individual late arrival notices have been sent to all late employees' email addresses automatically.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <div style="color: #666; font-size: 12px;">
            <p><em>This is an automated report from the Device 19 Attendance Monitor.</em></p>
        </div>
    </body>
    </html>
    """
    
    return send_email_alert(subject, body)

def reset_daily_notifications(today):
    """Reset daily notification tracking for a new day"""
    global daily_notifications
    if daily_notifications['date'] != today:
        logger.info(f"🔄 Resetting daily notifications for {today}")
        daily_notifications = {
            'date': today,
            'notified_employees': set()
        }

def should_send_notification(employee_code, today):
    """Check if we should send notification for this employee today"""
    global daily_notifications
    reset_daily_notifications(today)
    
    if employee_code in daily_notifications['notified_employees']:
        logger.info(f"⏭️ Already notified about {employee_code} today - skipping")
        return False
    
    return True

def mark_employee_notified(employee_code):
    """Mark an employee as notified for today"""
    global daily_notifications
    daily_notifications['notified_employees'].add(employee_code)
    logger.info(f"✅ Marked {employee_code} as notified for today")

def check_device_19_attendance():
    """Check attendance for Device 19 employees"""
    global daily_notifications
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
            new_late_employees = []  # Only employees we haven't notified about yet
            
            for emp in EMPLOYEES_TO_MONITOR:
                expected_time = datetime.strptime(emp['expected_in'], '%H:%M:%S').time()
                if current_time > expected_time:
                    late_employees.append(emp)
                    
                    # Check if we should notify about this employee
                    if should_send_notification(emp['code'], today):
                        new_late_employees.append(emp)
            
            if new_late_employees:
                logger.warning(f"🚨 {len(new_late_employees)} NEW late employees detected!")
                
                # Send individual emails to each late employee
                emails_sent = 0
                for emp in new_late_employees:
                    if send_individual_late_email(emp):
                        emails_sent += 1
                        mark_employee_notified(emp['code'])
                
                logger.info(f"📧 Sent {emails_sent} individual late notices")
                
                # Also send summary to management
                if emails_sent > 0:
                    send_management_summary_email(new_late_employees, today)
                        
            elif late_employees:
                logger.info(f"📋 {len(late_employees)} employees are late, but already notified today")
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
            
            # Check for late arrivals and log first punch times
            current_time = current_dt.time()
            late_employees = []
            new_late_employees = []  # Only employees we haven't notified about yet
            
            for emp_code, record in first_punches.items():
                first_time = record['LogDate']
                
                # Find employee details
                emp_details = next((emp for emp in EMPLOYEES_TO_MONITOR if emp['code'] == emp_code), None)
                if emp_details:
                    logger.info(f"✅ {emp_details['name']} (Code: {emp_code}) - First IN: {first_time.strftime('%H:%M:%S')}")
                    
                    # Check if this employee is late
                    expected_time = datetime.strptime(emp_details['expected_in'], '%H:%M:%S').time()
                    actual_time = first_time.time()
                    
                    if actual_time > expected_time:
                        late_emp = {
                            'code': emp_code,
                            'name': emp_details['name'],
                            'machine': emp_details['machine'],
                            'expected_in': emp_details['expected_in'],
                            'actual_in': first_time.strftime('%H:%M:%S')
                        }
                        late_employees.append(late_emp)
                        
                        # Check if we should notify about this employee
                        if should_send_notification(emp_code, today):
                            new_late_employees.append(late_emp)
                        
                        logger.warning(f"🔴 LATE: {emp_details['name']} (Code: {emp_code}) - Expected: {emp_details['expected_in']}, Actual: {first_time.strftime('%H:%M:%S')}")
            
            # Check for employees who haven't arrived yet
            for emp in EMPLOYEES_TO_MONITOR:
                if emp['code'] not in first_punches:
                    expected_time = datetime.strptime(emp['expected_in'], '%H:%M:%S').time()
                    if current_time > expected_time:
                        late_emp = {
                            'code': emp['code'],
                            'name': emp['name'],
                            'machine': emp['machine'],
                            'expected_in': emp['expected_in'],
                            'actual_in': 'NOT ARRIVED'
                        }
                        late_employees.append(late_emp)
                        
                        # Check if we should notify about this employee
                        if should_send_notification(emp['code'], today):
                            new_late_employees.append(late_emp)
                        
                        logger.warning(f"🔴 ABSENT/LATE: {emp['name']} (Code: {emp['code']}) - Expected: {emp['expected_in']}, Status: NOT ARRIVED")
            
            # Send email alert only for new late employees
            if new_late_employees:
                logger.warning(f"📧 NEW Late employees found: {len(new_late_employees)} employees")
                
                # Send individual emails to each late employee
                emails_sent = 0
                for emp in new_late_employees:
                    if send_individual_late_email(emp):
                        emails_sent += 1
                        mark_employee_notified(emp['code'])
                
                logger.info(f"📧 Sent {emails_sent} individual late notices")
                
                # Also send summary to management
                if emails_sent > 0:
                    send_management_summary_email(new_late_employees, today)
                    logger.info(f"✅ Management summary sent to {ALERT_EMAIL}")
                    
            elif late_employees:
                logger.info(f"📋 {len(late_employees)} employees are late, but already notified today")
            else:
                logger.info("✅ All employees arrived on time - no email alert needed")
        
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
        
        # Load employee emails from database on startup
        logger.info("🔧 Loading employee email configuration...")
        load_employee_emails()
        
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
