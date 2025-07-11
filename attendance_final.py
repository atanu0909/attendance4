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
            DepartmentId,
            Designation,
            Status,
            DOJ,
            ContactNo,
            Email
        FROM Employees
        WHERE Status = 'Working'
        ORDER BY EmployeeName
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n👥 Found {len(results)} active employees:")
            print("-" * 100)
            print(f"{'Employee Name':<25} {'Code':<8} {'Device Code':<12} {'Dept ID':<8} {'Designation':<15} {'Status':<10}")
            print("-" * 100)
            
            for row in results:
                emp_id = row[0] if row[0] else "N/A"
                emp_name = row[1] if row[1] else "N/A"
                emp_code = row[2] if row[2] else "N/A"
                device_code = row[3] if row[3] else "N/A"
                dept_id = row[4] if row[4] else "N/A"
                designation = row[5] if row[5] else "N/A"
                status = row[6] if row[6] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {device_code:<12} {str(dept_id):<8} {designation:<15} {status:<10}")
        else:
            print("❌ No employees found")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting employee list: {e}")
        return []

def get_employee_attendance_today(conn):
    """Get employee names and IN times for today"""
    try:
        cursor = conn.cursor()
        today = datetime.now().date()
        today_str = today.strftime('%Y-%m-%d')
        
        print(f"📅 Getting attendance for today: {today_str}")
        
        # Query to get employee names and IN times for today
        query = f"""
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
        WHERE al.AttendanceDate = '{today_str}'
            AND al.InTime != '1900-01-01 00:00:00'
        ORDER BY al.InTime ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Found {len(results)} attendance records for today:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'IN Time':<20} {'OUT Time':<20} {'Status':<10}")
            print("-" * 80)
            
            for row in results:
                emp_name = row[0] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                in_time = row[3] if row[3] and str(row[3]) != '1900-01-01 00:00:00' else "Not punched"
                out_time = row[4] if row[4] and str(row[4]) != '1900-01-01 00:00:00' else "Not punched"
                status = row[5] if row[5] else "N/A"
                
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

def get_employee_attendance_recent_days(conn, days=3):
    """Get employee names and IN times for recent days"""
    try:
        cursor = conn.cursor()
        
        # Get data for the last 'days' days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n📅 Getting attendance for last {days} days ({start_str} to {end_str})")
        
        query = f"""
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
        WHERE al.AttendanceDate BETWEEN '{start_str}' AND '{end_str}'
            AND al.InTime != '1900-01-01 00:00:00'
        ORDER BY al.AttendanceDate DESC, al.InTime ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Found {len(results)} attendance records for the last {days} days:")
            print("-" * 100)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'IN Time':<12} {'OUT Time':<12} {'Status':<10}")
            print("-" * 100)
            
            for row in results:
                emp_name = row[0] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                att_date = row[2].strftime('%Y-%m-%d') if hasattr(row[2], 'strftime') else str(row[2])
                in_time = row[3] if row[3] and str(row[3]) != '1900-01-01 00:00:00' else "Not punched"
                out_time = row[4] if row[4] and str(row[4]) != '1900-01-01 00:00:00' else "Not punched"
                status = row[5] if row[5] else "N/A"
                
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
        
        today_str = datetime.now().date().strftime('%Y-%m-%d')
        
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
        WHERE dl.LogDate >= '{today_str}'
        ORDER BY dl.LogDate DESC
        """
        
        cursor.execute(query)
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
                
                print(f"{emp_name:<25} {str(emp_code):<8} {log_time:<20} {direction:<10} {str(device_id):<8}")
        else:
            print(f"❌ No recent device logs found in {table_name}")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting device logs: {e}")
        # Try with main DeviceLogs table
        try:
            query = f"""
            SELECT TOP 20
                e.EmployeeName,
                e.EmployeeCode,
                dl.LogDate,
                dl.AttDirection,
                dl.DeviceId,
                dl.UserId
            FROM DeviceLogs dl
            LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
            WHERE dl.LogDate >= '{today_str}'
            ORDER BY dl.LogDate DESC
            """
            
            cursor.execute(query)
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
                    
                    print(f"{emp_name:<25} {str(emp_code):<8} {log_time:<20} {direction:<10} {str(device_id):<8}")
            
            return results
            
        except Exception as e2:
            print(f"❌ Error getting device logs from main table: {e2}")
            return []

def get_specific_employee_attendance(conn, employee_code):
    """Get attendance for a specific employee"""
    try:
        cursor = conn.cursor()
        
        # Get last 10 days of attendance for this employee
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=10)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status,
            al.Duration,
            al.LateBy,
            al.EarlyBy,
            al.Present,
            al.Absent
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE e.EmployeeCode = '{employee_code}'
            AND al.AttendanceDate BETWEEN '{start_str}' AND '{end_str}'
        ORDER BY al.AttendanceDate DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Last 10 days attendance for Employee Code: {employee_code}")
            print("-" * 100)
            print(f"{'Employee Name':<25} {'Date':<12} {'IN Time':<12} {'OUT Time':<12} {'Status':<10} {'Duration':<10}")
            print("-" * 100)
            
            for row in results:
                emp_name = row[0] if row[0] else "N/A"
                att_date = row[2].strftime('%Y-%m-%d') if hasattr(row[2], 'strftime') else str(row[2])
                in_time = row[3] if row[3] and str(row[3]) != '1900-01-01 00:00:00' else "Not punched"
                out_time = row[4] if row[4] and str(row[4]) != '1900-01-01 00:00:00' else "Not punched"
                status = row[5] if row[5] else "N/A"
                duration = row[6] if row[6] else "N/A"
                
                # Format times
                if in_time != "Not punched":
                    in_time = in_time.strftime('%H:%M:%S') if hasattr(in_time, 'strftime') else str(in_time)
                if out_time != "Not punched":
                    out_time = out_time.strftime('%H:%M:%S') if hasattr(out_time, 'strftime') else str(out_time)
                
                print(f"{emp_name:<25} {att_date:<12} {in_time:<12} {out_time:<12} {status:<10} {str(duration):<10}")
        else:
            print(f"❌ No attendance records found for employee code: {employee_code}")
            
        return results
        
    except Exception as e:
        print(f"❌ Error getting specific employee attendance: {e}")
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
        employees = get_employee_list(conn)
        
        # Get today's attendance
        print("\n\n2️⃣ TODAY'S ATTENDANCE")
        today_attendance = get_employee_attendance_today(conn)
        
        # Get recent attendance (last 3 days)
        print("\n\n3️⃣ RECENT ATTENDANCE (LAST 3 DAYS)")
        recent_attendance = get_employee_attendance_recent_days(conn, days=3)
        
        # Get live device logs
        print("\n\n4️⃣ RECENT DEVICE LOGS")
        device_logs = get_live_device_logs(conn)
        
        # Get specific employee attendance (example with employee code '1')
        print("\n\n5️⃣ SPECIFIC EMPLOYEE ATTENDANCE (CODE: 1)")
        specific_attendance = get_specific_employee_attendance(conn, '1')
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print(f"📊 Total Active Employees: {len(employees) if employees else 0}")
        print(f"📅 Today's Attendance Records: {len(today_attendance) if today_attendance else 0}")
        print(f"📈 Recent Attendance Records: {len(recent_attendance) if recent_attendance else 0}")
        print(f"🔍 Recent Device Logs: {len(device_logs) if device_logs else 0}")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
