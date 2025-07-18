from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
options = Options()
#options.add_argument("--headless")  # run in background
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")



driver = webdriver.Chrome( options=options)
driver.get("https://fictionzone.net/novel/global-job-change-necromancer-i-am-a-catastrophe")

time.sleep(3)  # Let page load JS

all_chapters = []

# Loop through page numbers
for page in range(1, 43):  # as seen, there are 42 pages
    time.sleep(20)
    print(f"Scraping Page {page}")
    time.sleep(2)

    # Collect chapter titles + links
    chapter_elements = driver.find_elements(By.CSS_SELECTOR, ".chapter .chapter-title a")
    for ch in chapter_elements:
        title = ch.text.strip()
        link = ch.get_attribute("href")
        all_chapters.append((title, link))

    # Click on the next page number (if not on the last one)
    if page < 42:
        try:
            next_button = driver.find_element(By.XPATH, f"//li[contains(@class, 'number') and text()='{page+1}']")
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print(f"Couldn't go to page {page+1}: {e}")
            break

driver.quit()

# Output results
for i, (title, link) in enumerate(all_chapters, 1):
    print(f"{i}. {title} - {link}")
