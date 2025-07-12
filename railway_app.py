#!/usr/bin/env python3
"""
Railway deployment script for Device 19 Attendance Monitor
Runs continuously with scheduled checks
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime, time as dt_time
from device_19_github_monitor import check_device_19_attendance

# Setup logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('railway_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

def run_attendance_check():
    """Wrapper function for scheduled attendance checks"""
    try:
        logger.info("🔄 Running scheduled attendance check...")
        check_device_19_attendance()
        logger.info("✅ Attendance check completed successfully")
    except Exception as e:
        logger.error(f"❌ Error in attendance check: {e}")

def is_work_hours():
    """Check if current time is within work hours (6 AM to 11 PM IST)"""
    now = datetime.now()
    work_start = dt_time(6, 0)  # 6 AM
    work_end = dt_time(23, 0)   # 11 PM
    current_time = now.time()
    
    return work_start <= current_time <= work_end

def main():
    """Main function for Railway deployment"""
    logger.info("🚀 Starting Device 19 Attendance Monitor on Railway")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    logger.info(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    logger.info("🔧 Setting up scheduled monitoring...")
    
    # Schedule the job to run every 5 minutes
    schedule.every(5).minutes.do(run_attendance_check)
    
    logger.info("✅ Scheduler configured - Running every 5 minutes")
    logger.info("⏳ Starting continuous monitoring loop...")
    
    # Keep the application running
    while True:
        try:
            # Only run during work hours
            if is_work_hours():
                schedule.run_pending()
            else:
                logger.info("⏰ Outside work hours - skipping checks")
            
            # Sleep for 30 seconds before checking again
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("🛑 Stopping attendance monitor...")
            break
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
