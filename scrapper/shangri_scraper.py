import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ncode.syosetu.com/n6169dz"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_shangri_chapters(start=1, end=1):
    chapters = []
    novel_title = "Shangri-La Frontier"

    for chap_num in range(start, end + 1):
        try:
            url = f"{BASE_URL}/{chap_num}/"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract chapter title (not novel title)
            chapter_title_tag = soup.select_one("h1.p-novel__title")
            chapter_title = chapter_title_tag.get_text(strip=True) if chapter_title_tag else f"Chapter {chap_num}"

            # Extract all novel text divs
            text_divs = soup.select("div.js-novel-text")
            paragraphs = []
            for div in text_divs:
                for p in div.find_all("p"):
                    text = p.get_text(strip=True)
                    if text:
                        paragraphs.append(text)
            html = f"<h2>章-{chap_num}</h2>"+f"<h2>{chapter_title}</h2>" + (
                "".join("<p>"+str(p)+"</p>" for p in paragraphs) or "<p>No content.</p>"
            )            
            chapters.append(html)

        except Exception as e:
            chapters.append(f"<p>Error loading chapter {chap_num}: {e}</p>")

    return novel_title, chapters
