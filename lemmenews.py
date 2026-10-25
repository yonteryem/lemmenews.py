import os
import requests
import xml.etree.ElementTree as ET

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

NEWS_SOURCES = [
    {
        "name": "Fox News",
        "url": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "color": 15548997
    },
    {
        "name": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "color": 11802914
    }
]

def get_image_url(item):
    namespaces = ["", "{http://search.yahoo.com/mrss/}"]
    for ns in namespaces:
        media = item.find(f"{ns}content") or item.find(f"{ns}thumbnail")
        if media is not None and media.get("url"):
            return media.get("url")
        
        group = item.find(f"{ns}group")
        if group is not None:
            content = group.find(f"{ns}content") or group.find(f"{ns}thumbnail")
            if content is not None and content.get("url"):
                return content.get("url")
    return ""

def post_to_discord():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK secret is missing.")
        return

    for source in NEWS_SOURCES:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(source['url'], headers=headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            item = root.find(".//item")
            
            if item is None:
                continue
                
            title = item.findtext("title", "No Title")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")
            img_url = get_image_url(item)

            payload = {
                "username": "LemmeNews",
                "embeds": [{
                    "title": title[:256],
                    "description": description[:500] + "..." if description else "Click to read more.",
                    "url": link,
                    "color": source['color'],
                    "image": {"url": img_url} if img_url else {},
                    "footer": {"text": f"{source['name']} | {pub_date}"}
                }]
            }

            res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            res.raise_for_status()
            
        except Exception as e:
            print(f"Error with {source['name']}: {e}")

if __name__ == "__main__":
    post_to_discord()
