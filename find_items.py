import pyodbc
from config import DB_CONFIG

print("🔍 Searching for item data...")
print("-" * 50)

try:
    conn_str = ';'.join([f"{k}={v}" for k, v in DB_CONFIG.items()])
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Try different possible table names for items
    possible_tables = [
        'Master1',
        'ITEMMASTER',
        'ItemMaster',
        'M_Item',
        'Item',
        'PRODUCT',
        'StockItem',
        'INVENTORY'
    ]
    
    for table_name in possible_tables:
        try:
            print(f"\nTrying table: {table_name}")
            cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                print(f"✅ SUCCESS! Found {len(rows)} rows in {table_name}")
                # Get column names
                columns = [column[0] for column in cursor.description]
                print(f"Columns: {columns[:10]}...")  # Show first 10 columns
                
                # Show first row as sample
                if rows:
                    print("Sample data:")
                    for i, col in enumerate(columns[:5]):  # Show first 5 columns
                        print(f"  {col}: {rows[0][i]}")
        except:
            print(f"❌ Table {table_name} not found or not accessible")
    
    conn.close()
    
except Exception as e:
    print(f"Connection error: {e}")