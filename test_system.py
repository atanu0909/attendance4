#!/usr/bin/env python3
"""
Test script to debug email and database connectivity
"""

import os
import sys
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Email configuration
GMAIL_USER = 'ghoshatanu32309@gmail.com'
GMAIL_PASSWORD = 'oqahvqkuaziufvfb'
ALERT_EMAIL = 'aghosh09092004@gmail.com'

def test_email_connection():
    """Test email sending functionality"""
    logger.info("🔍 Testing email connection...")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = "🧪 Test Email - Device 19 Attendance Monitor"
        
        body = f"""
        <h2>📧 Test Email from Device 19 Attendance Monitor</h2>
        <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> Email system is working correctly!</p>
        <p><strong>From:</strong> {GMAIL_USER}</p>
        <p><strong>To:</strong> {ALERT_EMAIL}</p>
        <p><em>This is a test email to verify the email alert system is functioning.</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    logger.info("🔍 Testing database connection...")
    
    try:
        import pymssql
        
        # Database parameters
        server = '1.22.45.168'
        port = 19471
        database = 'etimetrackliteWEB'
        username = 'sa'
        password = 'sa@123'
        
        logger.info(f"Connecting to {server}:{port}/{database}")
        
        conn = pymssql.connect(
            server=server,
            port=port,
            user=username,
            password=password,
            database=database,
            timeout=30
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT GETDATE() as CurrentTime")
        result = cursor.fetchone()
        
        logger.info(f"✅ Database connection successful! Server time: {result[0]}")
        
        # Test attendance query
        today = datetime.now().strftime('%Y-%m-%d')
        month_year = f"{datetime.now().month}_{datetime.now().year}"
        
        query = f"""
        SELECT COUNT(*) as RecordCount
        FROM dbo.DeviceLogs_{month_year}
        WHERE CAST(LogDate as DATE) = '{today}'
            AND DeviceId = 19
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        logger.info(f"📊 Device 19 records today: {result[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

def check_current_attendance():
    """Check if there are any late employees right now"""
    logger.info("🔍 Checking for late employees...")
    
    current_time = datetime.now().time()
    
    employees = [
        {'code': '3', 'name': 'Swarup Mahapatra', 'expected_in': '09:00:00'},
        {'code': '595', 'name': 'Santanu Das', 'expected_in': '07:00:00'},
        {'code': '593', 'name': 'Rohit Kabiraj', 'expected_in': '07:00:00'},
        {'code': '695', 'name': 'Soumen Ghoshal', 'expected_in': '09:00:00'},
        {'code': '641', 'name': 'Souvik Ghosh', 'expected_in': '07:00:00'},
        {'code': '744', 'name': 'Manoj Maity', 'expected_in': '07:00:00'},
        {'code': '20', 'name': 'Bablu Rajak', 'expected_in': '07:00:00'},
        {'code': '18', 'name': 'Somen Bhattacharjee', 'expected_in': '07:00:00'}
    ]
    
    late_employees = []
    
    for emp in employees:
        expected_time = datetime.strptime(emp['expected_in'], '%H:%M:%S').time()
        if current_time > expected_time:
            late_employees.append(emp)
            logger.info(f"⏰ {emp['name']} (Code: {emp['code']}) - Expected: {emp['expected_in']} - Status: LATE")
    
    logger.info(f"📊 Total employees that should be checked for lateness: {len(late_employees)}")
    return late_employees

def main():
    """Main test function"""
    logger.info("🧪 Starting comprehensive system test...")
    logger.info("=" * 50)
    
    # Test 1: Email system
    logger.info("TEST 1: Email System")
    email_success = test_email_connection()
    
    # Test 2: Database connection
    logger.info("\nTEST 2: Database Connection")
    db_success = test_database_connection()
    
    # Test 3: Check current attendance status
    logger.info("\nTEST 3: Current Attendance Status")
    late_employees = check_current_attendance()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📋 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    logger.info(f"✅ Email System: {'WORKING' if email_success else 'FAILED'}")
    logger.info(f"✅ Database Connection: {'WORKING' if db_success else 'FAILED'}")
    logger.info(f"📊 Employees expected to be late: {len(late_employees)}")
    
    if email_success and len(late_employees) > 0:
        logger.info("💡 RECOMMENDATION: You should have received an email alert!")
    elif not email_success:
        logger.info("⚠️  ISSUE: Email system is not working - check Gmail credentials")
    elif len(late_employees) == 0:
        logger.info("ℹ️  INFO: No late employees detected - no email alert needed")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
