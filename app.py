from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
import requests
import io
import xlsxwriter
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.permanent_session_lifetime = timedelta(minutes=30)

# GitHub JSON source
GITHUB_JSON_URL = "https://raw.githubusercontent.com/srfashoinned/busywin-live-inventory/main/items.json"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_items_data():
    """Fetch items from GitHub JSON"""
    try:
        response = requests.get(GITHUB_JSON_URL)
        return response.json()
    except:
        return []


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    session.clear()
    return redirect(url_for('index'))


@app.route('/')
def index():
    items = get_items_data()
    is_admin = 'logged_in' in session
    return render_template('index.html', items=items, is_admin=is_admin)


@app.route('/export/excel')
@login_required
def export_excel():

    items = get_items_data()

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Items')

    headers = ['Item Name', 'Barcode', 'Sale Price', 'MRP', 'Purchase Price']

    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, item in enumerate(items, start=1):

        worksheet.write(row, 0, item.get('ItemName'))
        worksheet.write(row, 1, item.get('Barcode'))
        worksheet.write(row, 2, float(item.get('SalePrice',0)))
        worksheet.write(row, 3, float(item.get('MRP',0)))
        worksheet.write(row, 4, float(item.get('PurchasePrice',0)))

    workbook.close()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='busywin_items.xlsx'
    )


@app.route('/api/items')
def api_items():
    items = get_items_data()
    return jsonify(items)


@app.route('/api/item/<barcode>')
def get_item_by_barcode(barcode):

    items = get_items_data()

    for item in items:
        if barcode.lower() in item['ItemName'].lower() or barcode.lower() in str(item['Barcode']).lower():
            return jsonify({'found': True, 'item': item})

    return jsonify({'found': False})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)