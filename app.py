from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import pandas as pd
import webbrowser
import os

app = Flask(__name__)

db_url = "postgresql://postgres.ywwtoplpwtptbytgrkha:v0kNI4Pqp6h5Om1UuzuQmwaAHOcqeTsW@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

def get_data():
    conn = psycopg2.connect(db_url)
    df = pd.read_sql_query("SELECT * FROM box_data;", conn)
    conn.close()
    return df

@app.route('/')
def index():
    df = get_data()
    return render_template('index.html', data=df.to_dict(orient='records'))

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    df = get_data()
    results = df[df['box_name'].astype(str).str.contains(keyword, case=False, na=False)]
    return render_template('index.html', data=results.to_dict(orient='records'))

@app.route('/add', methods=['POST'])
def add():
    data = {key: request.form[key] for key in ['box_name', 'address', 'lng_lat', 'entry_method', 'source_type', 'remark']}
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO box_data (box_name, address, lng_lat, entry_method, source_type, remark)
                      VALUES (%s, %s, %s, %s, %s, %s)""", tuple(data.values()))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<box_name>', methods=['GET', 'POST'])
def edit(box_name):
    conn = psycopg2.connect(db_url)
    if request.method == 'POST':
        data = {key: request.form[key] for key in ['box_name', 'address', 'lng_lat', 'entry_method', 'source_type', 'remark']}
        cursor = conn.cursor()
        cursor.execute("""UPDATE box_data SET box_name=%s, address=%s, lng_lat=%s, entry_method=%s, source_type=%s, remark=%s
                          WHERE box_name=%s""", tuple(data.values()) + (box_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        df = pd.read_sql_query("SELECT * FROM box_data WHERE box_name = %s", conn, params=(box_name,))
        conn.close()
        return render_template('edit.html', data=df.iloc[0].to_dict())

@app.route('/delete/<box_name>', methods=['POST'])
def delete(box_name):
    password = request.form['password']
    if password == '9487':
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM box_data WHERE box_name = %s", (box_name,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/map/address/<address>')
def map_address(address):
    webbrowser.open(f"https://www.google.com/maps/search/{address}")
    return redirect(url_for('index'))

@app.route('/map/coordinates/<lng_lat>')
def map_coordinates(lng_lat):
    coords = lng_lat.replace(" ", "").replace("，", ",").split(",")
    if len(coords) == 2:
        webbrowser.open(f"https://www.google.com/maps?q={coords[0]},{coords[1]}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
