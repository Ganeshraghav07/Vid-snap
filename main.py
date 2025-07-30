import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# ------------------ ENV-DRIVEN PATHS & CONFIG ------------------
UPLOAD_FOLDER = os.getenv("UPLOAD_DIR", "user_uploads")        # e.g., /var/data/user_uploads on Render
OUTPUT_FOLDER = os.getenv("OUTPUT_DIR", "static/reels")        # e.g., /var/data/static/reels on Render
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 524288000))  # 500 MB

# Ensure folders exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ ROUTES ------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    """
    Form expectations:
      - Hidden field: uuid (job id)  -> value used as folder name
      - Multiple files: images[]     -> file inputs (or generic names)
      - Textarea/input: text         -> description for TTS
    """
    # Generate a new ID for GET (to show in form). For POST we read incoming id.
    myid = uuid.uuid1()

    if request.method == "POST":
        rec_id = request.form.get("uuid") or str(uuid.uuid4())
        desc = (request.form.get("text") or "").strip()

        job_dir = Path(app.config["UPLOAD_FOLDER"]) / rec_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save description ONCE
        (job_dir / "desc.txt").write_text(desc, encoding="utf-8")

        saved_files = []

        # Iterate over all uploaded files (works with images[] or generic keys)
        for _, file in request.files.items():
            if not file or not file.filename:
                continue
            if not allowed_file(file.filename):
                # skip unsupported files silently or flash a message
                # flash(f"Unsupported file type: {file.filename}", "error")
                continue

            filename = secure_filename(file.filename)
            save_path = job_dir / filename
            file.save(str(save_path))
            saved_files.append(filename)

        # Build/overwrite input.txt ONCE (one line per image, duration=1)
        input_txt = job_dir / "input.txt"
        if saved_files:
            lines = []
            for fl in saved_files:
                # If your worker expects only filenames (relative), keep as below.
                # If it needs absolute paths, use: lines.append(f"file '{(job_dir/fl).as_posix()}'")
                lines.append(f"file '{fl}'\nduration 1\n")
            input_txt.write_text("".join(lines), encoding="utf-8")

        # Optional user feedback
        # flash("Your reel request has been queued. Check the gallery shortly.", "success")
        return render_template("create.html", myid=myid)

    # GET
    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    """
    Lists generated MP4 files from OUTPUT_FOLDER.
    Your template likely builds URLs like /static/reels/<name>.
    If OUTPUT_FOLDER is outside /static, adjust template or expose a route.
    """
    out_dir = Path(OUTPUT_FOLDER)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        reels = [p.name for p in out_dir.glob("*.mp4")]
    except FileNotFoundError:
        reels = []

    # For your current templates: they likely do src="/static/reels/{{ reel }}"
    # So just pass the file names.
    return render_template("gallery.html", reels=reels)


import subprocess

if __name__ == "__main__":
    # Start generate_process.py in background
    subprocess.Popen(["python", "generate_process.py"])

    # Start the Flask app
    app.run(debug=True)


