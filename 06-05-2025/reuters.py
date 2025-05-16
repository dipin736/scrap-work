import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Read news article links from text file
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]

# Extract article details from a Reuters URL
def extract_article_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Publication datetime
        pub_time_meta = soup.find("meta", attrs={"property": "og:article:published_time"})
        pub_datetime = pub_time_meta["content"] if pub_time_meta else None
        pub_display = None
        if pub_datetime:
            dt_obj = datetime.fromisoformat(pub_datetime.replace("Z", "+00:00"))
            pub_display = dt_obj.strftime("%B %d, %Y | %I:%M %p UTC")

        # Image
        image_meta = soup.find("meta", attrs={"property": "og:image"})
        image_url = image_meta["content"] if image_meta else None

        # Summary bullets
   # Fix summary selector
        summary_section = soup.find("ul", attrs={"data-testid": "Summary"})
        summary = [li.get_text(strip=True) for li in summary_section.find_all("li")] if summary_section else []


        # Article content
        paragraphs = soup.find_all("div", attrs={"data-testid": lambda x: x and x.startswith("paragraph-")})
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        return {
            "title": title,
            "url": url,
            "publication_datetime": pub_datetime,
            "publication_display": pub_display,
            "image_url": image_url,
            "summary": summary,
            "content": content
        }

    except Exception as e:
        print(f"❌ Error extracting data from {url}: {e}")
        return None

# Main function
def main():
    urls = read_urls_from_file("news_links.txt")
    all_articles = []

    for url in urls:
        article_data = extract_article_data(url)
        if article_data:
            all_articles.append(article_data)

    with open("articles_data.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print("✅ Articles saved to articles_data.json")

if __name__ == "__main__":
    main()
