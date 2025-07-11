import pyodbc
from datetime import datetime, timedelta

# Database connection parameters
server = '1.22.45.168,19471'
database = 'etimetrackliteWEB'
username = 'sa'
password = 'sa@123'

conn_str = (
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

def format_date(date_obj):
    """Safely format date object"""
    if date_obj is None:
        return "N/A"
    if isinstance(date_obj, str):
        return date_obj
    try:
        return date_obj.strftime('%Y-%m-%d')
    except:
        return str(date_obj)

def format_time(time_obj):
    """Safely format time object"""
    if time_obj is None:
        return "N/A"
    if isinstance(time_obj, str):
        if time_obj == '1900-01-01 00:00:00':
            return "Not punched"
        return time_obj
    try:
        return time_obj.strftime('%H:%M:%S')
    except:
        return str(time_obj)

def main():
    """Main function to get employee names and IN times"""
    print("🚀 EMPLOYEE ATTENDANCE TRACKER")
    print("🔍 Finding Employee Names and IN Times")
    print("="*80)
    
    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to the database!")
        cursor = conn.cursor()
        
        # Get recent attendance from AttendanceLogs
        print("\n📊 RECENT ATTENDANCE RECORDS")
        print("="*80)
        
        query = """
        SELECT TOP 50
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE al.InTime != '1900-01-01 00:00:00'
            AND al.InTime IS NOT NULL
        ORDER BY al.AttendanceDate DESC, al.InTime DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"👥 Found {len(results)} recent attendance records:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'IN Time':<12} {'OUT Time':<12}")
            print("-" * 80)
            
            for row in results:
                emp_name = str(row[0])[:24] if row[0] else "N/A"
                emp_code = str(row[1]) if row[1] else "N/A"
                att_date = format_date(row[2])
                in_time = format_time(row[3])
                out_time = format_time(row[4])
                
                print(f"{emp_name:<25} {emp_code:<8} {att_date:<12} {in_time:<12} {out_time:<12}")
        else:
            print("❌ No recent attendance records found")
        
        # Get recent device logs (punch records)
        print("\n📊 RECENT PUNCH RECORDS (DEVICE LOGS)")
        print("="*80)
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        table_name = f"DeviceLogs_{current_month}_{current_year}"
        
        query = f"""
        SELECT TOP 30
            e.EmployeeName,
            e.EmployeeCode,
            dl.LogDate,
            dl.AttDirection,
            dl.DeviceId
        FROM {table_name} dl
        LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
        ORDER BY dl.LogDate DESC
        """
        
        cursor.execute(query)
        device_results = cursor.fetchall()
        
        if device_results:
            print(f"🔍 Found {len(device_results)} recent punch records:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'Time':<12} {'Direction':<10}")
            print("-" * 80)
            
            for row in device_results:
                emp_name = str(row[0])[:24] if row[0] else "Unknown"
                emp_code = str(row[1]) if row[1] else "N/A"
                log_date = format_date(row[2])
                log_time = format_time(row[2])
                direction = str(row[3]) if row[3] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {log_date:<12} {log_time:<12} {direction:<10}")
        else:
            print("❌ No recent punch records found")
        
        # Get specific employee examples
        print("\n📊 SAMPLE EMPLOYEE IN TIMES")
        print("="*80)
        
        # Get the employee with code '1' (Naveen Kumar Baid)
        query = """
        SELECT TOP 10
            e.EmployeeName,
            e.EmployeeCode,
            al.AttendanceDate,
            al.InTime,
            al.OutTime,
            al.Status
        FROM AttendanceLogs al
        INNER JOIN Employees e ON al.EmployeeId = e.EmployeeId
        WHERE e.EmployeeCode = '1'
            AND al.InTime != '1900-01-01 00:00:00'
            AND al.InTime IS NOT NULL
        ORDER BY al.AttendanceDate DESC
        """
        
        cursor.execute(query)
        sample_results = cursor.fetchall()
        
        if sample_results:
            print(f"👤 Sample records for Employee Code '1' (Naveen Kumar Baid):")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Date':<12} {'IN Time':<12} {'OUT Time':<12}")
            print("-" * 80)
            
            for row in sample_results:
                emp_name = str(row[0])[:24] if row[0] else "N/A"
                emp_code = str(row[1]) if row[1] else "N/A"
                att_date = format_date(row[2])
                in_time = format_time(row[3])
                out_time = format_time(row[4])
                
                print(f"{emp_name:<25} {emp_code:<8} {att_date:<12} {in_time:<12} {out_time:<12}")
        else:
            print("❌ No records found for Employee Code '1'")
        
        # Get unique employees with recent activity
        print("\n📊 EMPLOYEES WITH RECENT ACTIVITY")
        print("="*80)
        
        query = """
        SELECT DISTINCT
            e.EmployeeName,
            e.EmployeeCode,
            e.Status
        FROM Employees e
        WHERE e.Status = 'Working'
            AND EXISTS (
                SELECT 1 FROM AttendanceLogs al 
                WHERE al.EmployeeId = e.EmployeeId 
                    AND al.AttendanceDate >= DATEADD(day, -30, GETDATE())
            )
        ORDER BY e.EmployeeName
        """
        
        cursor.execute(query)
        active_employees = cursor.fetchall()
        
        if active_employees:
            print(f"👥 Found {len(active_employees)} employees with recent activity:")
            print("-" * 60)
            print(f"{'Employee Name':<30} {'Code':<10} {'Status':<10}")
            print("-" * 60)
            
            for row in active_employees[:20]:  # Show first 20
                emp_name = str(row[0])[:29] if row[0] else "N/A"
                emp_code = str(row[1]) if row[1] else "N/A"
                status = str(row[2]) if row[2] else "N/A"
                
                print(f"{emp_name:<30} {emp_code:<10} {status:<10}")
            
            if len(active_employees) > 20:
                print(f"... and {len(active_employees) - 20} more employees")
        else:
            print("❌ No employees found with recent activity")
        
        # Summary
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"📈 Recent Attendance Records: {len(results)}")
        print(f"🔍 Recent Punch Records: {len(device_results)}")
        print(f"👥 Active Employees (last 30 days): {len(active_employees)}")
        
        if results:
            print(f"📅 Latest Attendance Date: {format_date(results[0][2])}")
            print(f"⏰ Latest IN Time: {format_time(results[0][3])}")
        
        if device_results:
            print(f"🔍 Latest Punch Record: {format_date(device_results[0][2])} {format_time(device_results[0][2])}")
        
        print("\n✅ Analysis Complete!")
        print("💡 Key Findings:")
        print("   - The database contains attendance records from multiple employees")
        print("   - Recent punch records are available in device logs")
        print("   - Employee names and IN times can be extracted from AttendanceLogs table")
        print("   - JOIN with Employees table provides employee names for each record")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            conn.close()
            print("🔒 Database connection closed")
        except:
            pass

if __name__ == "__main__":
    main()
