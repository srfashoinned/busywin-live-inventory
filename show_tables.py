import pyodbc
from config import DB_CONFIG

print("🔍 Looking for tables in BusyComp0002_db...")
print("-" * 50)

try:
    conn_str = ';'.join([f"{k}={v}" for k, v in DB_CONFIG.items()])
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Query to get all tables
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    print(f"Found {len(tables)} tables:\n")
    
    for schema, table in tables:
        print(f"📊 {schema}.{table}")
        
        # Check if this might be our items table
        if 'MASTER' in table.upper() or 'ITEM' in table.upper():
            print(f"   👆 Possible items table!")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")