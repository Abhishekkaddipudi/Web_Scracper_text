import os
import json
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

# where we store our last-used range
CONFIG_PATH = "config.json"


def load_config():
    """Read start/end from JSON, or return defaults if file missing or corrupt."""
    if not os.path.exists(CONFIG_PATH):
        return {"start": 1, "end": 10}
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            return {"start": int(cfg.get("start", 1)), "end": int(cfg.get("end", 1))}
    except (ValueError, json.JSONDecodeError):
        # if file corrupt, reset to defaults
        return {"start": 1, "end": 10}


def save_config(start, end):
    """Write the latest start/end back to disk."""
    with open(CONFIG_PATH, "w") as f:
        json.dump({"start": start, "end": end}, f)


def extract_chapter(start, end):
    chapters = []
    novel_title = ""

    if start > end:
        end = start + 1

    for i in range(start, end + 1):
        try:
            scraper = cloudscraper.create_scraper()
            url = f"https://novelbin.com/b/infinite-mana-in-the-apocalypse/chapter-{i}"
            response = scraper.get(url)

            if response.status_code != 200:
                chapters.append(
                    f"<h2>Chapter {i}</h2><p>Failed to load chapter content.</p>"
                )
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            title_tag = soup.find("a", class_="novel-title")
            if title_tag:
                novel_title = title_tag.text.strip()

            chapter_heading = soup.find(["h2", "h3", "h4"])
            chapter_title = (
                chapter_heading.get_text(strip=True)
                if chapter_heading
                else f"Chapter {i} (Title not found)"
            )

            content_div = soup.find("div", {"id": "chr-content"})
            paragraphs = content_div.find_all("p") if content_div else []

            chapter_html = f"<h2>{chapter_title}</h2>"
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text or any(
                    skip in text
                    for skip in [
                        "Enhance your reading experience",
                        "Translator: BornToBe",
                        "______",
                    ]
                ):
                    continue
                chapter_html += f"<p>{text}</p>"

            if not paragraphs:
                chapter_html += "<p>No content found.</p>"

            chapters.append(chapter_html)

        except Exception as e:
            chapters.append(
                f"<h2>Chapter {i}</h2><p>Error loading chapter: {str(e)}</p>"
            )

    return novel_title, chapters


@app.route("/", methods=["GET", "POST"])
def index():
    # load last-used values
    cfg = load_config()
    start = cfg["start"]
    end = cfg["end"]
    chapters = []
    novel_title = ""

    if request.method == "POST":
        try:
            # get from form
            start = int(request.form.get("start", start))
            end = int(request.form.get("end", end))
            novel_title, chapters = extract_chapter(start, end)
            # persist for next time
            save_config(start, end)
        except ValueError:
            chapters.append("<p>Invalid input. Please enter valid numbers.</p>")

    return render_template(
        "index.html", novel_title=novel_title, chapters=chapters, start=start, end=end
    )


if __name__ == "__main__":
    # ensure there's at least a default config on first run
    if not os.path.exists(CONFIG_PATH):
        save_config(1, 10)
    app.run(host="0.0.0.0", port=5000, debug=True)
