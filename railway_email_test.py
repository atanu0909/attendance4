#!/usr/bin/env python3
"""
Railway Email Test - Force send test email to debug why emails aren't being received
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

def send_test_email():
    """Send a test email to verify the email system"""
    
    # Email configuration from environment variables
    GMAIL_USER = os.getenv('GMAIL_USER', 'ghoshatanu32309@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'oqahvqkuaziufvfb')
    ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'aghosh09092004@gmail.com')
    
    logger.info("🧪 RAILWAY EMAIL TEST - Sending test email...")
    logger.info(f"From: {GMAIL_USER}")
    logger.info(f"To: {ALERT_EMAIL}")
    logger.info(f"Password: {'***' if GMAIL_PASSWORD else 'NOT SET'}")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = f"🧪 RAILWAY TEST - Device 19 Monitor - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""
        <h2>🧪 RAILWAY DEPLOYMENT TEST EMAIL</h2>
        <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Source:</strong> Railway Cloud Deployment</p>
        <p><strong>Status:</strong> ✅ Email system is working!</p>
        <p><strong>From:</strong> {GMAIL_USER}</p>
        <p><strong>To:</strong> {ALERT_EMAIL}</p>
        
        <h3>📋 System Check Results:</h3>
        <ul>
            <li>✅ Railway deployment: ACTIVE</li>
            <li>✅ Email credentials: CONFIGURED</li>
            <li>✅ SMTP connection: WORKING</li>
            <li>✅ Message delivery: SUCCESS</li>
        </ul>
        
        <p><em>If you received this email, the attendance monitoring system is working correctly!</em></p>
        <p><em>Check your spam/junk folder if you don't see attendance alerts.</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info("✅ TEST EMAIL SENT SUCCESSFULLY!")
        logger.info("📧 Check your inbox: aghosh09092004@gmail.com")
        logger.info("📧 Also check spam/junk folder if not in inbox")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST EMAIL FAILED: {e}")
        return False

def main():
    """Main test function - just send test email"""
    logger.info("🚀 RAILWAY EMAIL TEST STARTING...")
    logger.info("=" * 50)
    
    # Send test email immediately
    email_ok = send_test_email()
    
    if email_ok:
        logger.info("🎉 SUCCESS: Test email sent!")
        logger.info("📧 Check aghosh09092004@gmail.com for the test email")
    else:
        logger.error("❌ FAILED: Could not send test email")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
    
    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = alert_email
        msg['Subject'] = "🧪 Railway Test - Device 19 Monitor is ACTIVE!"
        
        body = f"""
        <h2>✅ Railway Deployment Test Successful!</h2>
        <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> Device 19 Attendance Monitor is running on Railway!</p>
        <p><strong>System Info:</strong></p>
        <ul>
            <li>Service: ACTIVE ✅</li>
            <li>Database: Checking every 5 minutes</li>
            <li>Email alerts: WORKING ✅</li>
            <li>Monitoring: 8 employees on Device 19</li>
        </ul>
        <p><strong>Next Steps:</strong></p>
        <p>If you receive this email, the system is working! You will receive alerts when employees are late.</p>
        <p><em>This is a test from your Railway-deployed attendance monitor.</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

if __name__ == "__main__":
    send_test_email()
