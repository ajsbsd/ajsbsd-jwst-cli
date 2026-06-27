# server.py  (put this in /home/aaron/ajsbsd-jwst-cli/)
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess, sys

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    cmd = [sys.executable, "main.py", "--no-color"]
    if data.get("ping"):
        return jsonify({"status": "ok"}) 
    if data.get("seed"):
        cmd += ["--seed", str(data["seed"])]
    if data.get("verbose"):
        cmd.append("--verbose")
    for k, v in (data.get("meters") or {}).items():
        cmd += ["--set-meter", f"{k}={v}"]
    for ev in (data.get("events") or []):
        cmd += ["--force-event", ev]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/aaron/ajsbsd-jwst-cli")
    return jsonify({"output": result.stdout or result.stderr})

app.run(port=5050)
