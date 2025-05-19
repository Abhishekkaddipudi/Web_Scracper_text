import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)


def extract_chapter(start, end):
    chapters = []

    if start > end:
        end = start + 1

    for i in range(start, end + 1):
        try:
            scraper = cloudscraper.create_scraper()
            url = f"https://novelbin.com/b/versatile-mage/chapter-{i}"
            response = scraper.get(url)

            if response.status_code != 200:
                chapters.append(
                    f"<h2>Chapter {i}</h2><p>Failed to load chapter content.</p>"
                )
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            novel_title = soup.find("a", class_="novel-title").text

            # Accept h2, h3, or h4 as title
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
    chapters = []
    if request.method == "POST":
        start = int(request.form.get("start", 1))
        end = int(request.form.get("end", start))
        novel_title, chapters = extract_chapter(start=start, end=end)

    return render_template("index.html", novel_title=novel_title, chapters=chapters)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
