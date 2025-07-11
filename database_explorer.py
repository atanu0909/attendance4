import pyodbc

# Database connection parameters
server = '1.22.45.168,19471'
database = 'etimetrackliteWEB'
username = 'sa'
password = 'sa@123'

def try_different_drivers():
    """Try different ODBC drivers to find one that works"""
    drivers = [
        'DRIVER={ODBC Driver 18 for SQL Server};',
        'DRIVER={ODBC Driver 17 for SQL Server};',
        'DRIVER={SQL Server Native Client 11.0};',
        'DRIVER={SQL Server};'
    ]
    
    for driver in drivers:
        conn_str = (
            driver +
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            'Encrypt=no;'
            'TrustServerCertificate=yes;'
        )
        
        try:
            print(f"🔧 Trying driver: {driver}")
            conn = pyodbc.connect(conn_str)
            print(f"✅ Successfully connected with: {driver}")
            return conn, driver
        except Exception as e:
            print(f"❌ Failed with {driver}: {e}")
            continue
    
    print("❌ No working ODBC driver found")
    return None, None

def list_available_drivers():
    """List all available ODBC drivers"""
    try:
        drivers = pyodbc.drivers()
        print("📋 Available ODBC drivers:")
        for driver in drivers:
            print(f"  - {driver}")
        return drivers
    except Exception as e:
        print(f"❌ Error listing drivers: {e}")
        return []

def main():
    """Main function"""
    print("🔍 Checking available ODBC drivers...")
    available_drivers = list_available_drivers()
    
    if not available_drivers:
        print("\n❌ No ODBC drivers found. Please install Microsoft ODBC Driver for SQL Server")
        print("Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        return
    
    print("\n🔧 Attempting to connect to database...")
    conn, working_driver = try_different_drivers()
    
    if conn:
        try:
            print("\n📊 Exploring database structure...")
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            tables = cursor.fetchall()
            print(f"\n📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Look for attendance-related tables
            attendance_keywords = ['attendance', 'punch', 'time', 'log', 'checkin', 'checkout']
            employee_keywords = ['employee', 'staff', 'user', 'person']
            
            print("\n🔍 Searching for attendance-related tables...")
            for table in tables:
                table_name = table[0].lower()
                if any(keyword in table_name for keyword in attendance_keywords):
                    print(f"  📅 Potential attendance table: {table[0]}")
                    
                    # Get column info
                    try:
                        cursor.execute(f"""
                            SELECT COLUMN_NAME, DATA_TYPE
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = '{table[0]}'
                            ORDER BY ORDINAL_POSITION
                        """)
                        columns = cursor.fetchall()
                        print(f"    Columns: {', '.join([col[0] for col in columns])}")
                        
                        # Try to get sample data
                        cursor.execute(f"SELECT TOP 3 * FROM {table[0]}")
                        sample_data = cursor.fetchall()
                        if sample_data:
                            print(f"    Sample data (first 3 rows):")
                            for row in sample_data:
                                print(f"      {row}")
                    except Exception as e:
                        print(f"    ❌ Error exploring {table[0]}: {e}")
            
            print("\n🔍 Searching for employee-related tables...")
            for table in tables:
                table_name = table[0].lower()
                if any(keyword in table_name for keyword in employee_keywords):
                    print(f"  👤 Potential employee table: {table[0]}")
                    
                    # Get column info
                    try:
                        cursor.execute(f"""
                            SELECT COLUMN_NAME, DATA_TYPE
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = '{table[0]}'
                            ORDER BY ORDINAL_POSITION
                        """)
                        columns = cursor.fetchall()
                        print(f"    Columns: {', '.join([col[0] for col in columns])}")
                        
                        # Try to get sample data
                        cursor.execute(f"SELECT TOP 3 * FROM {table[0]}")
                        sample_data = cursor.fetchall()
                        if sample_data:
                            print(f"    Sample data (first 3 rows):")
                            for row in sample_data:
                                print(f"      {row}")
                    except Exception as e:
                        print(f"    ❌ Error exploring {table[0]}: {e}")
            
        except Exception as e:
            print(f"❌ Error exploring database: {e}")
        finally:
            conn.close()
            print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
