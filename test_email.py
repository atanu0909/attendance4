import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email configuration
GMAIL_USER = 'ghoshatanu32309@gmail.com'
GMAIL_PASSWORD = 'oqahvqkuaziufvfb'
ALERT_EMAIL = 'aghosh09092004@gmail.com'

def test_email_setup():
    """Test email setup by sending a test email"""
    try:
        print("Testing email setup...")
        print(f"From: {GMAIL_USER}")
        print(f"To: {ALERT_EMAIL}")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = "🧪 TEST - Device 19 Monitor Setup Verification"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="border: 2px solid #00aa00; padding: 20px; border-radius: 10px; background-color: #f0fff0;">
            <h2 style="color: #00aa00; margin-top: 0;">✅ Test Email - Device 19 Monitor</h2>
            
            <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Repository:</strong> https://github.com/atanu0909/attendance4</p>
            <p><strong>Alert Email:</strong> {ALERT_EMAIL}</p>
            
            <div style="background-color: #ffffff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="color: #333; margin-top: 0;">System Status</h3>
                <p>✅ Email configuration: Working</p>
                <p>✅ Gmail connection: Success</p>
                <p>✅ Target email: {ALERT_EMAIL}</p>
            </div>
            
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="color: #0066cc; margin-top: 0;">What's Next?</h3>
                <p>If you received this email, the system is ready to monitor Device 19 attendance!</p>
                <p>You will receive alerts when any of the 8 employees arrive late.</p>
                <ul>
                    <li>Monitoring runs every 5 minutes during work hours</li>
                    <li>Alerts sent only once per employee per day</li>
                    <li>Rich HTML emails with all details</li>
                </ul>
            </div>
            
            <hr style="margin: 20px 0; border: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px; margin-bottom: 0;">
                <em>This is a test email to verify the Device 19 Attendance Monitor setup.</em><br>
                <em>Future alerts will be sent to this email address when employees are late.</em>
            </p>
        </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        print("Connecting to Gmail...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        print("Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ SUCCESS: Test email sent successfully!")
        print(f"Check your inbox at {ALERT_EMAIL}")
        print("If you don't see it, check your spam folder.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to send test email")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Device 19 Attendance Monitor - Email Test")
    print("=" * 60)
    
    success = test_email_setup()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Email system is working correctly!")
        print("You can now set up GitHub Actions with confidence.")
    else:
        print("❌ Email system needs attention.")
        print("Please check your Gmail credentials and try again.")
    print("=" * 60)
