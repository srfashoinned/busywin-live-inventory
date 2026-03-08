import pyodbc
import pandas as pd
import json
from config import DB_CONFIG

print("Exporting BusyWin items...")

query = """
SELECT
 I.Name AS ItemName,
 I.Alias AS Barcode,
 ISNULL(I.D3,0) AS SalePrice,
 ISNULL(I.D2,0) AS MRP,
 ISNULL(I.D4,0) AS PurchasePrice
FROM Master1 I
WHERE I.MasterType = 6
"""

conn_str = ';'.join([f"{k}={v}" for k,v in DB_CONFIG.items()])

conn = pyodbc.connect(conn_str)

df = pd.read_sql(query, conn)

conn.close()

items = df.to_dict(orient="records")

with open("items.json","w") as f:
 json.dump(items,f,indent=2)

print("items.json created successfully")