import requests
from bs4 import BeautifulSoup
import json
import time
import random

def load_browser_cookies(filepath):
    with open(filepath, "r") as f:
        raw_cookies = json.load(f)
    return {cookie["name"]: cookie["value"] for cookie in raw_cookies}

def scrape_article(url, cookies, headers):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print(f" Failed to fetch {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # removing unwanted stuffs 
    for box in soup.find_all("div", class_="wpds-c-PJLV article-body type-story subtype-context-box"):
        box.decompose()

    # removing the footer
    footer_div = soup.find("div", class_="wpds-c-iMBzTR article-footer")
    if footer_div:
        footer_div.decompose()

    # title
    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "No title found"

    # subheadline
    subheadline_tag = soup.find("p", {"data-qa": "subheadline"})
    subheadline = subheadline_tag.text.strip() if subheadline_tag else "No subheadline found"

    # article body getting (primary method)
    article_tag = soup.find("article", {"data-qa": "main"})
    article_text = ""
    if article_tag:
        paragraphs = []
        for p in article_tag.find_all("p"):
            if p.find("a") and not p.get_text(strip=True).replace(p.a.text.strip(), '').strip():
                continue
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        article_text = "\n".join(paragraphs)

    # secondary method seince there are 2 types of article body un here
    if not article_text.strip():
     paragraphs = []


    for section in soup.find_all("div", class_="wpds-c-PJLV article-body type-text grid-center grid-body"):
        for p in section.find_all("p", {"data-apitype": "text"}):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)


    if not paragraphs:
        for p in soup.find_all("p", {"data-component": "Text"}):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)

    article_text = "\n".join(paragraphs) if paragraphs else "No article content found."

    # datetime
    time_tag = soup.find("time", {"data-testid": "updated-and-published"})
    if time_tag and time_tag.has_attr("datetime"):
        datetime_value = time_tag["datetime"]
    else:
        time_tag = soup.find("time", datetime=True)
        datetime_value = time_tag["datetime"] if time_tag else "No datetime found"

    # imageurl
   # imageurl
    image_tag = soup.find("img")
    if image_tag:
        if image_tag.get("srcset"):
            # Get the highest resolution image from srcset
            srcset_urls = [u.split()[0] for u in image_tag["srcset"].split(",")]
            image_url = srcset_urls[-1] if srcset_urls else image_tag.get("src", "No image found")
        else:
            image_url = image_tag.get("src", "No image found")
    else:
        image_url = "No image found"


    return {
        "url": url,
        "datetime": datetime_value,
        "title": title,
        "subheadline": subheadline,
        "image_url": image_url,
        "article_text": article_text
    }

def main():
    # using cookis
    cookies = load_browser_cookies("cookie.json")

    # adding headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Read URLs from file
    with open("washington_post.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_articles = []
    for url in urls:
        print(f" Scraping {url} ...")
        article_data = scrape_article(url, cookies, headers)
        if article_data:
            all_articles.append(article_data)

        # random delays to prevent anti bot script getting trigglerd
        delay = random.uniform(1, 3)
        print(f" Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    # saving output to json
    with open("articles_output.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    print(f" Done Scraped {len(all_articles)} articles saved to articles_output.json")

if __name__ == "__main__":
    main()
