#!/usr/bin/env python3
"""
Simple email test script for Railway deployment
This will definitely send an email if deployed to Railway
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

# Email configuration from environment variables
GMAIL_USER = os.getenv('GMAIL_USER', 'ghoshatanu32309@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'oqahvqkuaziufvfb')
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'aghosh09092004@gmail.com')

def send_test_alert():
    """Send a test email alert immediately"""
    try:
        print(f"🔧 Sending test email from Railway...")
        print(f"📧 From: {GMAIL_USER}")
        print(f"📧 To: {ALERT_EMAIL}")
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = "🚨 URGENT TEST - Railway Device 19 Monitor is WORKING!"
        
        body = f"""
        <h2>🚨 URGENT TEST ALERT - Railway Deployment</h2>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> 🟢 Railway email system is WORKING!</p>
        <p><strong>Message:</strong> This confirms your Device 19 attendance monitor is deployed and can send emails.</p>
        
        <h3>🎯 What This Means:</h3>
        <ul>
            <li>✅ Railway deployment is successful</li>
            <li>✅ Email system is configured correctly</li>
            <li>✅ You will receive alerts when employees are late</li>
        </ul>
        
        <p><strong>Next:</strong> Monitor this email address for actual late employee alerts during work hours!</p>
        <p><em>Sent from Railway Cloud - Device 19 Attendance Monitor</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    """Send test email and exit"""
    print("🚀 Railway Email Test - Device 19 Attendance Monitor")
    print("=" * 60)
    
    # Send test email
    success = send_test_alert()
    
    if success:
        print("🎉 SUCCESS: Test email sent!")
        print("📱 Check your email: aghosh09092004@gmail.com")
    else:
        print("❌ FAILED: Could not send test email")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
