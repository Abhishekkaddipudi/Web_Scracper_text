import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)


def extract_chapter(start, end):
    chapter_output = ""
    if start > end:
        end = start + 1
    for i in range(start, end + 1):

        scraper = cloudscraper.create_scraper()
        url = f"https://novelbin.com/b/dungeon-diver-stealing-a-monsters-power/chapter-{i}"
        response = scraper.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)
        chapter_heading = soup.find("h3")
        chapter_text = (
            chapter_heading.get_text(strip=True)
            if chapter_heading
            else f"Chapter {i} (Title not found)"
        )

        content_div = soup.find("div", {"id": "chr-content"})
        # print(content_div)

        paragraphs = content_div.find_all("p") if content_div else []
        # print(paragraphs)
        chapter_output += f"<h2>{chapter_text}</h2>"
        for p in paragraphs:
            text = p.get_text(strip=True)
            if (
                text
                == "Enhance your reading experience by removing ads for as low as$1!"
            ):
                continue
            if text == "Translator: BornToBe":
                continue
            if text:
                chapter_output += f"<p>{text}</p>"
    return chapter_output


@app.route("/", methods=["GET", "POST"])
def index():
    chapter_output = ""
    if request.method == "POST":
        start = int(request.form.get("start", 1))
        end = int(request.form.get("end", 10))
        chapter_output = extract_chapter(start=start, end=end)

    return render_template(
        "./index.html",
        chapter_output=chapter_output,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
