from flask import Flask, request, render_template
from auth import requires_auth
from config import load_config, save_config, URL_LIST, CONFIG_PATH
from scraper import extract_chapter
from file_server import register_file_routes
from url_extractor import build_url
import os


def create_app():
    app = Flask(__name__)
    register_file_routes(app)

    @app.route("/")
    @requires_auth
    def nav_page():
        return render_template("nav.html")

    @app.route("/novel", methods=["GET", "POST"])
    @requires_auth
    def novel_index():
        cfg = load_config()
        start, end = cfg["start"], cfg["end"]
        chapters, novel_title = [], ""

        if request.method == "POST":
            try:
                start = int(request.form.get("start", start))
                end = int(request.form.get("end", end))
                novel_title, chapters = extract_chapter(
                    start, end, "chapters_full.json"
                )
                save_config(start, end)
            except ValueError:
                chapters = ["<p>Invalid input. Please enter numbers.</p>"]

        return render_template(
            "index.html",
            novel_title=novel_title,
            chapters=chapters,
            start=start,
            end=end,
        )

    return app


if __name__ == "__main__":
    if not os.path.exists(URL_LIST):
        build_url()
    app = create_app()

    if not os.path.exists(CONFIG_PATH):
        save_config(1, 10)
    app.run(host="0.0.0.0", port=5000, debug=True)
