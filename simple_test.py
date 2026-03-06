import pyodbc

print("Starting simple connection test...")

try:
    # Try Windows Authentication first
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-U5GLEE7;"
        "DATABASE=BusyComp0002_db;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    
    print(f"Connection string: {conn_str}")
    print("Attempting to connect...")
    
    conn = pyodbc.connect(conn_str)
    print("SUCCESS! Connected to database!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()
    print(f"SQL Server Version: {version[0][:50]}...")
    
    conn.close()
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    # Try to suggest fixes
    if "SQL Server" in str(e) and "exists" in str(e):
        print("\n🔧 TIP: Check if SQL Server is running")
    elif "login" in str(e).lower():
        print("\n🔧 TIP: Authentication failed - try different login method")
    elif "driver" in str(e).lower():
        print("\n🔧 TIP: ODBC Driver issue - list available drivers:")

print("\nTest complete.")