from flask import Flask, render_template,request
import json
import sqlite3
from modules.m1_misinfo import analyze

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html",project_name="PRAHAR")

@app.route("/status")
def status():
    return {"module": "PRAHAR", "status": "online"}


@app.route("/search")
def search():
    query = request.args.get("q", "")
    conn = sqlite3.connect("database/prahar.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weapons 
        WHERE name LIKE ? OR type LIKE ? OR description LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()

    results = [
        {"id": r[0], "name": r[1], "type": r[2], "country": r[3], "description": r[4]}
        for r in rows
    ]
    return {"results": results}

@app.route("/api/analyze")
def api_analyze():
    text = request.args.get("text", "")
    if not text:
        return {"error": "No text provided"}, 400
    result = analyze(text)
    return result


if __name__ == "__main__":
    app.run(debug=True)