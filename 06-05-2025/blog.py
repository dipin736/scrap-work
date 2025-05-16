import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

url = "https://www.timesofisrael.com/liveblog-april-28-2025/"


options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get(url)


soup = BeautifulSoup(driver.page_source, "html.parser")


title = soup.find("h1", class_="headline").get_text(
    strip=True) if soup.find("h1", class_="headline") else "No title found"

entries = []
liveblog_divs = soup.find_all("div", class_="liveblog-paragraph")

for div in liveblog_divs:
    entry = {}

    time_tag = div.find_previous_sibling("div", class_="liveblog-date")
    entry["time"] = time_tag.get_text(strip=True) if time_tag else "No time"

    headline_tag = div.find("h4")
    entry["headline"] = headline_tag.get_text(
        strip=True) if headline_tag else "No headline"

    paragraphs = div.find_all("p")
    content = " ".join(p.get_text(strip=True) for p in paragraphs)
    entry["content"] = content if content else "No content"

    byline = div.find("div", class_="byline")
    entry["author"] = byline.get_text(strip=True).replace(
        "By", "") if byline else "Unknown"

    entries.append(entry)


data = {
    "title": title,
    "url": url,
    "entries": entries
}


with open("liveblog_april_28_2025.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Data saved to liveblog_april_28_2025.json")

driver.quit()
