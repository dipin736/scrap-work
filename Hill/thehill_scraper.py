import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

def load_browser_cookies(filepath):
    with open(filepath, "r") as f:
        raw_cookies = json.load(f)
    return {cookie["name"]: cookie["value"] for cookie in raw_cookies}

def scrape_thehill_article(url, cookies, headers):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title_tag = soup.find("h1", class_="page-title")
    title = title_tag.get_text(strip=True) if title_tag else "No title found"

    # Date
    date_section = soup.find("section", class_="submitted-by")
    if date_section:
        match = re.search(r"\d{2}/\d{2}/\d{2} \d{1,2}:\d{2} [AP]M ET", date_section.get_text(strip=True))
        published_date = match.group(0) if match else "No date found"
    else:
        published_date = "No date found"

    # Article content
    article_section = soup.find("div", class_="article__text")
    article_text = ""
    if article_section:
        paragraphs = [
            p.get_text(strip=True)
            for p in article_section.find_all("p")
            if p.get_text(strip=True)
        ]
        article_text = "\n".join(paragraphs)
    else:
        article_text = "No article content found"

    # Image
    image_url = "No image found"

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if any(part in src for part in ["/assets/", "/themes/", "logo", "icon", "sprite", "google-news"]):
            continue

        if "wp-content/uploads" in src:
            if img.has_attr("srcset"):
                srcset_urls = [entry.split()[0] for entry in img["srcset"].split(",")]
                image_url = srcset_urls[-1] if srcset_urls else src
            else:
                image_url = src
            break


    caption_div = soup.find("div", class_="caption")
    subheadline = caption_div.get_text(strip=True) if caption_div else "No subheadline found"


    return {
        "url": url,
        "datetime": published_date,
        "title": title,
        "image_url": image_url,
        "subheadline": subheadline,
        "article_text": article_text
    }

def main():
    cookies = load_browser_cookies("cookie.json")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Read URLs from file
    with open("thehill_urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_articles = []
    for url in urls:
        print(f"🔍 Scraping {url} ...")
        article_data = scrape_thehill_article(url, cookies, headers)
        if article_data:
            all_articles.append(article_data)

        delay = random.uniform(1, 3)
        print(f"Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    with open("thehill_articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    print(f" Done. Scraped {len(all_articles)} articles saved to thehill_articles.json")

if __name__ == "__main__":
    main()
