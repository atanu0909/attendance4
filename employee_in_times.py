import pyodbc
from datetime import datetime, timedelta

# Database connection parameters
server = '1.22.45.168,19471'
database = 'etimetrackliteWEB'
username = 'sa'
password = 'sa@123'

# Working connection string
conn_str = (
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

def connect_to_database():
    """Establish connection to the database"""
    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to the database!")
        return conn
    except Exception as e:
        print("❌ Failed to connect to database:", e)
        return None

def get_employee_in_times_today(conn):
    """Get employee names and IN times for today"""
    print("\n" + "="*80)
    print("📊 EMPLOYEE NAMES AND IN TIMES - TODAY")
    print("="*80)
    
    try:
        cursor = conn.cursor()
        
        # Try to get from AttendanceLogs first
        today_str = datetime.now().date().strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            al.InTime,
            al.OutTime,
            al.Status
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE al.AttendanceDate = '{today_str}'
            AND al.InTime != '1900-01-01 00:00:00'
            AND al.InTime IS NOT NULL
        ORDER BY al.InTime ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"📅 Date: {today_str}")
            print(f"👥 Total employees with IN time: {len(results)}")
            print("-" * 80)
            print(f"{'Employee Name':<30} {'Code':<8} {'IN Time':<15} {'OUT Time':<15} {'Status':<10}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0][:29] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                in_time = row[2].strftime('%H:%M:%S') if row[2] else "N/A"
                out_time = row[3].strftime('%H:%M:%S') if row[3] and str(row[3]) != '1900-01-01 00:00:00' else "Not Out"
                status = row[4] if row[4] else "N/A"
                
                print(f"{emp_name:<30} {emp_code:<8} {in_time:<15} {out_time:<15} {status:<10}")
        else:
            print(f"❌ No attendance records found for today ({today_str})")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting today's attendance: {e}")
        return []

def get_employee_in_times_recent(conn, days=7):
    """Get employee names and IN times for recent days"""
    print("\n" + "="*80)
    print(f"📊 EMPLOYEE NAMES AND IN TIMES - LAST {days} DAYS")
    print("="*80)
    
    try:
        cursor = conn.cursor()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE al.AttendanceDate BETWEEN '{start_str}' AND '{end_str}'
            AND al.InTime != '1900-01-01 00:00:00'
            AND al.InTime IS NOT NULL
        ORDER BY al.AttendanceDate DESC, al.InTime ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"📅 Period: {start_str} to {end_str}")
            print(f"👥 Total attendance records: {len(results)}")
            print("-" * 95)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'IN Time':<12} {'OUT Time':<12} {'Status':<10}")
            print("-" * 95)
            
            for row in results:
                emp_name = row[0][:24] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                att_date = row[2].strftime('%Y-%m-%d') if row[2] else "N/A"
                in_time = row[3].strftime('%H:%M:%S') if row[3] else "N/A"
                out_time = row[4].strftime('%H:%M:%S') if row[4] and str(row[4]) != '1900-01-01 00:00:00' else "Not Out"
                status = row[5] if row[5] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {att_date:<12} {in_time:<12} {out_time:<12} {status:<10}")
        else:
            print(f"❌ No attendance records found for the last {days} days")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting recent attendance: {e}")
        return []

def get_live_punch_records(conn):
    """Get recent punch records from device logs"""
    print("\n" + "="*80)
    print("📊 RECENT PUNCH RECORDS (DEVICE LOGS)")
    print("="*80)
    
    try:
        cursor = conn.cursor()
        
        # Get device logs from the current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        table_name = f"DeviceLogs_{current_month}_{current_year}"
        
        # Get logs from today
        today_str = datetime.now().date().strftime('%Y-%m-%d')
        
        query = f"""
        SELECT TOP 30
            e.EmployeeName,
            e.EmployeeCode,
            dl.LogDate,
            dl.AttDirection,
            dl.DeviceId,
            dl.UserId
        FROM {table_name} dl
        LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
        WHERE dl.LogDate >= '{today_str}'
        ORDER BY dl.LogDate DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"📅 Date: {today_str}")
            print(f"🔍 Total punch records: {len(results)}")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Punch Time':<20} {'Direction':<10} {'Device':<8}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0][:24] if row[0] else "Unknown"
                emp_code = row[1] if row[1] else row[5]
                punch_time = row[2].strftime('%H:%M:%S') if row[2] else "N/A"
                direction = row[3] if row[3] else "N/A"
                device_id = row[4] if row[4] else "N/A"
                
                print(f"{emp_name:<25} {str(emp_code):<8} {punch_time:<20} {direction:<10} {str(device_id):<8}")
        else:
            print(f"❌ No punch records found for today")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting punch records: {e}")
        return []

def get_employee_summary(conn):
    """Get summary of employees with recent activity"""
    print("\n" + "="*80)
    print("📊 EMPLOYEE SUMMARY - RECENT ACTIVITY")
    print("="*80)
    
    try:
        cursor = conn.cursor()
        
        # Get employees who have punched in the last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            COUNT(al.AttendanceLogId) as TotalDays,
            MAX(al.AttendanceDate) as LastAttendanceDate,
            MAX(CASE WHEN al.InTime != '1900-01-01 00:00:00' THEN al.InTime END) as LastInTime
        FROM Employees e
        LEFT JOIN AttendanceLogs al ON e.EmployeeId = al.EmployeeId 
            AND al.AttendanceDate BETWEEN '{start_str}' AND '{end_str}'
        WHERE e.Status = 'Working'
        GROUP BY e.EmployeeName, e.EmployeeCode
        HAVING COUNT(al.AttendanceLogId) > 0
        ORDER BY MAX(al.AttendanceDate) DESC, e.EmployeeName
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"📅 Period: Last 7 days ({start_str} to {end_str})")
            print(f"👥 Employees with activity: {len(results)}")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Days':<6} {'Last Date':<12} {'Last IN Time':<12}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0][:24] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                total_days = row[2] if row[2] else 0
                last_date = row[3].strftime('%Y-%m-%d') if row[3] else "N/A"
                last_in_time = row[4].strftime('%H:%M:%S') if row[4] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {total_days:<6} {last_date:<12} {last_in_time:<12}")
        else:
            print(f"❌ No employees with recent activity found")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting employee summary: {e}")
        return []

def main():
    """Main function to get employee names and IN times"""
    print("🚀 EMPLOYEE ATTENDANCE TRACKER")
    print("🔍 Finding Employee Names and IN Times")
    print("="*80)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Get today's IN times
        today_results = get_employee_in_times_today(conn)
        
        # Get recent IN times (last 7 days)
        recent_results = get_employee_in_times_recent(conn, days=7)
        
        # Get live punch records
        punch_results = get_live_punch_records(conn)
        
        # Get employee summary
        summary_results = get_employee_summary(conn)
        
        # Final Summary
        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        print(f"📅 Today's Attendance Records: {len(today_results)}")
        print(f"📈 Recent Attendance Records (7 days): {len(recent_results)}")
        print(f"🔍 Recent Punch Records: {len(punch_results)}")
        print(f"👥 Active Employees (last 7 days): {len(summary_results)}")
        
        if today_results:
            print(f"⏰ Earliest IN time today: {min([r[2] for r in today_results if r[2]]).strftime('%H:%M:%S')}")
            print(f"⏰ Latest IN time today: {max([r[2] for r in today_results if r[2]]).strftime('%H:%M:%S')}")
        
        print("✅ Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
