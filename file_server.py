import os
from flask import send_from_directory, render_template, redirect, url_for, request
from config import UPLOAD_FOLDER, ALLOWED_EXTS
from auth import requires_auth


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


def register_file_routes(app):
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
