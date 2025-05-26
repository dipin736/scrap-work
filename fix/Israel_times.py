from datetime import datetime
from zoneinfo import ZoneInfo
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_article_data(page, url):
    try:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("load")

        # Save the page HTML locally
        with open("body.html", "wb") as html_file:
            html_file.write(page.content().encode("utf-8"))

        # Headline
        headline = page.query_selector("h1.headline")
        headline_text = headline.text_content().strip() if headline else "N/A"

        # Subheading
        subheading = page.query_selector("h2.underline")
        subheading_text = subheading.text_content().strip() if subheading else "N/A"

        # Timestamp
        timestamp_tag = page.query_selector("span.date")
        timestamp_text = timestamp_tag.text_content().strip() if timestamp_tag else "N/A"

        # Format timestamp
       # Format timestamp
        try:
            if timestamp_text != "N/A":
                timestamp_dt = datetime.strptime(timestamp_text, "%d %B %Y, %I:%M %p")
                local_dt = timestamp_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
            else:
                raise ValueError("Missing or invalid timestamp")

            date_text = local_dt.strftime("Updated %I:%M %p GMT+5:30, %B %d, %Y")

        except (ValueError, TypeError):
            now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
            date_text = now_ist.strftime("Updated %I:%M %p GMT+5:30, %B %d, %Y")


        # Article body from .the-content
        article_text = "N/A"
        article_div = page.query_selector("div.the-content")
        if article_div:
            paragraphs = article_div.query_selector_all("p")
            article_text = "\n".join([p.text_content().strip() for p in paragraphs if p.text_content().strip()])

        # Image URLs (featured + inline)
      # Image URLs (featured + inline)
# Only use the first featured image (if any)
        image = None
        image_element = page.query_selector("img.wp-post-image, div.media-rslides img")
        if image_element:
            image = image_element.get_attribute("src")

        # Liveblog entries using BeautifulSoup
        soup = BeautifulSoup(page.content(), "html.parser")
        entries = soup.find_all('div', id=lambda x: x and x.startswith('liveblog-entry'))

        liveblog_entries = []
        for entry in entries:
            heading_tag = entry.find('h4')
            heading = heading_tag.get_text() if heading_tag else None
            heading_link = heading_tag.find('a')['href'] if heading_tag and heading_tag.find('a') else None

            date_tag = entry.find('div', class_='liveblog-date')
            date = date_tag.get_text() if date_tag else None

            author_tag = entry.find('div', class_='byline')
            author = author_tag.get_text() if author_tag else None
            author_link = author_tag.find('a')['href'] if author_tag and author_tag.find('a') else None

            media_tag = entry.find('div', class_='media')
            image_url = media_tag.find('img')['src'] if media_tag and media_tag.find('img') else None
            caption = media_tag.find('div', class_='caption').get_text() if media_tag and media_tag.find('div', class_='caption') else None

            paragraphs = entry.find_all('p')
            content = " ".join([para.get_text() for para in paragraphs]) if paragraphs else None

            social_links = {}
            social_media = entry.find('ul', class_='social')
            if social_media:
                for social_tag in social_media.find_all('a', href=True):
                    social_platform = social_tag['class'][0] if social_tag.get('class') else 'unknown'
                    social_links[social_platform] = social_tag['href']

            liveblog_entries.append({
                "heading": heading,
                "heading_link": heading_link,
                "date": date,
                "author": author,
                "author_link": author_link,
                "image_url": image_url,
                "caption": caption,
                "content": content,
                "social_links": social_links
            })

        return {
            "url": url,
            "headline": headline_text,
            "subheading": subheading_text,
            "date": date_text,
            "article": article_text,
            "image": image,
            "liveblog_entries": liveblog_entries
        }

    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return None

# Main scraping flow
def main():
    with open("TOIsrael_article_links_v21.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    all_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for url in urls:
            article_data = extract_article_data(page, url)
            if article_data:
                all_articles.append(article_data)

        browser.close()

    # Save output to JSON
    with open("all_articles_output.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print("Saved all articles to all_articles_output.json")

if __name__ == "__main__":
    main()
