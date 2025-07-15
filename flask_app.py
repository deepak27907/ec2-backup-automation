from flask import Flask ,request,jsonify
import shutil, os
from datetime import datetime

app = Flask(__name__)

os.makedirs("backups",exist_ok=True)

@app.route("/backup",methods=["POST"])
def backup():
    data = request.get_json()
    folder = data.get("folder")

    if not folder or not os.path.exists(folder):
        return jsonify({"error":"Folder not found"}), 400
    
    name = os.path.basename(folder.rstrip("/"))

    time = datetime.now().strftime("%Y%m%d_%H%M")

    zip_path = f"backups/{name}_{time}.zip"

    shutil.make_archive(zip_path.replace(".zip",""),"zip",folder)
    return jsonify({"message":"backup done", "file": zip_path})

app.run(host="0.0.0.0",port=5000)