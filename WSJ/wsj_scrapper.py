import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime
import pytz  

def load_browser_cookies(filepath):
    with open(filepath, "r") as f:
        raw_cookies = json.load(f)
    return {cookie["name"]: cookie["value"] for cookie in raw_cookies}


def extract_date_from_ld_json(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict) and "datePublished" in entry:
                        return convert_iso_to_et(entry["datePublished"])
            elif isinstance(data, dict) and "datePublished" in data:
                return convert_iso_to_et(data["datePublished"])
        except:
            continue
    return "No published date"

def convert_iso_to_et(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        # Convert to Eastern Time (ET)
        eastern = pytz.timezone("US/Eastern")
        dt_et = dt.astimezone(eastern)
        return dt_et.strftime("%B %d, %Y %I:%M %p ET")  # e.g., May 23, 2025 11:34 AM ET
    except:
        return iso_string  # fallback

def scrape_wsj_article(url, cookies, headers):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title_tag = soup.find("h1", {"data-testid": "headline"}) or \
                soup.select_one("div.css-bsrkcm-Box.e1vnmyci0 h1") or \
                soup.find("h1", class_=re.compile("StyledHeadline"))
    title = title_tag.get_text(strip=True) if title_tag else "No title found"
    published_date = extract_date_from_ld_json(soup)

    # Dek
    dek_block = soup.find("h2", {"data-testid": "dek-block"}) or \
                soup.find("h2", class_=re.compile("NormalDek"))
    dek = dek_block.get_text(strip=True) if dek_block else "No dek found"

    # Subheadline
    caption_span = soup.find("span", class_="css-426zcb-CaptionSpan")
    subheadline = caption_span.get_text(strip=True) if caption_span else "No subheadline found"

    # Image
    image_url = "No image found"
    img_tag = soup.find("picture", class_="css-u314cv")
    if img_tag:
        img = img_tag.find("img")
        if img and img.has_attr("srcset"):
            srcset_urls = [entry.split()[0] for entry in img["srcset"].split(",")]
            image_url = srcset_urls[-1] if srcset_urls else img.get("src", "No image found")
        elif img and img.get("src"):
            image_url = img["src"]

    # Article text
    article_section = soup.find("section", class_="css-1lhnhkw-Container")

    article_text = ""
    if article_section:
        paragraphs = article_section.find_all("p", {"data-testid": "paragraph"})
        
        if not paragraphs:
            paragraphs = article_section.find_all("p")

        article_text = "\n".join(
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        )
    else:
        article_text = "No article content found"


    return {
        "url": url,
        "datetime": published_date,
        "title": title,
        "dek": dek,
        "subheadline": subheadline,
        "image_url": image_url,
        "article_text": article_text
    }

def main():
    cookies = load_browser_cookies("cookie.json")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    with open("wsj_urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_articles = []
    for url in urls:
        print(f"Scraping {url} ...")
        article_data = scrape_wsj_article(url, cookies, headers)
        if article_data:
            all_articles.append(article_data)
        time.sleep(random.uniform(1, 3))

    with open("wsj_articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    print(f"Done. Scraped {len(all_articles)} articles and saved to wsj_articles.json")

if __name__ == "__main__":
    main()
