import pyodbc
import pandas as pd
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

def get_employee_attendance_today(conn):
    """Get employee names and IN times for today"""
    try:
        cursor = conn.cursor()
        today = datetime.now().date()
        
        print(f"📅 Getting attendance for today: {today}")
        
        # Query to get employee names and IN times for today
        query = """
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status,
            al.Present,
            al.Absent,
            al.Duration,
            al.LateBy,
            al.EarlyBy
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE al.AttendanceDate = ?
            AND al.InTime != '1900-01-01 00:00:00'
        ORDER BY al.InTime ASC
        """
        
        cursor.execute(query, today)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Found {len(results)} attendance records for today:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'IN Time':<20} {'OUT Time':<20} {'Status':<10}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0]
                emp_code = row[1]
                in_time = row[3] if row[3] and row[3] != '1900-01-01 00:00:00' else "Not punched"
                out_time = row[4] if row[4] and row[4] != '1900-01-01 00:00:00' else "Not punched"
                status = row[5] or "N/A"
                
                # Format times
                if in_time != "Not punched":
                    in_time = in_time.strftime('%H:%M:%S') if hasattr(in_time, 'strftime') else str(in_time)
                if out_time != "Not punched":
                    out_time = out_time.strftime('%H:%M:%S') if hasattr(out_time, 'strftime') else str(out_time)
                
                print(f"{emp_name:<25} {emp_code:<8} {in_time:<20} {out_time:<20} {status:<10}")
        else:
            print("❌ No attendance records found for today")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting attendance data: {e}")
        return []

def get_employee_attendance_recent_days(conn, days=7):
    """Get employee names and IN times for recent days"""
    try:
        cursor = conn.cursor()
        
        # Get data for the last 'days' days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        print(f"\n📅 Getting attendance for last {days} days ({start_date} to {end_date})")
        
        query = """
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status,
            al.Present,
            al.Absent,
            al.Duration,
            al.LateBy
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE al.AttendanceDate BETWEEN ? AND ?
            AND al.InTime != '1900-01-01 00:00:00'
        ORDER BY al.AttendanceDate DESC, al.InTime ASC
        """
        
        cursor.execute(query, start_date, end_date)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Found {len(results)} attendance records for the last {days} days:")
            print("-" * 100)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'IN Time':<12} {'OUT Time':<12} {'Status':<10}")
            print("-" * 100)
            
            for row in results:
                emp_name = row[0]
                emp_code = row[1]
                att_date = row[2].strftime('%Y-%m-%d') if hasattr(row[2], 'strftime') else str(row[2])
                in_time = row[3] if row[3] and row[3] != '1900-01-01 00:00:00' else "Not punched"
                out_time = row[4] if row[4] and row[4] != '1900-01-01 00:00:00' else "Not punched"
                status = row[5] or "N/A"
                
                # Format times
                if in_time != "Not punched":
                    in_time = in_time.strftime('%H:%M:%S') if hasattr(in_time, 'strftime') else str(in_time)
                if out_time != "Not punched":
                    out_time = out_time.strftime('%H:%M:%S') if hasattr(out_time, 'strftime') else str(out_time)
                
                print(f"{emp_name:<25} {emp_code:<8} {att_date:<12} {in_time:<12} {out_time:<12} {status:<10}")
        else:
            print(f"❌ No attendance records found for the last {days} days")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting attendance data: {e}")
        return []

def get_live_device_logs(conn):
    """Get recent device logs (punch records)"""
    try:
        cursor = conn.cursor()
        
        # Get device logs from the current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Table name for current month
        table_name = f"DeviceLogs_{current_month}_{current_year}"
        
        print(f"\n🔍 Checking live device logs from {table_name}")
        
        query = f"""
        SELECT TOP 20
            e.EmployeeName,
            e.EmployeeCode,
            dl.LogDate,
            dl.AttDirection,
            dl.DeviceId,
            dl.UserId
        FROM {table_name} dl
        LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
        WHERE dl.LogDate >= ?
        ORDER BY dl.LogDate DESC
        """
        
        # Get logs from today
        today = datetime.now().date()
        cursor.execute(query, today)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Found {len(results)} recent device logs:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Log Time':<20} {'Direction':<10} {'Device':<8}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0] if row[0] else "Unknown"
                emp_code = row[1] if row[1] else row[5]  # Use device user ID if employee code not found
                log_time = row[2].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row[2], 'strftime') else str(row[2])
                direction = row[3] if row[3] else "N/A"
                device_id = row[4] if row[4] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {log_time:<20} {direction:<10} {device_id:<8}")
        else:
            print(f"❌ No recent device logs found in {table_name}")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting device logs: {e}")
        # Try with main DeviceLogs table
        try:
            query = """
            SELECT TOP 20
                e.EmployeeName,
                e.EmployeeCode,
                dl.LogDate,
                dl.AttDirection,
                dl.DeviceId,
                dl.UserId
            FROM DeviceLogs dl
            LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
            WHERE dl.LogDate >= ?
            ORDER BY dl.LogDate DESC
            """
            
            cursor.execute(query, datetime.now().date())
            results = cursor.fetchall()
            
            if results:
                print(f"\n📊 Found {len(results)} recent device logs from main table:")
                print("-" * 80)
                print(f"{'Employee Name':<25} {'Code':<8} {'Log Time':<20} {'Direction':<10} {'Device':<8}")
                print("-" * 80)
                
                for row in results:
                    emp_name = row[0] if row[0] else "Unknown"
                    emp_code = row[1] if row[1] else row[5]
                    log_time = row[2].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row[2], 'strftime') else str(row[2])
                    direction = row[3] if row[3] else "N/A"
                    device_id = row[4] if row[4] else "N/A"
                    
                    print(f"{emp_name:<25} {emp_code:<8} {log_time:<20} {direction:<10} {device_id:<8}")
            
            return results
            
        except Exception as e2:
            print(f"❌ Error getting device logs from main table: {e2}")
            return []

def get_employee_list(conn):
    """Get list of all employees"""
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT 
            EmployeeId,
            EmployeeName,
            EmployeeCode,
            EmployeeCodeInDevice,
            Department = (SELECT DepartmentName FROM Departments d WHERE d.DepartmentId = e.DepartmentId),
            Designation,
            Status,
            DOJ,
            ContactNo,
            Email
        FROM Employees e
        WHERE Status = 'Working'
        ORDER BY EmployeeName
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n👥 Found {len(results)} active employees:")
            print("-" * 100)
            print(f"{'Employee Name':<25} {'Code':<8} {'Device Code':<12} {'Department':<15} {'Designation':<15}")
            print("-" * 100)
            
            for row in results:
                emp_name = row[1] if row[1] else "N/A"
                emp_code = row[2] if row[2] else "N/A"
                device_code = row[3] if row[3] else "N/A"
                department = row[4] if row[4] else "N/A"
                designation = row[5] if row[5] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {device_code:<12} {department:<15} {designation:<15}")
        else:
            print("❌ No employees found")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting employee list: {e}")
        return []

def main():
    """Main function to run attendance queries"""
    print("🚀 Starting Employee Attendance Tracker")
    print("=" * 60)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Get employee list
        print("\n1️⃣ EMPLOYEE LIST")
        get_employee_list(conn)
        
        # Get today's attendance
        print("\n\n2️⃣ TODAY'S ATTENDANCE")
        get_employee_attendance_today(conn)
        
        # Get recent attendance (last 7 days)
        print("\n\n3️⃣ RECENT ATTENDANCE (LAST 7 DAYS)")
        get_employee_attendance_recent_days(conn, days=7)
        
        # Get live device logs
        print("\n\n4️⃣ RECENT DEVICE LOGS")
        get_live_device_logs(conn)
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
