import requests

# Hardcoded directly so it works instantly
WEBHOOK_URL = "https://discord.com/api/webhooks/1563997924235415565/Lw_eZwv_JNMhfhEfIyeltIr64OLuI0mpvzjYQRNIMqC4cKoKbeCJNrVMqKrmq83duOMH"

NEWS_SOURCES = [
    {
        "name": "Fox News",
        "rss_url": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "color": 15548997
    },
    {
        "name": "BBC News",
        "rss_url": "https://feeds.bbci.co.uk/news/rss.xml",
        "color": 11802914
    }
]

def post_to_discord():
    for source in NEWS_SOURCES:
        try:
            api_url = f"https://api.rss2json.com/v1/api.json?rss_url={source['rss_url']}"
            response = requests.get(api_url, timeout=10).json()
            articles = response.get('items', [])

            if not articles:
                print(f"No articles found for {source['name']}")
                continue

            news = articles[0]
            img_url = news.get('thumbnail', '')
            if not img_url and isinstance(news.get('enclosure'), dict):
                img_url = news['enclosure'].get('link', '')

            payload = {
                "username": "LemmeNews",
                "embeds": [{
                    "title": news.get('title', 'No Title'),
                    "description": (news.get('description', '')[:500] + "...") if news.get('description') else "Click to read more.",
                    "url": news.get('link', ''),
                    "color": source['color'],
                    "image": {"url": img_url} if img_url else {},
                    "footer": {"text": f"{source['name']} | {news.get('pubDate', '')}"}
                }]
            }

            res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            res.raise_for_status()
            print(f"Sent {source['name']} successfully.")
            
        except Exception as e:
            print(f"Error with {source['name']}: {e}")

if __name__ == "__main__":
    post_to_discord()
