from flask import Flask, render_template,request
import json

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
    with open("data/prahar_kb.json") as f:
        kb = json.load(f)
    results = [x for x in kb if query.lower() in x["name"].lower()]
    return {"results": results}


if __name__ == "__main__":
    app.run(debug=True)