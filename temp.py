import requests
from bs4 import BeautifulSoup

# scrapper for shangri la-frontier
# Target URL

url = "https://ncode.syosetu.com/n6169dz/1/"

# Custom headers to simulate a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Fetch the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Extract title
title_tag = soup.select_one("h1.p-novel__title")
title = title_tag.get_text(strip=True) if title_tag else "Title not found"

# Extract novel text
text_div = soup.select_one("div.js-novel-text")
paragraphs = text_div.find_all("p") if text_div else []
text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

# Output
print("Title:", title)
print("\n--- Novel Text ---\n")
print(text)

