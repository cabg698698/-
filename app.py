from flask import Flask, render_template, request, jsonify
import psycopg2
import pandas as pd
import os

app = Flask(__name__)

db_url = "postgresql://postgres.ywwtoplpwtptbytgrkha:v0kNI4Pqp6h5Om1UuzuQmwaAHOcqeTsW@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

def get_data():
    conn = psycopg2.connect(db_url)
    df = pd.read_sql_query("SELECT * FROM box_data;", conn)
    conn.close()
    return df

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "").strip()
    print(keyword)
    df = get_data()
    results = df[df["box_name"].str.contains(keyword, case=False, na=False, regex=False)]
    print(results)
    return jsonify(results.to_dict(orient="records"))

@app.route("/add", methods=["POST"])
def add():
    data = request.json
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO box_data (box_name, address, lng_lat, entry_method, source_type, remark) VALUES (%s, %s, %s, %s, %s, %s)",
        (data["box_name"], data["address"], data["lng_lat"], data["entry_method"], data["source_type"], data["remark"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE box_data SET box_name=%s, address=%s, lng_lat=%s, entry_method=%s, source_type=%s, remark=%s WHERE box_name=%s",
        (data["box_name"], data["address"], data["lng_lat"], data["entry_method"], data["source_type"], data["remark"], data["original_box_name"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/delete", methods=["POST"])
def delete():
    data = request.json
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM box_data WHERE box_name = %s", (data["box_name"],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

