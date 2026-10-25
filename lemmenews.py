import os
import time
import html
import requests
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
RSS_URL = "https://moxie.foxnews.com/google-publisher/latest.xml"
CHECK_INTERVAL = 300  
STATE_FILE = Path("knowbetter_state.json")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

def load_last_article():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8")).get("last_article", "")
    except Exception:
        pass
    return ""

def save_last_article(article_id):
    try:
        STATE_FILE.write_text(json.dumps({"last_article": article_id}), encoding="utf-8")
    except Exception:
        pass

def get_latest_article():
    response = SESSION.get(RSS_URL, timeout=20)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    item = root.find("./channel/item")
    
    if item is None:
        return None

    article = {
        "title": item.findtext("title", ""),
        "link": item.findtext("link", ""),
        "description": item.findtext("description", ""),
        "guid": item.findtext("guid", ""),
        "pubDate": item.findtext("pubDate", ""),
        "image_url": ""
    }

    media_group = item.find("{http://search.yahoo.com/mrss/}group")
    if media_group is not None:
        media_content = media_group.find("{http://search.yahoo.com/mrss/}content")
        if media_content is not None:
            article["image_url"] = media_content.get("url", "")
    else:
        media_content = item.find("{http://search.yahoo.com/mrss/}content")
        if media_content is not None:
            article["image_url"] = media_content.get("url", "")
        else:
            enclosure = item.find("enclosure")
            if enclosure is not None:
                article["image_url"] = enclosure.get("url", "")

    return article

def get_article_id(article):
    identifier = article["guid"] or article["link"] or article["title"]
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()

def post_to_discord(article):
    embed = {
        "title": html.unescape(article["title"])[:256],
        "description": html.unescape(article["description"])[:4000],
        "url": article["link"] if article["link"].startswith("http") else "",
        "color": 15548997,
        "footer": {"text": f"Fox News | {article['pubDate']}"[:2048]}
    }
    
    if article["image_url"].startswith("http"):
        embed["image"] = {"url": article["image_url"]}

    response = SESSION.post(
        WEBHOOK_URL,
        json={"username": "KnowBetter", "embeds": [embed]},
        timeout=20
    )
    response.raise_for_status()

def main():
    if not WEBHOOK_URL:
        return print("ERROR: Set DISCORD_WEBHOOK_URL")

    last_article = load_last_article()
    
    while True:
        try:
            article = get_latest_article()
            if article:
                article_id = get_article_id(article)
                if article_id != last_article:
                    post_to_discord(article)
                    save_last_article(article_id)
                    last_article = article_id
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
