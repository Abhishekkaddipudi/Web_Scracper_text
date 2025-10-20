from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time
import json

from git_cmsg import update_novel_title_version

def build_url(url="https://novelbin.me/novel-book/my-augmented-statuses-have-unlimited-duration#tab-chapters-title",):
    update_novel_title_version(url)
    if 2 > 1:
        options = ChromeOptions()
        options.add_argument("--headless=new")  # Problem here
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        # Use a user-agent to avoid detection
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(3)

            # Find all chapter links
            chapters = []
            elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-chapter li a")
            print("---------------building url-------------")
            chapter_number=0
            for a_tag in elements:
                href = a_tag.get_attribute("href")
                title = a_tag.get_attribute("title")
                #match = re.search(r"Chapter (\d+)", title)
                """
                if match:
                    chapter_number = match.group(1)
                else:
                    match = re.search(r"/(?:chap\w*|ch\w*)[-_]?(\d+)", href, re.IGNORECASE)
                    if match:
                        chapter_number = match.group(1)
                    else:
                        print(match," ",title," ",href)
                        chapter_number = "unknown"
                """
                chapter_number+=1

                chapters.append({"chapter_number": chapter_number, "url": href})
            print("--------------saving chapters to json-------------")
            # Save chapters to JSON
            with open("chapters_full.json", "w", encoding="utf-8") as f:
                json.dump(chapters, f, ensure_ascii=False, indent=4)

            print(
                f"Extracted {len(chapters)} chapters after scrolling and saved to chapters_full.json"
            )

        except TimeoutException:
            print(f"Timed out waiting for content on {url}")
        except WebDriverException as e:
            print(f"Selenium WebDriver error on {url}: {e}")
        finally:
            driver.quit()

    # Wait for initial chapters to load


build_url()
