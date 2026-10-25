import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1483156092597960927/VmGU-WdHbvz2KuvB3J2fmTlph5_vAGEXzZ6tPWZpiGgKEVBsQYMNWzgNOnKguD5b4TF9"

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
            response = requests.get(api_url).json()
            articles = response.get('items', [])

            if not articles:
                print(f"No news found for {source['name']}.")
                continue

            # Grab the newest article
            news = articles[0]
            
            # Pulling the image from the RSS feed data
            img_url = news.get('thumbnail', '')
            if not img_url and isinstance(news.get('enclosure'), dict):
                img_url = news['enclosure'].get('link', '')

            payload = {
                "username": "KnowBetter",
                "embeds": [{
                    "title": news['title'],
                    "description": news['description'][:500] + "..." if news.get('description') else "Click the link to read more.",
                    "url": news['link'],
                    "color": source['color'],
                    "image": {"url": img_url} if img_url else {},
                    "footer": {"text": f"{source['name']} | {news['pubDate']}"}
                }]
            }

            requests.post(WEBHOOK_URL, json=payload)
            print(f"{source['name']} sent!")
            
        except Exception as e:
            print(f"Error with {source['name']}: {e}")

if __name__ == "__main__":
    post_to_discord()
