import pyodbc
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_odbc_drivers():
    """Test what ODBC drivers are available and which ones work"""
    logger.info("🔍 Testing ODBC Database Connectivity")
    logger.info("=" * 50)
    
    # Get all available drivers
    drivers = [x for x in pyodbc.drivers()]
    logger.info(f"Available ODBC drivers: {drivers}")
    
    # Database connection parameters
    db_server = os.getenv('DB_SERVER', '1.22.45.168,19471')
    db_database = os.getenv('DB_DATABASE', 'etimetrackliteWEB')
    db_username = os.getenv('DB_USERNAME', 'sa')
    db_password = os.getenv('DB_PASSWORD', 'sa@123')
    
    # Test different connection configurations
    test_configs = [
        {
            'name': 'ODBC Driver 18 - No Encryption',
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;Encrypt=no;Connection Timeout=30;'
        },
        {
            'name': 'ODBC Driver 17 - No Encryption',
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;Encrypt=no;Connection Timeout=30;'
        },
        {
            'name': 'ODBC Driver 18 - Standard',
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;Encrypt=yes;Connection Timeout=30;'
        },
        {
            'name': 'ODBC Driver 17 - Standard',
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;Connection Timeout=30;'
        },
        {
            'name': 'SQL Server Native Client',
            'driver': 'SQL Server',
            'extra_params': 'Connection Timeout=30;'
        },
        {
            'name': 'FreeTDS',
            'driver': 'FreeTDS',
            'extra_params': 'TDS_Version=8.0;Port=19471;Connection Timeout=30;'
        }
    ]
    
    successful_configs = []
    
    for config in test_configs:
        if config['driver'] not in drivers:
            logger.info(f"⏭️  Skipping {config['name']} - driver not available")
            continue
            
        try:
            conn_str = (
                f"DRIVER={{{config['driver']}}};"
                f"SERVER={db_server};"
                f"DATABASE={db_database};"
                f"UID={db_username};"
                f"PWD={db_password};"
                f"{config['extra_params']}"
            )
            
            logger.info(f"Testing {config['name']}...")
            logger.info(f"Connection string: {conn_str.replace(db_password, '***')}")
            
            with pyodbc.connect(conn_str, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                logger.info(f"SUCCESS! {config['name']} - Result: {result}")
                successful_configs.append(config)
                
        except Exception as e:
            logger.error(f"❌ {config['name']} - FAILED: {str(e)}")
    
    # Write results to file
    with open('odbc_test_results.txt', 'w', encoding='utf-8') as f:
        f.write("ODBC Driver Test Results\n")
        f.write("=" * 30 + "\n")
        f.write(f"Available drivers: {', '.join(drivers)}\n\n")
        
        if successful_configs:
            f.write("SUCCESS - Successful configurations:\n")
            for i, config in enumerate(successful_configs, 1):
                f.write(f"{i}. {config['name']}\n")
                f.write(f"   Driver: {config['driver']}\n")
                f.write(f"   Extra params: {config['extra_params']}\n\n")
            
            # Write the best config for use by the main script
            best_config = successful_configs[0]
            f.write(f"RECOMMENDED_DRIVER={best_config['driver']}\n")
            f.write(f"RECOMMENDED_EXTRA_PARAMS={best_config['extra_params']}\n")
            
            logger.info(f"Found {len(successful_configs)} working configuration(s)")
            logger.info(f"Recommended: {best_config['name']}")
            return successful_configs[0]
        else:
            f.write("FAILED - No working configurations found!\n")
            logger.error("No working ODBC configuration found!")
            return None

if __name__ == "__main__":
    test_odbc_drivers()
