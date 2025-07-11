import pyodbc
import pandas as pd
from datetime import datetime
import os

# Database connection parameters (using the working connection from final_attendance.py)
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

def get_db_connection():
    """Get database connection"""
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_device_19_in_times():
    """Get IN times for specific employees from device 19 today"""
    # Employee codes to check
    employee_codes = ['3', '595', '593', '695', '641', '744', '20', '18']
    employee_codes_str = "', '".join(employee_codes)
    
    # Today's date
    today = datetime.now().strftime('%Y-%m-%d')
    current_dt = datetime.now()
    month_year = f"{current_dt.month}_{current_dt.year}"
    
    print(f"=== Device 19 IN Times for {today} ===")
    print(f"Checking employees: {', '.join(employee_codes)}")
    print(f"Using table: DeviceLogs_{month_year}")
    print("="*60)
    
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return
    
    try:
        # Query to get all punch records from device 19 for today
        query = f"""
        SELECT 
            CAST(dl.UserId as varchar) as EmployeeCode,
            dl.LogDate,
            dl.DeviceId,
            e.EmployeeName
        FROM dbo.DeviceLogs_{month_year} dl
        LEFT JOIN dbo.Employees e ON CAST(e.EmployeeCode as varchar) = CAST(dl.UserId as varchar)
        WHERE CAST(dl.LogDate as DATE) = '{today}'
            AND dl.DeviceId = 19
            AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
        ORDER BY CAST(dl.UserId as varchar), dl.LogDate
        """
        
        print(f"Executing query for device 19 records...")
        df = pd.read_sql(query, connection)
        
        if df.empty:
            print("No records found for the specified employees on device 19 today.")
            
            # Let's check if there are any records on device 19 at all today
            check_query = f"""
            SELECT COUNT(*) as RecordCount
            FROM dbo.DeviceLogs_{month_year}
            WHERE CAST(LogDate as DATE) = '{today}'
                AND DeviceId = 19
            """
            
            check_df = pd.read_sql(check_query, connection)
            total_records = check_df.iloc[0]['RecordCount']
            print(f"Total records on device 19 today: {total_records}")
            
            # Check if these employees have records on any device today
            any_device_query = f"""
            SELECT 
                CAST(dl.UserId as varchar) as EmployeeCode,
                dl.LogDate,
                dl.DeviceId,
                e.EmployeeName
            FROM dbo.DeviceLogs_{month_year} dl
            LEFT JOIN dbo.Employees e ON CAST(e.EmployeeCode as varchar) = CAST(dl.UserId as varchar)
            WHERE CAST(dl.LogDate as DATE) = '{today}'
                AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
            ORDER BY CAST(dl.UserId as varchar), dl.LogDate
            """
            
            any_device_df = pd.read_sql(any_device_query, connection)
            
            if not any_device_df.empty:
                print(f"\nHowever, these employees have records on other devices today:")
                print("-" * 80)
                for _, row in any_device_df.iterrows():
                    emp_name = row['EmployeeName'] if pd.notna(row['EmployeeName']) else "Unknown"
                    print(f"Code: {row['EmployeeCode']:<4} | Name: {emp_name:<25} | Device: {row['DeviceId']:<3} | Time: {row['LogDate']}")
                    
                # Get first punch for each employee from any device
                print(f"\nFirst IN time for each employee from ANY device today:")
                print("-" * 80)
                
                first_punches = any_device_df.groupby('EmployeeCode')['LogDate'].min().reset_index()
                first_punches = first_punches.merge(
                    any_device_df[['EmployeeCode', 'EmployeeName', 'DeviceId', 'LogDate']],
                    on=['EmployeeCode', 'LogDate'],
                    how='left'
                )
                
                for _, row in first_punches.iterrows():
                    emp_name = row['EmployeeName'] if pd.notna(row['EmployeeName']) else "Unknown"
                    in_time = row['LogDate'].strftime('%H:%M:%S')
                    print(f"Code: {row['EmployeeCode']:<4} | Name: {emp_name:<25} | First IN: {in_time} | Device: {row['DeviceId']}")
            else:
                print("No records found for these employees on any device today.")
            
        else:
            print(f"Found {len(df)} records from device 19:")
            print("-" * 80)
            
            # Display all records
            for _, row in df.iterrows():
                emp_name = row['EmployeeName'] if pd.notna(row['EmployeeName']) else "Unknown"
                punch_time = row['LogDate'].strftime('%H:%M:%S')
                print(f"Code: {row['EmployeeCode']:<4} | Name: {emp_name:<25} | Time: {punch_time} | Device: {row['DeviceId']}")
            
            print("\nFirst IN time for each employee from device 19:")
            print("-" * 80)
            
            # Get first punch for each employee from device 19
            first_punches = df.groupby('EmployeeCode')['LogDate'].min().reset_index()
            first_punches = first_punches.merge(
                df[['EmployeeCode', 'EmployeeName', 'DeviceId', 'LogDate']],
                on=['EmployeeCode', 'LogDate'],
                how='left'
            )
            
            for _, row in first_punches.iterrows():
                emp_name = row['EmployeeName'] if pd.notna(row['EmployeeName']) else "Unknown"
                in_time = row['LogDate'].strftime('%H:%M:%S')
                print(f"Code: {row['EmployeeCode']:<4} | Name: {emp_name:<25} | First IN: {in_time}")
            
            # Check which employees haven't punched on device 19
            punched_codes = set(df['EmployeeCode'].unique())
            not_punched = set(employee_codes) - punched_codes
            
            if not_punched:
                print(f"\nEmployees who haven't punched on device 19 today:")
                print("-" * 50)
                for code in not_punched:
                    print(f"Code: {code}")
        
        # Summary
        print("\n" + "="*60)
        print(f"Summary for Device 19 on {today}:")
        print(f"- Total employees checked: {len(employee_codes)}")
        if not df.empty:
            unique_employees = len(df['EmployeeCode'].unique())
            print(f"- Employees with records on device 19: {unique_employees}")
            print(f"- Total punch records from device 19: {len(df)}")
        else:
            print(f"- Employees with records on device 19: 0")
        print("="*60)
        
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    get_device_19_in_times()
