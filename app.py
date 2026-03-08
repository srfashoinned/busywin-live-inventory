from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
import pyodbc
import pandas as pd
from config import DB_CONFIG
import io
import xlsxwriter
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.permanent_session_lifetime = timedelta(minutes=30)

# Admin credentials (change these)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout admin"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Home page"""
    items = get_items_data()
    is_admin = 'logged_in' in session
    return render_template('index.html', items=items, is_admin=is_admin)

@app.route('/export/excel')
@login_required
def export_excel():
    """Export to Excel (Admin only)"""
    items = get_items_data()
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Items')
    
    headers = ['Item Name', 'Alias', 'Group', 'Stock', 'MRP', 'Sale Price', 'Wholesale', 'Purchase Price']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    for row, item in enumerate(items, start=1):
        worksheet.write(row, 0, item['ItemName'])
        worksheet.write(row, 1, item['ItemAlias'] or '-')
        worksheet.write(row, 2, item['GroupName'] or '-')
        worksheet.write(row, 3, float(item['Stock']))
        worksheet.write(row, 4, float(item['Item_MRP']))
        worksheet.write(row, 5, float(item['Item_Sale_Price']))
        worksheet.write(row, 6, float(item['Item_Wholesale_Price']))
        worksheet.write(row, 7, float(item['Item_Purchase_Price']))
    
    workbook.close()
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='busywin_items.xlsx'
    )

@app.route('/api/item/<barcode>')
def get_item_by_barcode(barcode):
    """Find item by barcode"""
    items = get_items_data()
    
    for item in items:
        if barcode.lower() in item['ItemName'].lower() or barcode.lower() in str(item['ItemAlias'] or '').lower():
            is_admin = 'logged_in' in session
            return jsonify({'found': True, 'item': item, 'is_admin': is_admin})
    
    return jsonify({'found': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)