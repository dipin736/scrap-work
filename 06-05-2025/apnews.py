import requests
from bs4 import BeautifulSoup
import json

def extract_article_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Headline
    headline = soup.find("h1", class_="Page-headline")
    headline_text = headline.get_text(strip=True) if headline else "N/A"

    # Date
    date_span = soup.select_one(".Page-dateModified [data-date]")
    date_text = date_span.get_text(strip=True) if date_span else "N/A"

    # Article body
    article_div = soup.find("div", class_="RichTextStoryBody")
    article_paragraphs = article_div.find_all("p") if article_div else []
    article_text = "\n".join(p.get_text(strip=True) for p in article_paragraphs)

    # One image per figure
    image_urls = []
    figures = soup.find_all("figure", class_="Figure")
    for figure in figures:
        first_source = figure.find("source", srcset=True)
        if first_source:
            srcset = first_source["srcset"]
            image_url = srcset.split(",")[0].split()[0]
            image_urls.append(image_url)

    return {
        "url": url,
        "headline": headline_text,
        "date": date_text,
        "article": article_text,
        "images": image_urls
    }

# Read URLs from file
with open("article_links.txt", "r", encoding="utf-8") as file:
    urls = [line.strip() for line in file if line.strip()]

# Extract data for each article
all_articles = []
for url in urls:
    try:
        article_data = extract_article_data(url)
        all_articles.append(article_data)
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Save all data to JSON
with open("all_articles_output.json", "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=2)

print("Saved all articles to all_articles_output.json")
