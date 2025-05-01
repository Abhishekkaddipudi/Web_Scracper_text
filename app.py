import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    chapter_output = ""  # Will hold the generated chapter HTML content

    if request.method == "POST":
        start = int(request.form.get("start", 1))
        end = int(request.form.get("end", 10))

        for i in range(start, end + 1):
            URL = f"https://novelbin.com/b/nine-star-hegemon-body-arts/chapter-{i}"
            r = requests.get(URL)
            soup = BeautifulSoup(r.content, "html.parser")

            chapter_heading = soup.find("h4")
            chapter_text = (
                chapter_heading.get_text(strip=True)
                if chapter_heading
                else f"Chapter {i} (Title not found)"
            )

            content_div = soup.find("div", {"id": "chr-content"})
            paragraphs = content_div.find_all("p") if content_div else []

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

    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chapter Viewer</title>
<style>
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        background-color: #fdfcf9;
        padding: 20px;
        line-height: 1.8;
        color: #222;
        font-weight: 600;
    }

    h1, h2 {
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 10px;
    }

    form {
        margin-bottom: 30px;
    }

    label {
        font-weight: bold;
        margin-right: 5px;
    }

    input[type="number"] {
        padding: 5px 10px;
        margin-right: 10px;
        font-size: 16px;
    }

    button {
        padding: 8px 16px;
        font-size: 16px;
        background-color: #2c3e50;
        color: white;
        border: none;
        cursor: pointer;
    }

    button:hover {
        background-color: #1a252f;
    }

    #chapter-content {
        max-width: 800px;
        margin-top: 20px;
    }

    p {
        font-size: 18px;
        margin-bottom: 16px;
    }
</style>


    </head>
    <body>
        
        <form method="POST">
           
            <input type="number" name="start" id="start" required value="{{ request.form.get('start', 1) }}">
            
            <input type="number" name="end" id="end" required value="{{ request.form.get('end', 10) }}">
            <button type="submit"></button>
        </form>

        <div id="chapter-content">
            {{ chapter_output | safe }}
        </div>
                <button id="increment" style="margin-top: 20px; padding: 8px 16px; background-color: #3498db; color: white; border: none; cursor: pointer;">
            Next
        </button>
          <script>
            document.getElementById('increment').onclick = function() {
                var startInput = document.getElementById('start');
                var endInput = document.getElementById('end');

                startInput.value = parseInt(startInput.value) + 10;
                endInput.value = parseInt(endInput.value) + 10;

                // Submit the form to fetch the next set of chapters
                document.querySelector('form').submit();
            };
        </script>

    </body>
    </html>
    """,
        chapter_output=chapter_output,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
