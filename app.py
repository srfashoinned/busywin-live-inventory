from flask import Flask, render_template, jsonify
import pyodbc
import pandas as pd
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    """Create database connection"""
    try:
        conn_str = ';'.join([f"{k}={v}" for k, v in DB_CONFIG.items()])
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def get_items_data():
    """Fetch items data using your query"""
    query = """
    SELECT
      I.Name                                   AS ItemName,
      I.Alias                                  AS ItemAlias,
      G.Name                                   AS GroupName,
      ISNULL(I.D2, 0)                          AS Item_MRP,
      ISNULL(I.D3, 0)                          AS Item_Sale_Price,
      ISNULL(I.D4, 0)                          AS Item_Purchase_Price,
      COALESCE(NULLIF(I.D9, 0), OV.OpenValPerUnit, 0) AS Item_Wholesale_Price,
      ISNULL(SQ.Stock, 0)                      AS Stock
    FROM Master1 I
    LEFT JOIN Master1 G
      ON I.ParentGrp = G.Code AND G.MasterType = 5
    LEFT JOIN (
      SELECT T4.MasterCode1 AS ItemCode,
             SUM(T4.D1) AS OpenQty,
             SUM(T4.D2) AS OpenValue,
             CASE WHEN SUM(T4.D1) <> 0 THEN SUM(T4.D2) / SUM(T4.D1) ELSE 0 END AS OpenValPerUnit
      FROM Tran4 T4
      GROUP BY T4.MasterCode1
    ) OV
      ON OV.ItemCode = I.Code
    LEFT JOIN (
      SELECT T2.MasterCode1 AS ItemCode,
             SUM(CASE WHEN T2.TranType IN (0,1) THEN T2.Value1 ELSE -T2.Value1 END) AS Stock
      FROM Tran2 T2
      GROUP BY T2.MasterCode1
    ) SQ
      ON SQ.ItemCode = I.Code
    WHERE I.MasterType = 6
    ORDER BY I.Name
    """
    
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df.to_dict('records')
        except Exception as e:
            print(f"Query error: {e}")
            return []
    return []

@app.route('/')
def index():
    """Home page - displays the items"""
    items = get_items_data()
    return render_template('index.html', items=items)

@app.route('/api/items')
def api_items():
    """API endpoint to get items as JSON"""
    items = get_items_data()
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)