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

# ─── Configuration ───────────────────────────────────────────────────────
CONFIG_PATH = "config.json"
UPLOAD_FOLDER = "shared"
ALLOWED_EXTS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "py", "csv"}
USERNAME = "admin"  # <<< change me
PASSWORD = "1234"  # <<< and me!

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── Basic Auth ────────────────────────────────────────────────


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


# ─── Config I/O ──────────────────────────────────────────────


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


# ─── Novel Extraction (READ NOW then next_chap links) ────────────────────────


def extract_chapter(start, end):
    chapters = []
    novel_title = ""

    base = "https://novelbin.com/b/reincarnated-as-an-energy-with-a-system-novel"
    scraper = cloudscraper.create_scraper()

    # Try to find true starting URL
    try:
        r0 = scraper.get(base)
        if r0.status_code == 200:
            soup0 = BeautifulSoup(r0.content, "html.parser")
            read_now = soup0.find("a", class_="btn btn-danger btn-read-now")
            current_url = (
                read_now["href"]
                if read_now and read_now.get("href")
                else f"{base}/chapter-{start}"
            )
        else:
            current_url = f"{base}/chapter-{start}"
    except:
        current_url = f"{base}/chapter-{start}"

    for _ in range(start, end + 1):
        try:
            r = scraper.get(current_url)
            if r.status_code != 200:
                chapters.append(f"<h2>Failed to load</h2><p>{current_url}</p>")
                break

            soup = BeautifulSoup(r.content, "html.parser")
            title_tag = soup.find("a", "novel-title")
            if title_tag:
                novel_title = title_tag.get_text(strip=True)

            heading = soup.find(["h2", "h3", "h4"])
            chap_title = heading.get_text(strip=True) if heading else "Untitled Chapter"

            body = soup.find("div", {"id": "chr-content"})
            paras = body.find_all("p") if body else []

            html = f"<h2>{chap_title}</h2>"
            # print(paras)

            if not paras:
                html += "<p>No content found.</p>"
            else:
                paras = paras[:-1]
                html += "".join(str(p) for p in paras)

            chapters.append(html)

            next_tag = soup.find("a", id="next_chap")
            if next_tag and next_tag.get("href"):
                current_url = next_tag["href"]
            else:
                break
        except Exception as e:
            chapters.append(f"<h2>Error</h2><p>{e}</p>")
            break

    return novel_title, chapters


# ─── File-Server Helpers ─────────────────────────────────────────


def allowed_file(fn):
    return "." in fn and fn.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


# ─── Routes ────────────────────────────────────────────


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


# ─── Start ────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(CONFIG_PATH):
        save_config(1, 10)
    app.run(host="0.0.0.0", port=5000, debug=True)
