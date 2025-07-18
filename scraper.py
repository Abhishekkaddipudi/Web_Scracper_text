import json
import cloudscraper
from bs4 import BeautifulSoup


def extract_chapter(start: int, end: int, chapters_json_path: str):
    """
    Fetches chapters from `start` to `end` (inclusive) using the URLs in the JSON file.

    Args:
      start:  The first chapter number to fetch (1-based).
      end:    The last chapter number to fetch (inclusive).
      chapters_json_path: Path to your JSON file containing:
          [
            {"chapter_number": "1", "url": "..."},
            {"chapter_number": "2", "url": "..."},
            ...
          ]

    Returns:
      novel_title: The novel title (from the first chapter page).
      chapters:    A list of HTML strings, one per chapter.
    """
    # Load your chapters list
    with open(chapters_json_path, encoding="utf-8") as f:
        all_chapters = json.load(f)

    # Build a dict for quick lookup by chapter number
    url_map = {int(item["chapter_number"]): item["url"] for item in all_chapters}

    scraper = cloudscraper.create_scraper()
    novel_title = ""
    chapters = []

    for chap_num in range(start, end + 1):
        url = url_map.get(chap_num)
        if not url:
            chapters.append(
                f"<h2>Missing URL</h2><p>Chapter {chap_num} URL not found.</p>"
            )
            continue

        try:
            r = scraper.get(url)
            if r.status_code != 200:
                chapters.append(f"<h2>Failed to load</h2><p>{url}</p>")
                continue

            soup = BeautifulSoup(r.content, "html.parser")

            # Once, grab the canonical novel title
            if not novel_title:
                title_tag = soup.find("a", class_="novel-title")
                if title_tag:
                    novel_title = title_tag.get_text(strip=True)

            # Chapter heading
            heading = soup.find(["h2", "h3", "h4"])
            chap_title = (
                heading.get_text(strip=True) if heading else f"Chapter {chap_num}"
            )

            # Chapter body
            body = soup.find("div", {"id": "chr-content"})
            paras = body.find_all("p")[:-1] if body else []
            
            filtered_paras = [BeautifulSoup(str(p).replace("_", " "), "html.parser") if "_" in p.get_text() else p for p in paras]

            html = f"<h2>{chap_title}</h2>" + (
                "".join("<p>"+str(p)+"</p>" for p in filtered_paras) or "<p>No content.</p>"
            )
            chapters.append(html)

        except Exception as e:
            chapters.append(f"<h2>Error</h2><p>{e}</p>")

    return novel_title, chapters
