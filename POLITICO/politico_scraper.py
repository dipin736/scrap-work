from datetime import datetime
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extract_politico_article(page, url):
    try:
        page.goto(url, timeout=90000, wait_until="domcontentloaded")

        html_content = page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        with open("politico_body.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        # HEADLINE
        headline = soup.select_one("h1.headline, h1.article__headline, h1")
        headline_text = headline.get_text(strip=True) if headline else "N/A"

        # SUBHEADING
        subheading = soup.select_one("p.dek, div.dek, div.summary, h2")
        subheading_text = subheading.get_text(strip=True) if subheading else "N/A"

        # DATE
        time_tag = soup.select_one("time[datetime], p.story-meta__timestamp time")
        timestamp_text = time_tag.get("datetime") if time_tag else "N/A"

        # Format readable date
        if timestamp_text != "N/A":
            try:
                timestamp_dt = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S")
                date_text = timestamp_dt.strftime("%B %d, %Y – %I:%M %p EDT")
            except ValueError:
                date_text = timestamp_text
        else:
            date_text = "N/A"

        # ARTICLE BODY
        article_text = "N/A"
        for selector in [
            "div.story-text",
            "div.article__content",
            "main article",
            "article[data-story-id]",
            "section.article-content"
        ]:
            article_div = soup.select_one(selector)
            if article_div:
                paragraphs = article_div.find_all("p")
                if paragraphs:
                    article_text = "\n".join(
                        [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                    )
                    break

        # IMAGE
        image_tag = soup.select_one("figure img, img.article__image")
        image = image_tag.get("src") if image_tag and image_tag.get("src") else None

        if not image:
            og_image = soup.find("meta", property="og:image")
            image = og_image.get("content") if og_image else None

        return {
            "url": url,
            "headline": headline_text,
            "subheading": subheading_text,
            "date": date_text,
            "article": article_text,
            "image": image
        }

    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return {
            "url": url,
            "headline": "N/A",
            "subheading": "N/A",
            "date": "N/A",
            "article": "N/A",
            "image": None
        }

# ---------- Main Runner ---------- #
def main():
    start_time = datetime.now()
    print("Started at:", start_time.strftime("%Y-%m-%d %I:%M:%S %p"))

    with open("POLITICO/politico.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    all_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for url in urls:
            try:
                page = browser.new_page()
                article_data = extract_politico_article(page, url)
                all_articles.append(article_data)
                page.close()
            except Exception as e:
                print(f"Error loading {url}: {e}")

        browser.close()

    with open("politico_articles_output.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    end_time = datetime.now()
    print("Finished at:", end_time.strftime("%Y-%m-%d %I:%M:%S %p"))
    print("Duration:", str(end_time - start_time))

if __name__ == "__main__":
    main()
