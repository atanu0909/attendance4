import pyodbc

# Database connection parameters
server = '1.22.45.168,19471'
database = 'etimetrackliteWEB'
username = 'sa'
password = 'sa@123'

conn_str = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'Encrypt=no;'
    'TrustServerCertificate=yes;'
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

def explore_tables(conn):
    """Explore available tables in the database"""
    try:
        cursor = conn.cursor()
        
        # Get all user tables (excluding system tables)
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_NAME NOT LIKE 'sys%'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        print("\n📋 Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return [table[0] for table in tables]
    except Exception as e:
        print("❌ Error exploring tables:", e)
        return []

def get_table_columns(conn, table_name):
    """Get column information for a specific table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Columns in '{table_name}':")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, Nullable: {col[2]})")
        
        return columns
    except Exception as e:
        print(f"❌ Error getting columns for {table_name}:", e)
        return []

def find_employee_attendance(conn):
    """Find employee names and IN times from attendance-related tables"""
    try:
        cursor = conn.cursor()
        
        # Common table names for attendance systems
        attendance_tables = [
            'Attendance', 'AttendanceLog', 'EmployeeAttendance', 
            'TimeLog', 'PunchData', 'CheckInOut', 'AttendanceRecord'
        ]
        
        employee_tables = [
            'Employee', 'Employees', 'Staff', 'Personnel', 'Users'
        ]
        
        # First, let's see what tables exist
        all_tables = explore_tables(conn)
        
        # Look for attendance-related tables
        found_attendance_tables = []
        found_employee_tables = []
        
        for table in all_tables:
            table_lower = table.lower()
            if any(att_table.lower() in table_lower for att_table in attendance_tables):
                found_attendance_tables.append(table)
            elif any(emp_table.lower() in table_lower for emp_table in employee_tables):
                found_employee_tables.append(table)
        
        print(f"\n🔍 Found potential attendance tables: {found_attendance_tables}")
        print(f"🔍 Found potential employee tables: {found_employee_tables}")
        
        # Examine the structure of found tables
        for table in found_attendance_tables[:3]:  # Limit to first 3 tables
            print(f"\n--- Examining {table} ---")
            get_table_columns(conn, table)
            
            # Try to get a sample of data
            try:
                cursor.execute(f"SELECT TOP 5 * FROM {table}")
                rows = cursor.fetchall()
                if rows:
                    print(f"📝 Sample data from {table}:")
                    for row in rows:
                        print(f"  {row}")
            except Exception as e:
                print(f"❌ Error getting sample data from {table}: {e}")
        
        for table in found_employee_tables[:3]:  # Limit to first 3 tables
            print(f"\n--- Examining {table} ---")
            get_table_columns(conn, table)
            
            # Try to get a sample of data
            try:
                cursor.execute(f"SELECT TOP 5 * FROM {table}")
                rows = cursor.fetchall()
                if rows:
                    print(f"📝 Sample data from {table}:")
                    for row in rows:
                        print(f"  {row}")
            except Exception as e:
                print(f"❌ Error getting sample data from {table}: {e}")
        
        return found_attendance_tables, found_employee_tables
        
    except Exception as e:
        print("❌ Error finding employee attendance:", e)
        return [], []

def main():
    """Main function to run the attendance query"""
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Find and analyze attendance tables
        attendance_tables, employee_tables = find_employee_attendance(conn)
        
        print("\n" + "="*50)
        print("📊 ANALYSIS COMPLETE")
        print("="*50)
        
        if attendance_tables:
            print(f"✅ Found {len(attendance_tables)} attendance-related tables")
        else:
            print("❌ No obvious attendance tables found")
            
        if employee_tables:
            print(f"✅ Found {len(employee_tables)} employee-related tables")
        else:
            print("❌ No obvious employee tables found")
            
    except Exception as e:
        print("❌ Error in main execution:", e)
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
