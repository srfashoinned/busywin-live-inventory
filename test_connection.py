import pyodbc
from config import DB_CONFIG

print("🔌 Testing connection to BusyComp0002_db...")
print("-" * 50)

try:
    # Build connection string
    conn_str = ';'.join([f"{k}={v}" for k, v in DB_CONFIG.items()])
    print(f"Connecting to: {DB_CONFIG['SERVER']}\\{DB_CONFIG['DATABASE']}")
    
    # Try to connect
    conn = pyodbc.connect(conn_str)
    print("✅ Connected successfully!")
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Master1 WHERE MasterType = 6")
    count = cursor.fetchone()[0]
    print(f"📊 Found {count} items in database")
    
    conn.close()
    print("✅ Test complete!")
    
except Exception as e:
    print("❌ Connection failed!")
    print(f"Error: {e}")