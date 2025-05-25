import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
URL_LIST = os.path.join(os.path.dirname(__file__), "chapters_full.json")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "shared")
ALLOWED_EXTS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "py", "csv"}
USERNAME = "admin"  # <<< change me
PASSWORD = "1234"  # <<< change me!

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"start": 1, "end": 10}
    try:
        with open(CONFIG_PATH) as f:
            c = json.load(f)
            return {"start": int(c.get("start", 1)), "end": int(c.get("end", 10))}
    except Exception:
        return {"start": 1, "end": 10}


def save_config(s, e):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"start": s, "end": e}, f)
