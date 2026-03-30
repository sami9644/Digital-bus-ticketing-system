import os
from flask import Flask, render_template, abort,send_from_directory
from pathlib import Path

app = Flask(__name__)

# Base directory to start from
BASE_DIR = Path("C:/")

@app.route('/')
@app.route('/browse/<path:subpath>')
def browse(subpath=""):
    # Securely join the base path with the requested subpath
    # This prevents users from using "../../" to escape the C:/ drive
    requested_path = (BASE_DIR / subpath).resolve()

    if not str(requested_path).startswith(str(BASE_DIR)):
        return abort(403) # Forbidden

    if not requested_path.exists():
        return abort(404)

    try:
        # Separate directories and files for a better UI
        items = list(requested_path.iterdir())
        dirs = [d.name for d in items if d.is_dir()]
        files = [f.name for f in items if f.is_file()]
    except PermissionError:
        return "Access Denied to this folder.", 403

    return render_template('index.html', 
                           dirs=dirs, 
                           files=files, 
                           current_path=subpath)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    # Convert the string path back to a full system path
    full_path = (BASE_DIR / filepath).resolve()
    
    # Security check: ensure the file is still inside C:/
    if not str(full_path).startswith(str(BASE_DIR)) or not full_path.is_file():
        return abort(403)

    # send_from_directory needs the folder and the filename separately
    return send_from_directory(full_path.parent, full_path.name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)