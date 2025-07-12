#!/usr/bin/env python3
"""
Railway-optimized Device 19 Attendance Monitor
Simplified version with better error handling for cloud deployment
"""

import os
import sys
import time
import logging
from datetime import datetime, time as dt_time
from device_19_github_monitor import (
    check_device_19_attendance, 
    logger as monitor_logger,
    EMPLOYEES_TO_MONITOR
)

# Setup logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
            # Don't fail completely, just log and continue
    
    def run(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting Device 19 Attendance Monitor on Railway")
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
