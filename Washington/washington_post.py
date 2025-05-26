from datetime import datetime
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def extract_article(driver, url):
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'h1[data-qa="headline"], h1[data-testid="headline"], div[data-qa="article-body"]')
                )
            )
        except TimeoutException:
            print(f"Timeout waiting for page content at {url}")

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # HEADLINE
        headline = soup.select_one('h1[data-qa="headline"], h1[data-testid="headline"]')
        headline_text = headline.get_text(strip=True) if headline else "N/A"

        # DATE
        date_tag = soup.select_one('span[data-testid="display-date"]') or soup.select_one('span[data-testid="published-date"]')
        date_text = date_tag.get_text(strip=True) if date_tag else "N/A"


        # SUBHEADING
        subheading = soup.select_one('p[data-qa="subheadline"], p[data-testid="subheadline"]')
        subheading_text = subheading.get_text(strip=True) if subheading else "N/A"

        # ARTICLE BODY
        article_paragraphs = soup.select('div[data-qa="article-body"] p')
        article_text = "\n\n".join(p.get_text(strip=True) for p in article_paragraphs if p.get_text(strip=True)) or "N/A"

        # IMAGE
        image_tag = soup.select_one('img.w-100.mw-100.h-auto')
        if image_tag:
            srcset = image_tag.get('srcset')
            if srcset:
                image_url = srcset.split()[0]
            else:
                image_url = image_tag.get('src')
        else:
            og_image = soup.find('meta', property='og:image')
            image_url = og_image['content'] if og_image else None

        return {
            "url": url,
            "headline": headline_text,
            "date": date_text,
            "subheading": subheading_text,
            "article": article_text,
            "image": image_url
        }

    except WebDriverException as e:
        print(f"WebDriverException while loading {url}: {e}")
    except Exception as e:
        print(f"Failed to process {url}: {e}")

    return {
        "url": url,
        "headline": "N/A",
        "date": "N/A",
        "subheading": "N/A",
        "article": "N/A",
        "image": None
    }


def main():
    start_time = datetime.now()
    print("Started at:", start_time.strftime("%Y-%m-%d %I:%M:%S %p"))

    # Make sure your ChromeDriver matches your Chrome browser version
    # https://chromedriver.chromium.org/downloads

    with open("washington_post.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    all_articles = []

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set a common user agent to avoid bot blocking
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    try:
        for url in urls:
            print(f"Processing: {url}")
            article_data = extract_article(driver, url)
            all_articles.append(article_data)

    finally:
        driver.quit()

    with open("washington_post_output.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    end_time = datetime.now()
    print("Finished at:", end_time.strftime("%Y-%m-%d %I:%M:%S %p"))
    print("Duration:", str(end_time - start_time))


if __name__ == "__main__":
    main()
