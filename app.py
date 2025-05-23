import os
import json
import cloudscraper
from bs4 import BeautifulSoup
from functools import wraps
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    send_from_directory,
    render_template,
    abort,
    Response,
)

app = Flask(__name__)

# ─── Configuration ─────────────────────────────────────────────────────────────
CONFIG_PATH = "config.json"
UPLOAD_FOLDER = "shared"
ALLOWED_EXTS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "py", "csv"}
USERNAME = "admin"  # <<< change me
PASSWORD = "1234"  # <<< and me!

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── Basic Auth ────────────────────────────────────────────────────────────────
def check_auth(u, p):
    return u == USERNAME and p == PASSWORD


def authenticate():
    return Response(
        "Authentication required",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return wrapper


# ─── Config I/O ────────────────────────────────────────────────────────────────
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"start": 1, "end": 10}
    try:
        with open(CONFIG_PATH) as f:
            c = json.load(f)
            return {"start": int(c.get("start", 1)), "end": int(c.get("end", 10))}
    except:
        return {"start": 1, "end": 10}


def save_config(s, e):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"start": s, "end": e}, f)


# ─── Novel Extraction ─────────────────────────────────────────────────────────
def extract_chapter(start, end):
    chapters = []
    novel_title = ""
    if start > end:
        end = start + 1

    for i in range(start, end + 1):
        try:
            scraper = cloudscraper.create_scraper()
            url = f"https://novelbin.com/b/infinite-mana-in-the-apocalypse/chapter-{i}"
            r = scraper.get(url)
            if r.status_code != 200:
                chapters.append(f"<h2>Chapter {i}</h2><p>Failed to load.</p>")
                continue

            soup = BeautifulSoup(r.content, "html.parser")
            tt = soup.find("a", "novel-title")
            if tt:
                novel_title = tt.get_text(strip=True)

            heading = soup.find(["h2", "h3", "h4"])
            title = heading.get_text(strip=True) if heading else f"Chapter {i}"
            body = soup.find("div", {"id": "chr-content"})
            ps = body.find_all("p") if body else []

            html = f"<h2>{title}</h2>"
            for p in ps:
                t = p.get_text(strip=True)
                if not t or any(
                    skip in t
                    for skip in ["Enhance your reading", "Translator:", "______"]
                ):
                    continue
                html += f"<p>{t}</p>"
            if not ps:
                html += "<p>No content found.</p>"

            chapters.append(html)
        except Exception as e:
            chapters.append(f"<h2>Chapter {i}</h2><p>Error: {e}</p>")
    return novel_title, chapters


# ─── File-Server Helpers ────────────────────────────────────────────────────────
def allowed_file(fn):
    return "." in fn and fn.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


# ─── Routes ────────────────────────────────────────────────────────────────────


@app.route("/novel", methods=["GET", "POST"])
@requires_auth
def index():
    cfg = load_config()
    start, end = cfg["start"], cfg["end"]
    chapters, novel_title = [], ""

    if request.method == "POST":
        try:
            start = int(request.form.get("start", start))
            end = int(request.form.get("end", end))
            novel_title, chapters = extract_chapter(start, end)
            save_config(start, end)
        except ValueError:
            chapters = ["<p>Invalid input. Please enter numbers.</p>"]

    return render_template(
        "index.html", novel_title=novel_title, chapters=chapters, start=start, end=end
    )


@app.route("/files/")
@requires_auth
def list_files():
    items = os.listdir(UPLOAD_FOLDER)
    return render_template("files.html", files=items)


@app.route("/files/<path:filename>")
@requires_auth
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
@requires_auth
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "<p>No file part.</p>"
        f = request.files["file"]
        if f.filename == "":
            return "<p>No selected file.</p>"
        if f and allowed_file(f.filename):
            dest = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(dest)
            return redirect(url_for("list_files"))
    return render_template("upload.html")


@app.route("/")
@requires_auth
def nav_page():
    return render_template("nav.html")


# ─── Start ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(CONFIG_PATH):
        save_config(1, 10)
    app.run(host="0.0.0.0", port=5000, debug=True)
