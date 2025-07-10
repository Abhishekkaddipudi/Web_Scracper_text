from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import sys
import os

# Import your custom function (comment out if not available)
try:
    from git_cmsg import update_novel_title_version
except ImportError:
    def update_novel_title_version(url):
        """Fallback function if git_cmsg module is not available"""
        print(f"Processing URL: {url}")
        pass

def detect_browser():
    """Detect which browser is available in Termux"""
    try:
        # Check if geckodriver is available
        os.system("geckodriver --version > /dev/null 2>&1")
        if os.system("which geckodriver > /dev/null 2>&1") == 0:
            print("Firefox/Geckodriver detected")
            return "firefox"
    except:
        pass
    
    try:
        # Check if chromedriver is available
        if os.system("which chromedriver > /dev/null 2>&1") == 0:
            print("Chrome/Chromedriver detected")
            return "chrome"
    except:
        pass
    
    print("No browser driver found. Please install geckodriver or chromedriver")
    return None

def create_driver(browser_type="firefox"):
    """Create WebDriver instance based on available browser"""
    if browser_type == "firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Set user agent
        options.set_preference("general.useragent.override", 
                              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        try:
            driver = webdriver.Firefox(options=options)
            print("Firefox driver created successfully")
            return driver
        except Exception as e:
            print(f"Failed to create Firefox driver: {e}")
            return None
    
    elif browser_type == "chrome":
        options = ChromeOptions()
        options.add_argument("--headless")  # Use --headless instead of --headless=new for compatibility
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--window-size=1920,1080")
        
        # Set user agent
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(options=options)
            print("Chrome driver created successfully")
            return driver
        except Exception as e:
            print(f"Failed to create Chrome driver: {e}")
            return None
    
    return None

def scroll_to_load_all_chapters(driver, max_scrolls=10):
    """Scroll to load all chapters with better control"""
    print("Starting to scroll and load all chapters...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    
    while scrolls < max_scrolls:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for content to load
        time.sleep(3)
        
        # Check current chapter count
        current_chapters = driver.find_elements(By.CSS_SELECTOR, "ul.list-chapter li a")
        print(f"Scroll {scrolls + 1}: Found {len(current_chapters)} chapters")
        
        # Check if page height changed
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            print("No new content loaded, checking for load more buttons...")
            
            # Try to find and click load more buttons
            load_more_selectors = [
                "button:contains('Load More')",
                "button:contains('Show More')",
                "a:contains('Load More')",
                "a:contains('Show More')",
                ".load-more",
                ".show-more",
                "[onclick*='load']",
                "[onclick*='more']"
            ]
            
            button_clicked = False
            for selector in load_more_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector.replace(':contains', ''))
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Check if text contains load/more
                            text = element.text.lower()
                            if 'load' in text or 'more' in text:
                                driver.execute_script("arguments[0].click();", element)
                                print(f"Clicked button: {element.text}")
                                time.sleep(3)
                                button_clicked = True
                                break
                    if button_clicked:
                        break
                except:
                    continue
            
            if not button_clicked:
                print("No more content to load")
                break
        
        last_height = new_height
        scrolls += 1
    
    final_chapters = driver.find_elements(By.CSS_SELECTOR, "ul.list-chapter li a")
    print(f"Finished scrolling. Total chapters found: {len(final_chapters)}")
    return final_chapters

def build_url(url="https://readnovelfull.com/i-have-a-special-cultivation-talent.html#tab-chapters-title"):
    """Enhanced version for Termux with better error handling and scrolling"""
    
    print(f"Starting chapter extraction from: {url}")
    update_novel_title_version(url)
    
    # Detect available browser
    browser_type = detect_browser()
    if not browser_type:
        print("Error: No browser driver found!")
        print("Please install:")
        print("  For Firefox: pkg install firefox geckodriver")
        print("  For Chrome: pkg install chromium (and setup chromedriver)")
        return
    
    driver = None
    try:
        # Create driver
        driver = create_driver(browser_type)
        if not driver:
            print("Failed to create driver")
            return
        
        print("Loading page...")
        driver.get(url)
        
        # Wait for initial content to load
        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-chapter")))
            print("Chapter list found, waiting for content to load...")
        except TimeoutException:
            print("Warning: Chapter list not found immediately, continuing anyway...")
        
        # Wait a bit more for dynamic content
        time.sleep(5)
        
        # Scroll to load all chapters
        all_elements = scroll_to_load_all_chapters(driver)
        
        print("---------------building url-------------")
        
        # Extract chapter information
        chapters = []
        for i, a_tag in enumerate(all_elements):
            try:
                href = a_tag.get_attribute("href")
                title = a_tag.get_attribute("title")
                
                # Handle None values
                if not href:
                    continue
                
                if not title:
                    title = a_tag.text.strip()
                
                # Extract chapter number
                chapter_number = "unknown"
                
                # Try to find chapter number in title
                if title:
                    match = re.search(r"Chapter (\d+)", title, re.IGNORECASE)
                    if match:
                        chapter_number = match.group(1)
                    else:
                        # Try other patterns
                        patterns = [
                            r"Ch\.?\s*(\d+)",
                            r"Chap\.?\s*(\d+)",
                            r"第(\d+)章",
                            r"(\d+)\s*-"
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, title, re.IGNORECASE)
                            if match:
                                chapter_number = match.group(1)
                                break
                
                # If still no chapter number, try URL
                if chapter_number == "unknown":
                    url_patterns = [
                        r"/(?:chap\w*|ch\w*)[-_]?(\d+)",
                        r"chapter[-_]?(\d+)",
                        r"/(\d+)(?:\.html?)?(?:[?#].*)?$"
                    ]
                    for pattern in url_patterns:
                        match = re.search(pattern, href, re.IGNORECASE)
                        if match:
                            chapter_number = match.group(1)
                            break
                
                if chapter_number == "unknown":
                    print(f"Could not extract chapter number from: title='{title}', href='{href}'")
                
                chapters.append({
                    "chapter_number": chapter_number,
                    "url": href,
                    "title": title
                })
                
            except Exception as e:
                print(f"Error processing element {i}: {e}")
                continue
        
        print("--------------saving chapters to json-------------")
        
        # Save chapters to JSON
        with open("chapters_full.json", "w", encoding="utf-8") as f:
            json.dump(chapters, f, ensure_ascii=False, indent=4)
        
        print(f"Extracted {len(chapters)} chapters and saved to chapters_full.json")
        
        # Print some statistics
        valid_chapters = [ch for ch in chapters if ch["chapter_number"] != "unknown"]
        print(f"Valid chapters with numbers: {len(valid_chapters)}")
        if valid_chapters:
            numbers = [int(ch["chapter_number"]) for ch in valid_chapters if ch["chapter_number"].isdigit()]
            if numbers:
                print(f"Chapter range: {min(numbers)} - {max(numbers)}")
        
        return chapters
        
    except TimeoutException:
        print(f"Timed out waiting for content on {url}")
        return []
    except WebDriverException as e:
        print(f"Selenium WebDriver error on {url}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
                print("Driver closed successfully")
            except:
                print("Error closing driver")

def main():
    """Main function to run the scraper"""
    print("=== Termux Novel Chapter Scraper ===")
    print("Make sure you have installed:")
    print("  pkg install python firefox geckodriver")
    print("  pip install selenium")
    print()
    
    # You can change the URL here
    url = "https://readnovelfull.com/i-have-a-special-cultivation-talent.html#tab-chapters-title"
    
    # Allow custom URL from command line
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Using custom URL: {url}")
    
    chapters = build_url(url)
    
    if chapters:
        print(f"\n✅ Success! Extracted {len(chapters)} chapters")
        print("📁 Saved to: chapters_full.json")
    else:
        print("\n❌ Failed to extract chapters")

if __name__ == "__main__":
    main()