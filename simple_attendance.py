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
                emp_name = row[0][:24] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                att_date = row[2].strftime('%Y-%m-%d') if row[2] else "N/A"
                in_time = row[3].strftime('%H:%M:%S') if row[3] else "N/A"
                out_time = row[4].strftime('%H:%M:%S') if row[4] and str(row[4]) != '1900-01-01 00:00:00' else "Not Out"
                
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
        SELECT TOP 50
            e.EmployeeName,
            e.EmployeeCode,
            dl.LogDate,
            dl.AttDirection,
            dl.DeviceId
        FROM {table_name} dl
        LEFT JOIN Employees e ON dl.UserId = e.EmployeeCodeInDevice
        WHERE dl.LogDate >= DATEADD(day, -7, GETDATE())
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
                emp_name = row[0][:24] if row[0] else "Unknown"
                emp_code = row[1] if row[1] else "N/A"
                log_date = row[2].strftime('%Y-%m-%d') if row[2] else "N/A"
                log_time = row[2].strftime('%H:%M:%S') if row[2] else "N/A"
                direction = row[3] if row[3] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {log_date:<12} {log_time:<12} {direction:<10}")
        else:
            print("❌ No recent punch records found")
        
        # Get employees with their latest IN times
        print("\n📊 EMPLOYEES WITH LATEST IN TIMES")
        print("="*80)
        
        query = """
        SELECT 
            e.EmployeeName,
            e.EmployeeCode,
            MAX(al.AttendanceDate) as LastDate,
            MAX(CASE WHEN al.InTime != '1900-01-01 00:00:00' THEN al.InTime END) as LastInTime
        FROM Employees e
        LEFT JOIN AttendanceLogs al ON e.EmployeeId = al.EmployeeId
        WHERE e.Status = 'Working'
            AND al.AttendanceDate >= DATEADD(day, -30, GETDATE())
        GROUP BY e.EmployeeName, e.EmployeeCode
        HAVING MAX(CASE WHEN al.InTime != '1900-01-01 00:00:00' THEN al.InTime END) IS NOT NULL
        ORDER BY MAX(al.AttendanceDate) DESC
        """
        
        cursor.execute(query)
        latest_results = cursor.fetchall()
        
        if latest_results:
            print(f"👥 Found {len(latest_results)} employees with recent IN times:")
            print("-" * 80)
            print(f"{'Employee Name':<25} {'Code':<8} {'Last Date':<12} {'Last IN Time':<12}")
            print("-" * 80)
            
            for row in latest_results:
                emp_name = row[0][:24] if row[0] else "N/A"
                emp_code = row[1] if row[1] else "N/A"
                last_date = row[2].strftime('%Y-%m-%d') if row[2] else "N/A"
                last_in_time = row[3].strftime('%H:%M:%S') if row[3] else "N/A"
                
                print(f"{emp_name:<25} {emp_code:<8} {last_date:<12} {last_in_time:<12}")
        else:
            print("❌ No employees found with recent IN times")
        
        # Summary
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"📈 Recent Attendance Records: {len(results)}")
        print(f"🔍 Recent Punch Records: {len(device_results)}")
        print(f"👥 Employees with Recent IN Times: {len(latest_results)}")
        
        if results:
            print(f"📅 Latest Attendance Date: {results[0][2].strftime('%Y-%m-%d')}")
            print(f"⏰ Latest IN Time: {results[0][3].strftime('%H:%M:%S')}")
        
        if device_results:
            print(f"🔍 Latest Punch Record: {device_results[0][2].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("✅ Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            conn.close()
            print("🔒 Database connection closed")
        except:
            pass

if __name__ == "__main__":
    main()
